import copy
import logging
from datetime import datetime, timezone
from typing import Literal, Optional, Union

import micro_language
from nqs_pycore import TokenMetadata

from nqs_sdk.agent import ABCAgent, Arbitrageur, BasicAgent
from nqs_sdk.environment import BlockchainEnv, EnvironmentBuilder
from nqs_sdk.environment.helpers import mapping_type_to_state_helper
from nqs_sdk.generator import ABCSoloGenerator, DTQERC20Generator
from nqs_sdk.generator.historical.abc_web3 import Web3SoloGenerator
from nqs_sdk.generator.random.random_generator import RandomGenerator
from nqs_sdk.mappings import (
    ProtocolTypes,
    mapping_type_to_generator,
    mapping_type_to_observer,
    mapping_type_to_protocol,
)
from nqs_sdk.miner import Broker
from nqs_sdk.observer import SPOT_OBSERVER_ID, ABCObserver
from nqs_sdk.observer.agent import AgentObserver
from nqs_sdk.observer.protocol.compoundv2 import ComptrollerObserver
from nqs_sdk.observer.spot import SpotObserver
from nqs_sdk.protocol import LENDING_PROTOCOL_MANDATORY_TOKEN, ABCProtocol
from nqs_sdk.run_configuration.mapping_pool_objects import mapping_address_protocol, mapping_protocols_objects
from nqs_sdk.run_configuration.parameters import Parameters
from nqs_sdk.run_configuration.utils import DEFAULT_TOKEN_DECIMALS, CTokenInfo, ScaledTokenInfo
from nqs_sdk.shared_kernel import DefaultMessageDispatcher, MessageDispatcher
from nqs_sdk.spot import (
    CustomProcess,
    DeterministicSpotProcessArray,
    HistoricalProcess,
    StochasticProcess,
    StochasticSpotProcessArray,
)
from nqs_sdk.spot.mapping_spot_objects import mapping_spot_objects
from nqs_sdk.spot.spot_oracle import SpotOracle
from nqs_sdk.state import StateCERC20
from nqs_sdk.token_utils import wrap_token
from nqs_sdk.utils import generate_grid
from nqs_sdk.wallet.arbitrageur_wallet import Arbitrageur_NAME


