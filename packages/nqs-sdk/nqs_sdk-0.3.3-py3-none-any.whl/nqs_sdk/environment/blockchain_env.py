import logging
import os
from typing import Any, Dict, List

import micro_language

from nqs_sdk.agent import ABCAgent, AgentAction, BasicAgent
from nqs_sdk.constants import SEED_SHIFT
from nqs_sdk.environment import ABCEnvironment
from nqs_sdk.generator import ABCSoloGenerator
from nqs_sdk.miner import Broker
from nqs_sdk.observer import SPOT_OBSERVER_ID, ABCObserver
from nqs_sdk.protocol import ABCProtocol
from nqs_sdk.run_configuration.parameters import CommonParameters
from nqs_sdk.shared_kernel import MessageDispatcher, ObserveCall
from nqs_sdk.transaction import ABCTransaction
from nqs_sdk.utils import load_log_file, parse_tx_log, sample_outputs


class BlockchainEnv(ABCEnvironment):
    def __init__(
        self,
        block_start: int,
        block_end: int,
        block_grids: List[int],
        message_dispatcher: MessageDispatcher,
        common_params: CommonParameters,
        broker: Broker,
        generators: Dict[str, ABCSoloGenerator],
        protocols: Dict[str, ABCProtocol],
        observers: Dict[str, ABCObserver],
        agents: Dict[str, ABCAgent],
        transaction_lists: Dict[str, List[ABCTransaction]],
        micro_language_interpreter: micro_language,
        mapping_block_number_timestamp: Dict[int, int],
        params_microlanguage: Any,
    ) -> None:
        self._block_start = block_start
        self._block_end = block_end
        self._block_grids = block_grids
        self._message_dispatcher = message_dispatcher
        self._common_parameters = common_params
        self._broker = broker
        self._generators = generators
        self._protocols = protocols
        self._observers = observers
        self._transactions_protocols = transaction_lists
        self._micro_language_interpreter = micro_language_interpreter
        self._mapping_block_number_timestamp = mapping_block_number_timestamp
        self._params_microlanguage = params_microlanguage
        self._agents = agents

    def __str__(self) -> str:
        message_to_print = "# PREPARING ENVIRONMENT #"
        formatted_heading = [
            "\n",
            "#" * len(message_to_print),
            message_to_print,
            "#" * len(message_to_print),
        ]
        return "\n".join(formatted_heading)

    @property
    def block_timestamp_start(self) -> int:
        """
        returns the min timestamp from the mapping block number -> timestamp, so the starting timestamp of the sim
        """
        return list(self._mapping_block_number_timestamp.values())[0]

    @property
    def block_timestamp_max(self) -> int:
        """
        returns the max timestamp from the mapping block number -> timestamp
        """
        return list(self._mapping_block_number_timestamp.values())[-1]

    @property
    def block_start(self) -> int:
        return self._block_start

    @property
    def block_end(self) -> int:
        return self._block_end

    def _initialize_observers(self) -> None:
        """
        Initialize all observers
        """
        for observer in self._observers.values():
            observer.collect_observables(self._block_start, block_timestamp=self.block_timestamp_start)

    def _start_simulation(self) -> None:
        self._message_dispatcher.start_pulling(self._block_start, self._block_end, "TRANSACTIONS")

    def _instantiate_random_generators(self, seed: int, use_antithetic_variates: bool) -> None:
        # instantiate random generators of protocol generators
        for i, protocol_id in enumerate(self._generators.keys()):
            self._generators[protocol_id].set_seed(seed + i * SEED_SHIFT, use_antithetic_variates)

        # instantiate random generators of spot oracle
        self._observers[SPOT_OBSERVER_ID].spot_oracle.set_seed(seed, use_antithetic_variates)

    def run_environment(self, seed: int, use_antithetic_variates: bool = True) -> None:
        logging.info(f"Running environment with seed {seed}")
        self._instantiate_random_generators(seed=seed, use_antithetic_variates=use_antithetic_variates)
        self._message_dispatcher.register_listener(ABCTransaction, self._broker, "TRANSACTIONS")
        self._message_dispatcher.register_listener(AgentAction, self._broker, "TRANSACTIONS")
        self._message_dispatcher.register_listener(ObserveCall, self._broker, "TRANSACTIONS")
        self._message_dispatcher.start(low_watermark=self._block_start)
        self._initialize_observers()
        self._evaluate_agents_custom_variables(self.block_timestamp_start, self.block_start)
        self._start_simulation()
        logging.info(f"Simulation over for seed {seed}")

    def _evaluate_agents_custom_variables(self, block_timestamp: int, block_number: int) -> None:
        for agent in self._agents.values():
            if not isinstance(agent, BasicAgent):
                continue
            self._broker.evaluate_agent_custom_variables(agent, block_timestamp, block_number)

    def get_simulation_outputs(self, obs_to_aggregate_only: bool = True, log_file_path: str = "") -> dict:
        all_obs: dict = {}
        for protocol_id in self._observers.keys():
            all_obs.update(self._observers[protocol_id].get_all_metrics())
        self.enrich_obs_with_tx_logs(all_obs, log_file_path)
        timestamps_grid = [self._mapping_block_number_timestamp[x] for x in self._block_grids]
        sampled_observables = sample_outputs(all_obs, timestamps_grid)
        if obs_to_aggregate_only:
            sampled_observables = {key: value for key, value in sampled_observables.items() if "position=" not in key}
        return sampled_observables

    def enrich_obs_with_tx_logs(self, all_obs: dict, log_file_path: str) -> None:
        if not os.path.exists(log_file_path):
            return
        for agent_name, agent in self._agents.items():
            if not isinstance(agent, BasicAgent):
                continue
            txs = load_log_file(log_file_path, agent_name=agent_name, key="Transaction")
            txs_dict: dict[str, list] = {}
            for tx in txs:
                timestamp, tx_info = parse_tx_log(tx)
                txs_dict.setdefault(timestamp, [])
                txs_dict[timestamp].append(tx_info)
            all_obs["events_log_" + agent_name] = {
                "block_timestamps": [int(el) for el in txs_dict.keys()],
                "values": list(txs_dict.values()),
            }

    def compare_protocol_final_state(self, protocol_id: str) -> None:
        if protocol_id == "cex":
            logging.info(f"\nNo comparison possible for protocol {protocol_id}")
            return
        logging.info(f"\nComparing protocol {protocol_id} final state")
        this_protocol = self._protocols[protocol_id]
        state_final = self._generators[protocol_id].generate_state_at_block(self._block_end)
        state_final_protocol = this_protocol.get_state(self._block_end)
        self._generators[protocol_id].compare_two_states(state_final, state_final_protocol)


def is_abc_agent(agent: ABCAgent) -> bool:
    return isinstance(agent, ABCAgent)
