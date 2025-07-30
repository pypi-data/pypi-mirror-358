import datetime
import logging
from typing import Any, Optional, cast

from micro_language import EmptyTimeseriesError, Expression

from nqs_sdk.agent import ABCAgent, AgentAction, Arbitrageur, BasicAgent
from nqs_sdk.agent.agent_action import CustomVariable
from nqs_sdk.agent.transaction_helper import TransactionHelper
from nqs_sdk.miner.utils import deduplicate_time_series
from nqs_sdk.observer import SPOT_OBSERVER_ID, ABCObserver, AgentObserver, ProtocolObserver, SpotObserver
from nqs_sdk.observer.utils import parse_metric_name
from nqs_sdk.protocol import ABCProtocol
from nqs_sdk.shared_kernel import MessageDispatcher, MessageListener, ObserveCall
from nqs_sdk.spot.spot_oracle import SpotOracle
from nqs_sdk.transaction import ABCTransaction
from nqs_sdk.wallet.arbitrageur_wallet import Arbitrageur_NAME


class Broker(MessageListener[ABCTransaction | AgentAction | ObserveCall]):
    def __init__(self, message_dispatcher: MessageDispatcher) -> None:
        self._last_block_observables: int = -1
        self._block_grid: list[int] = []
        self._block_step: int = 0
        self._final_block_number: Optional[int] = None
        self._agents: dict[str, ABCAgent] = {}
        self._transactions_agent: list[AgentAction] = []
        self._protocols: dict[str, ABCProtocol] = {}
        self._transactions_protocols: list[ABCTransaction] = []
        self._observers: dict[str, ABCObserver] = {}
        self._spot_oracle: Optional[SpotOracle] = None
        self._message_dispatcher = message_dispatcher
        self._params_microlanguage: Optional[Any] = None
        self._mappings_block_number_timestamp: dict[int, int] = {}
        self._arbitrageur: Optional[Arbitrageur] = None
        self.transaction_helper = TransactionHelper()

    def handle(self, message: ABCTransaction | AgentAction | ObserveCall) -> None:
        block_number = message.time_index()
        block_timestamp = self._mappings_block_number_timestamp.get(block_number, -1)
        if isinstance(message, ABCTransaction):
            self.handle_non_agent_transactions(message, block_number, block_timestamp)
        elif isinstance(message, AgentAction):
            self.handle_agent_transactions(message, block_number, block_timestamp)
        elif isinstance(message, ObserveCall):
            self.refresh_observables(block_number, block_timestamp)
        else:
            raise NotImplementedError(f"No support for transaction {message}")
        if self._message_dispatcher.count_remaining_message_for_time_index(block_number, "TRANSACTIONS") == 0:
            self.handle_arbitrages(block_number, block_timestamp)

    def refresh_observables(self, block_number: int, block_timestamp: int) -> None:
        self._collect_all_observables(block_number, block_timestamp)
        self._last_block_observables = block_number
        self._flush_buffers()

    def check_condition(
        self, condition: Expression, block_number: int, block_timestamp: int, last_update_timestamp: datetime.datetime
    ) -> Any:
        expected_data = condition.expected_data(self._params_microlanguage)
        self._fill_expected_data(expected_data, block_timestamp, block_number)
        try:
            condition_is_true = condition.eval(
                self._params_microlanguage,
                expected_data,
                last_update_timestamp,
                datetime.datetime.now(datetime.timezone.utc),
            )
            return condition_is_true
        except EmptyTimeseriesError as e:
            logging.warning(f"{e} \n Following condition will be False by default: {condition}")
            return False

    def handle_spot(self, transaction: ABCTransaction, protocol_id: str) -> None:
        required_spots = self._protocols[protocol_id].spots_to_inject(transaction)
        if required_spots and self._spot_oracle is not None:
            self._protocols[protocol_id].inject_spot_values(
                transaction.block_timestamp,
                self._spot_oracle.get_selected_spots(required_spots, transaction.block_timestamp),
            )

    def handle_agent_transactions(self, agent_action: AgentAction, block_number: int, block_timestamp: int) -> None:
        logger_key = "AgentAction"
        agent_name = str(agent_action.agent_name)
        condition = agent_action.condition
        condition_str = agent_action.condition_str
        transactions = agent_action.transactions
        protocol_id = str(agent_action.protocol_id)
        new_custom_variables = agent_action.custom_variables
        logging.debug(f"Received agent transactions : {list(transactions)}")
        for transaction in transactions:
            transaction.inject_block_timestamp(block_timestamp=block_timestamp)
        assert block_timestamp > 0, f"Received invalid block timestamp: {block_timestamp}"
        # agent actions require the observables to be refreshed before their execution so to use the latest available
        # data on conditions and expressions - note that this should not cause particular issues as agent actions are
        # executed before random/historical transactions, if happening on the same block
        self._collect_all_observables(block_number, block_timestamp)
        if condition is not None:
            condition_is_true = self.check_condition(
                condition, block_number, block_timestamp, agent_action.last_update_timestamp
            )
            if not condition_is_true:
                logging.info(
                    f"Key: {logger_key} - Timestamp: {block_timestamp} - Block number: {block_number} -  "
                    f"Agent: {agent_name} - Condition: {condition_str} - Status: Not triggered - Comment: skipping "
                    f"agent transactions: {transactions}"
                )
                return

        logging.info(
            f"Key: {logger_key} - Timestamp: {block_timestamp} - Block number: {block_number} - Agent: {agent_name} - "
            f"Condition: {condition_str} - Status: Triggered - Comment: proceeding with agent "
            f"transactions: {transactions}"
        )
        for transaction in transactions:
            tmp_transaction = self.evaluate_agent_transaction(
                transaction, block_timestamp, block_number, agent_action.last_update_timestamp
            )
            if tmp_transaction is None:
                continue
            else:
                transaction = tmp_transaction
            self.handle_spot(transaction, protocol_id)

            # charge gas fees - inside this function we are sure that transaction.sender_wallet is not None
            gas_fees_charged = self._protocols[protocol_id].charge_gas_fee(wallet=transaction.sender_wallet)
            if gas_fees_charged:
                self._protocols[protocol_id].process_single_transaction(transaction)
            else:
                if transaction.sender_wallet is not None:
                    balance = transaction.sender_wallet.get_balance_of_float(self._protocols[protocol_id].gas_fee_ccy)
                else:
                    balance = "N/A"

                logging.info(
                    f"Key: {logger_key} - Timestamp: {block_timestamp} - Block number: {block_number} -  "
                    f"Agent: {agent_name} - impossible to charge gas fees because of insufficient balance. "
                    f"{self._protocols[protocol_id].gas_fee_ccy} balance in wallet is {balance} "
                    f"Transaction: {transaction}"
                )
            if agent_name in self._observers:
                self._observers[protocol_id].collect_observables(block_number, block_timestamp)
                self._observers[agent_name].collect_observables(block_number, block_timestamp)
                # update the custom variables of the agent
                new_custom_variables = cast(list[CustomVariable], new_custom_variables)
                self.update_agent_custom_variables(str(agent_name), new_custom_variables, block_timestamp, block_number)
        agent_action.last_update_timestamp = datetime.datetime.now(datetime.timezone.utc)

    def handle_non_agent_transactions(
        self, transaction: ABCTransaction, block_number: int, block_timestamp: int
    ) -> None:
        protocol_id = transaction.protocol_id
        block_number = transaction.block_number
        logging.debug(f"Received transaction : {transaction}")
        block_timestamp = self._mappings_block_number_timestamp.get(block_number, -1)
        transaction.inject_block_timestamp(block_timestamp=block_timestamp)
        assert block_timestamp > 0, f"Received invalid block timestamp: {block_timestamp}"
        self.handle_spot(transaction, protocol_id)
        self._protocols[protocol_id].process_single_transaction(transaction)

    def evaluate_single_custom_variable(
        self, var: CustomVariable, block_timestamp: int, block_number: int
    ) -> CustomVariable:
        if isinstance(var.value, Expression):
            expected_data = var.value.expected_data(self._params_microlanguage)
            self._fill_expected_data(expected_data, block_timestamp, block_number)
            try:
                var.value = var.value.eval(
                    self._params_microlanguage,
                    expected_data,
                    var.last_update_timestamp,
                    datetime.datetime.now(datetime.timezone.utc),
                )
            except EmptyTimeseriesError as e:
                logging.warning(f"{e} \n Following custom variable won't be updated: {var}")
            var.last_update_timestamp = datetime.datetime.now(datetime.timezone.utc)
        return var

    def update_agent_custom_variables(
        self, agent_name: str, new_custom_variables: list[CustomVariable], block_timestamp: int, block_number: int
    ) -> None:
        evaluated_custom_variables = [
            self.evaluate_single_custom_variable(var, block_timestamp, block_number) for var in new_custom_variables
        ]
        self._agents[agent_name].update_custom_variables(evaluated_custom_variables)

    def evaluate_agent_custom_variables(self, agent: BasicAgent, block_timestamp: int, block_number: int) -> None:
        for var in agent.custom_variables.values():
            self.evaluate_single_custom_variable(var, block_timestamp, block_number)

    def evaluate_agent_transaction(
        self,
        transaction: ABCTransaction,
        block_timestamp: int,
        block_number: int,
        last_update_timestamp: datetime.datetime,
    ) -> ABCTransaction | None:
        for key, value in transaction.__dict__.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, Expression):
                        expected_data = sub_value.expected_data(self._params_microlanguage)
                        self._fill_expected_data(expected_data, block_timestamp, block_number)
                        try:
                            transaction.__dict__[key][sub_key] = sub_value.eval(
                                self._params_microlanguage,
                                expected_data,
                                last_update_timestamp,
                                datetime.datetime.now(datetime.timezone.utc),
                            )
                        except EmptyTimeseriesError as e:
                            logging.warning(f"{e} \n Following transaction will be skipped: {transaction}")
                            return None

            if isinstance(value, Expression):
                expected_data = value.expected_data(self._params_microlanguage)
                self._fill_expected_data(expected_data, block_timestamp, block_number)
                try:
                    transaction.__dict__[key] = value.eval(
                        self._params_microlanguage,
                        expected_data,
                        last_update_timestamp,
                        datetime.datetime.now(datetime.timezone.utc),
                    )
                except EmptyTimeseriesError as err0:
                    logging.warning(f"{err0} \n Following transaction will be skipped: {transaction}")
                    return None
        mapped_transaction = self.transaction_helper.map_ux_transaction(ux_transaction=transaction)
        return mapped_transaction

    def handle_arbitrages(self, block_number: int, block_timestamp: int) -> None:
        if (
            self._arbitrageur is None
            or self._arbitrageur.arbitrage_block_frequency is None
            or block_number - self._arbitrageur.last_arbitraged_block < self._arbitrageur.arbitrage_block_frequency
        ):
            return None

        for protocol_id in self._protocols.keys():
            if not isinstance(self._observers[protocol_id], ProtocolObserver) or (
                isinstance(self._observers[protocol_id], ProtocolObserver)
                and not self._observers[protocol_id].exists_arbitrage_opportunity(  # type: ignore
                    block_number, block_timestamp
                )
            ):
                continue

            agents_to_update = self._observers[protocol_id].agents_id_to_update() + [Arbitrageur_NAME]  # type: ignore
            arbitrage_transactions = list(
                self._observers[protocol_id].create_arbitrage_transactions(  # type: ignore
                    block_number, block_timestamp, self._agents[Arbitrageur_NAME].wallet
                )
            )
            for trx in arbitrage_transactions:
                trx.inject_block_timestamp(block_timestamp)
                required_spots = self._protocols[protocol_id].spots_to_inject(trx)
                if required_spots and self._spot_oracle is not None:
                    self._protocols[protocol_id].inject_spot_values(
                        trx.block_timestamp, self._spot_oracle.get_selected_spots(required_spots, trx.block_timestamp)
                    )
                self._protocols[protocol_id].process_single_transaction(trx)
            for agent_id in agents_to_update:
                self._observers[agent_id].collect_observables(
                    block_number=block_number, block_timestamp=block_timestamp
                )

        self._arbitrageur.last_arbitraged_block = block_number

    def set_environment(
        self,
        env_ending_block_number: int,
        env_block_grid: list[int],
        env_agents: dict[str, ABCAgent],
        env_protocols: dict[str, ABCProtocol],
        env_observers: dict[str, ABCObserver],
        spot_oracle: Optional[SpotOracle],
        env_params_microlanguage: Optional[Any],
        mappings_block_number_timestamp: Optional[dict[int, int]] = None,
    ) -> None:
        if mappings_block_number_timestamp is None:
            mappings_block_number_timestamp = {}
        self._final_block_number = env_ending_block_number
        self._block_grid = env_block_grid
        self._block_step = env_block_grid[1] - env_block_grid[0] if len(env_block_grid) > 1 else 0
        self._agents = env_agents
        self._protocols = env_protocols
        env_agent = env_agents.get("basic_agent")
        if env_agent is not None:
            self._transactions_agent = env_agent.get_policy() if len(env_agents) != 0 else []
        else:
            self._transactions_agent = []
        self._arbitrageur = cast(Optional[Arbitrageur], env_agents.get(Arbitrageur_NAME, None))
        self._observers = env_observers
        self._spot_oracle = spot_oracle
        self._params_microlanguage = env_params_microlanguage
        self._mappings_block_number_timestamp = mappings_block_number_timestamp

    def _fill_expected_data(self, expected_data: dict[str, Any], block_timestamp: int, block_number: int) -> None:
        # todo this needs to handle also market_spot
        for key in expected_data.keys():
            metric_name_dict = parse_metric_name(key)
            if metric_name_dict["protocol"] == "variables":
                assert metric_name_dict["agent"] is not None, "Agent must be specified for 'variables' metrics"
                custom_variable = self._observers[metric_name_dict["agent"]].get_custom_variable(
                    metric_name_dict["metric"]
                )
                expected_data[key] = custom_variable.value
                continue
            if metric_name_dict["protocol"] == "common":
                protocol_id = SPOT_OBSERVER_ID
            elif metric_name_dict["protocol"] == "all":
                assert metric_name_dict["agent"] is not None, "Agent must be specified for 'all' metrics"
                protocol_id = metric_name_dict["agent"]
            elif metric_name_dict["agent"] is not None:
                # then it is a metric like agent_1.protocol.metric
                protocol_id = metric_name_dict["agent"]
            else:
                protocol_id = metric_name_dict["protocol"]
            values, timestamps, decimals = self._observers[protocol_id].get_metric_value_timeseries(
                metric_name=key, block_number=block_number, block_timestamp=block_timestamp
            )

            timestamps_unique, values_unique = deduplicate_time_series(timestamps, values)

            expected_data[key] = (
                timestamps_unique,
                values_unique,
                decimals,
            )

    def _collect_all_observables(self, block_number: int, block_timestamp: int) -> None:
        # update spot
        for observer in self._observers.values():
            if isinstance(observer, SpotObserver):
                observer.collect_observables(block_number=block_number, block_timestamp=block_timestamp)
        # update protocol metrics
        for observer in self._observers.values():
            if not isinstance(observer, (AgentObserver, SpotObserver)):
                observer.collect_observables(block_number=block_number, block_timestamp=block_timestamp)
        # update agent metrics
        for observer in self._observers.values():
            if isinstance(observer, AgentObserver):
                observer.collect_observables(block_number=block_number, block_timestamp=block_timestamp)

    def _flush_buffers(self) -> None:
        for observer in self._observers.values():
            observer.flush_buffer()