class BlockchainEnvSetter:
    """
    Class that generates the environment, given the parameters.
    """

    def __init__(
        self,
        parameters: Parameters,
        random_generator: RandomGenerator = RandomGenerator(),
    ):
        self._validate(parameters.execution_mode)
        self.execution_mode = parameters.execution_mode
        self.parameters = parameters
        self.common_parameters = self.parameters.common_parameters
        self.backtest_params = self.parameters.backtest_parameters if self.execution_mode == "backtest" else None
        self.simulation_params = self.parameters.simulation_parameters if self.execution_mode == "simulation" else None
        self.spot_parameters = self.parameters.spot_parameters

        # simulation ranges (both blocks and timestamps)
        self.block_number_start = self.common_parameters.block_number_start
        self.block_number_end = self.common_parameters.block_number_end
        self.timestamp_start = self.common_parameters.timestamp_start
        self.timestamp_end = self.common_parameters.timestamp_end
        self.block_grid = generate_grid(
            self.block_number_start, self.block_number_end + 1, self.common_parameters.block_step_metrics
        )

        self.token_metadata: list[TokenMetadata | StateCERC20] = []
        self._message_dispatcher: MessageDispatcher = DefaultMessageDispatcher(self.block_grid)
        self.numeraire = self.parameters.common_parameters.numeraire

        self.protocol_generators: dict[str, ABCSoloGenerator] = {}
        self.protocols: dict[str, ABCProtocol] = {}
        self.protocol_observers: dict[str, ABCObserver] = {}
        self.agents: dict[str, ABCAgent] = {}
        self.agent_observers: dict[str, ABCObserver] = {}
        self.spot_oracle: Optional[SpotOracle] = None
        self.oracle_observers: dict[str, ABCObserver] = {}

        self.random_generator = copy.deepcopy(random_generator)

    def _validate(self, execution_mode: Literal["backtest", "simulation"]) -> None:
        if execution_mode not in ["backtest", "simulation"]:
            raise ValueError(f"Execution mode must be either 'backtest' or 'simulation', not {execution_mode}.")

    def generate_protocol_generators(self) -> None:
        self.generate_protocol_generators_backtest()
        self.generate_protocol_generators_simulation()

    def generate_protocol_generators_backtest(self) -> None:
        if self.backtest_params is None:
            return
        for protocol_name, protocol_info_backtested in self.backtest_params.protocols_to_replay.items():
            params_generator = {
                "id": protocol_info_backtested.id,
                "name": protocol_name,
                "protocol_info": protocol_info_backtested.protocol_info,
            }
            # create generator
            generator_class = mapping_protocols_objects[protocol_info_backtested.protocol_type]["generator"]
            # XXX legacy code to be removed
            if issubclass(generator_class, Web3SoloGenerator):
                params_generator.update({"mapping_address_protocol": mapping_address_protocol})
            this_generator = generator_class(**params_generator)
            self.protocol_generators[protocol_name] = this_generator

    def generate_protocol_generators_simulation(self) -> None:
        if self.simulation_params is None:
            return
        for protocol_name, protocol_info_simulated in self.simulation_params.protocols_to_simulate.items():
            # pass a copy of the random generator so that each protocol generator has its own random generator
            random_generator = copy.deepcopy(self.random_generator)
            random_generation_params = protocol_info_simulated.random_generation_params
            generator_type = mapping_type_to_generator.get(protocol_info_simulated.protocol_type)
            if protocol_info_simulated.protocol_type in [ProtocolTypes.COMPOUND_V2.value]:
                for market_name, market_params in random_generation_params.items():
                    if generator_type is not None:
                        self.protocol_generators[protocol_name + "_" + market_name] = generator_type(
                            id=protocol_info_simulated.id,
                            name=market_name,
                            type=protocol_info_simulated.protocol_type,
                            random_generation_parameters=market_params,
                            random_generator=random_generator,
                            additional_params=protocol_info_simulated.additional_parameters[market_name],
                            mapping_block_timestamps=self.common_parameters.mapping_block_number_timestamp,
                        )
            else:
                if generator_type is not None:
                    this_generator = generator_type(
                        id=protocol_info_simulated.id,
                        name=protocol_name,
                        type=protocol_info_simulated.protocol_type,
                        random_generation_parameters=random_generation_params,
                        random_generator=random_generator,
                        mapping_block_timestamps=self.common_parameters.mapping_block_number_timestamp,
                    )
                    self.protocol_generators[protocol_name] = this_generator
                else:
                    raise ValueError(f"Protocol : {protocol_info_simulated.protocol_type} not implemented")

    def generate_protocols(self) -> None:
        if len(self.protocol_generators) == 0:
            raise ValueError("Protocol generators must be generated before protocols.")

        # convert gas fees from float to integer
        gas_fee: int = 0
        if self.common_parameters.gas_fee > 0:
            gas_fee_decimals = [
                metadata.decimals
                for metadata in self.token_metadata
                if metadata.symbol == self.common_parameters.gas_fee_ccy
            ][0]
            gas_fee = int(self.common_parameters.gas_fee * 10**gas_fee_decimals)

        if self.backtest_params is not None:
            for protocol_name, protocol_info_backtested in self.backtest_params.protocols_to_replay.items():
                state_init = self.protocol_generators[protocol_name].generate_state_at_block(self.block_number_start)
                # create protocol
                this_protocol = mapping_protocols_objects[protocol_info_backtested.protocol_type]["protocol"](
                    state=state_init,
                    gas_fee=gas_fee,
                    gas_fee_ccy=self.common_parameters.gas_fee_ccy,
                )
                self.protocols[protocol_name] = this_protocol

        elif self.simulation_params is not None:
            for protocol_name, protocol_info_simulated in self.simulation_params.protocols_to_simulate.items():
                initial_state = protocol_info_simulated.initial_state
                # TODO: there is no standard type for initial state
                if (
                    protocol_info_simulated.protocol_type in [ProtocolTypes.COMPOUND_V2.value]
                    and self.spot_oracle is not None
                    and LENDING_PROTOCOL_MANDATORY_TOKEN not in self.spot_oracle.tokens
                ):
                    # the spot oracle is not generated before the protocols (because of Uniswap spot requirements)
                    # hence we cannot add USDC on the fly here - we have to raise an error
                    raise ValueError(
                        """Lending protocols require USDC to be part of a simulated token pair.
                        Please add it to the list of simulated tokens or in the mandatory_token field."""
                    )
                else:
                    if mapping_type_to_protocol.get(protocol_info_simulated.protocol_type) is not None:
                        correct_state = mapping_type_to_state_helper[protocol_info_simulated.protocol_type](
                            initial_state, self.spot_oracle
                        )
                        this_protocol = mapping_type_to_protocol[protocol_info_simulated.protocol_type](
                            state=correct_state,
                            gas_fee=gas_fee,
                            gas_fee_ccy=self.common_parameters.gas_fee_ccy,
                        )
                    else:
                        raise ValueError(f"Protocol : {protocol_info_simulated.protocol_type} not implemented")
                    self.protocols[protocol_name] = this_protocol

    def generate_protocol_observers(self) -> None:
        if len(self.protocols) == 0:
            raise ValueError("Protocols must be generated before protocol observers.")
        if self.backtest_params is not None:
            self.generate_protocol_observers_backtest()
        elif self.simulation_params is not None:
            self.generate_protocol_observers_simulation()

    def generate_protocol_observers_backtest(self) -> None:
        for protocol_name, protocol_info_backtested in self.backtest_params.protocols_to_replay.items():  # type: ignore
            # create protocol observer
            if protocol_info_backtested.protocol_type == ProtocolTypes.COMPOUND_V2.value:
                this_protocol_observer = mapping_protocols_objects[protocol_info_backtested.protocol_type]["observer"](
                    comptroller=self.protocols[protocol_name]
                )
                self.protocol_observers[protocol_name] = this_protocol_observer
                for ctoken, market_obs in this_protocol_observer.markets_observables.items():
                    self.protocol_observers[protocol_name + "_" + ctoken] = market_obs
            else:
                this_protocol_observer = mapping_protocols_objects[protocol_info_backtested.protocol_type]["observer"](
                    protocol=self.protocols[protocol_name]
                )
                self.protocol_observers[protocol_name] = this_protocol_observer

    def generate_protocol_observers_simulation(self) -> None:
        for protocol_name, protocol_info_simulated in self.simulation_params.protocols_to_simulate.items():  # type: ignore
            protocol = self.protocols[protocol_name]
            protocol_type = protocol_info_simulated.protocol_type
            if protocol_type == ProtocolTypes.COMPOUND_V2.value:
                compound_v2_obs = mapping_type_to_observer[protocol_type](protocol)
                if not isinstance(compound_v2_obs, ComptrollerObserver):
                    raise ValueError("CompoundV2 observer must be of type ComptrollerObserver")  # for mypy
                self.protocol_observers[protocol_name] = compound_v2_obs
                for ctoken, market_obs in compound_v2_obs.markets_observables.items():
                    self.protocol_observers[protocol_name + "_" + market_obs.underlying] = market_obs
            else:
                if mapping_type_to_observer.get(protocol_type) is not None:
                    this_protocol_observer = mapping_type_to_observer[protocol_type](protocol)
                    self.protocol_observers[protocol_name] = this_protocol_observer
                else:
                    raise ValueError(f"Protocol : {protocol_info_simulated.protocol_type} not implemented")

    def generate_token_metadata(self) -> None:
        if self.backtest_params is not None:
            token_mapping = self.backtest_params.token_mapping
            this_generator_tokens = DTQERC20Generator(
                id=-1,
                name="ERC20",
                token_mapping=token_mapping,
            )
            # this fills tokens addresses, decimals and names
            erc20_token_metadata = this_generator_tokens.generate_token_metadata()
            self.token_metadata += erc20_token_metadata

            # do the same for ctokens
            if "compound_v2" in self.protocol_generators.keys():
                self.token_metadata += self.protocol_generators["compound_v2"].generate_ctoken_metadata()  # type: ignore
            for contract_name, contract_info in self.backtest_params.protocols_to_replay.items():
                match contract_info.protocol_type:
                    case ProtocolTypes.COMPOUND_V2.value:
                        self.token_metadata += self.protocol_generators["compound_v2"].generate_ctoken_metadata()  # type: ignore

        elif self.simulation_params is not None:
            self.token_metadata = [
                TokenMetadata(
                    name=token_info.name,
                    symbol=symbol,
                    decimals=token_info.decimals,
                )
                for (symbol, token_info) in self.simulation_params.token_info_dict.items()
                if (not isinstance(token_info, CTokenInfo) or not isinstance(token_info, ScaledTokenInfo))
            ]

            self.token_metadata += [
                StateCERC20(
                    name=token_info.name,
                    symbol=symbol,
                    decimals=token_info.decimals,
                    # address=token_info.address,
                    underlying_symbol=token_info.underlying_symbol,
                    underlying_address=token_info.underlying_address,
                    block_number=self.block_number_start,
                    block_timestamp=0,
                    total_supply=None,
                    comptroller_id=token_info.comptroller_id,
                )
                for (symbol, token_info) in self.simulation_params.token_info_dict.items()
                if isinstance(token_info, CTokenInfo)
            ]

        # fill in with default information any token that has not been used in a protocol or provided with
        # information by the user in the params
        self.token_metadata += [
            TokenMetadata(
                name=wrap_token(symbol) + "coin",
                symbol=wrap_token(symbol),
                decimals=DEFAULT_TOKEN_DECIMALS,
            )
            for symbol in self.spot_parameters.tokens
            if wrap_token(symbol) not in [token.symbol for token in self.token_metadata]
        ]

        # set the decimals information about the tokens in the spot_oracle. Useful to know the decimals of the
        # numéraire for example
        if self.spot_oracle is not None:
            self.spot_oracle.set_token_decimals({state.symbol: state.decimals for state in self.token_metadata})

    def generate_agents(self) -> None:
        for name in self.parameters.agents_parameters:
            self.agents[name] = BasicAgent(
                name=name,
                agent_config=self.parameters.agents_parameters[name],
                tokens_metadata=self.token_metadata,
            )
        if self.common_parameters.use_arbitrageur:
            self.agents[Arbitrageur_NAME] = Arbitrageur(
                tokens_metadata=self.token_metadata,
                arbitrage_block_frequency=self.common_parameters.arbitrage_block_frequency,
            )

    def generate_agent_observers(self) -> None:
        for name in self.agents:
            self.agent_observers[name] = AgentObserver(agent=self.agents[name])

    def generate_oracle_observer(self) -> None:
        self.oracle_observers[SPOT_OBSERVER_ID] = SpotObserver()

    def generate_spot_oracle(self) -> None:
        stoc_spots: list[StochasticProcess] = []
        deterministic_spots: list[Union[HistoricalProcess, CustomProcess]] = []

        for pair, params in self.spot_parameters.stochastic_param.items():
            process_type = list(params.keys())[0]
            if params[process_type] is None:
                params[process_type] = {}
            params[process_type]["current_timestamp"] = self.timestamp_start
            stoc_spots.append(mapping_spot_objects[process_type](pair=pair, **params[process_type]))
        for pair, params in self.spot_parameters.deterministic_params.items():
            process_type = list(params.keys())[0]
            if params[process_type] is None:
                params[process_type] = {}
            params[process_type]["current_timestamp"] = self.timestamp_start
            params[process_type]["end_timestamp"] = self.timestamp_end
            params[process_type]["execution_mode"] = self.execution_mode
            deterministic_spots.append(mapping_spot_objects[process_type](pair=pair, **params[process_type]))

        if stoc_spots or deterministic_spots:
            # pass an independent copy of the random generator
            random_generator = copy.deepcopy(self.random_generator)
            self.spot_oracle = SpotOracle(
                stochastic_spot=StochasticSpotProcessArray(stoc_spots, self.spot_parameters.correlation),
                deterministic_spot=DeterministicSpotProcessArray(deterministic_spots, self.execution_mode),
                end_timestamp=self.timestamp_end,
                numeraire=self.numeraire,
                random_generator=random_generator,
                current_timestamp=self.timestamp_start,
                mandatory_tokens=self.common_parameters.mandatory_tokens,
                execution_mode=self.execution_mode,
            )
            self.spot_oracle.set_timestamps_list(list(self.common_parameters.mapping_block_number_timestamp.values()))

    def generate_components(self) -> None:
        self.generate_protocol_generators()
        self.generate_spot_oracle()
        self.generate_oracle_observer()
        self.generate_token_metadata()
        self.generate_protocols()
        self.generate_protocol_observers()
        self.generate_agents()
        self.generate_agent_observers()

    def generate_environment(self) -> BlockchainEnv:
        # generate components
        self.generate_components()
        logging.info("Simulation components generated")

        builder = EnvironmentBuilder()

        builder.set_block_start(self.block_number_start)
        builder.set_block_end(self.block_number_end)
        builder.set_block_grid(self.block_grid)
        builder.set_message_dispatcher(self._message_dispatcher)
        builder.add_tokens(self.token_metadata)
        builder.add_micro_language_interpreter(micro_language)
        builder.set_common_params(self.common_parameters)
        builder.set_mapping_block_number_timestamp(
            mapping_block_number_timestamp=self.common_parameters.mapping_block_number_timestamp
        )

        for name, protocol in self.protocols.items():
            builder.add_protocol(name, protocol)
        for name, generator in self.protocol_generators.items():
            builder.add_generator(name, generator)
        for name, observer in self.protocol_observers.items():
            builder.add_observer(name, observer)
        for name, agent in self.agents.items():
            builder.add_agent(name, agent)
        for name, agent_observer in self.agent_observers.items():
            builder.add_observer(name, agent_observer)
        if self.spot_oracle is not None:
            builder.add_oracle(self.spot_oracle)
            builder.add_observer(SPOT_OBSERVER_ID, self.oracle_observers[SPOT_OBSERVER_ID])

        builder.set_parameters_micro_language_start_date(datetime.now(timezone.utc))
        this_broker = Broker(self._message_dispatcher)
        builder.set_broker(this_broker)
        this_environment = builder.build()
        logging.info("Simulation environment built")

        return this_environment
