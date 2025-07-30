import warnings
from datetime import datetime
from typing import Any, Dict, List, Optional, Self, Type, cast

import micro_language
from nqs_pycore import TokenMetadata

from nqs_sdk.agent.abc_agent import ABCAgent
from nqs_sdk.agent.basic_agent import BasicAgent
from nqs_sdk.environment.blockchain_env import BlockchainEnv
from nqs_sdk.generator import ABCSoloGenerator
from nqs_sdk.miner import Broker
from nqs_sdk.observer import ABCObserver
from nqs_sdk.protocol.abc_protocol import ABCProtocol
from nqs_sdk.protocol.amm.uniswapv3.uniswap_v3 import UniswapV3
from nqs_sdk.protocol.lending_protocol.compoundv2.compoundv2 import Comptroller
from nqs_sdk.run_configuration.parameters import CommonParameters
from nqs_sdk.shared_kernel import MessageDispatcher
from nqs_sdk.spot.spot_oracle import SpotOracle
from nqs_sdk.state import StateCERC20
from nqs_sdk.transaction import ABCTransaction


class EnvironmentBuilder:
    def __init__(self) -> None:
        self.block_start: int
        self.block_end: int
        self.block_grid: list[int]
        self.parameters_micro_language_start_date: Optional[datetime] = None
        self.common_params: Optional[CommonParameters] = None
        self.broker: Optional[Broker] = None
        self.generators: Dict[str, ABCSoloGenerator] = {}
        self.protocols: Dict[str, ABCProtocol] = {}
        self.observers: Dict[str, ABCObserver] = {}
        self.spot_oracle: Optional[SpotOracle] = None
        self.agents: Dict[str, ABCAgent] = {}
        self.transaction_lists: Dict[str, List[ABCTransaction]] = {}
        self.micro_language_interpreter: Optional[Any] = None
        self.mapping_block_number_timestamp: Optional[Dict[int, int]] = None
        self.params_microlanguage: Optional[Any] = None
        self.tokens: List[TokenMetadata | StateCERC20] = []
        self.message_dispatcher: MessageDispatcher

    def set_block_start(self, value: int) -> Self:
        self.block_start = value
        return self

    def set_block_end(self, value: int) -> Self:
        self.block_end = value
        return self

    def set_block_grid(self, value: list[int]) -> Self:
        self.block_grid = value
        return self

    def set_message_dispatcher(self, message_dispatcher: MessageDispatcher) -> Self:
        self.message_dispatcher = message_dispatcher
        return self

    def set_common_params(self, common_params: CommonParameters) -> Self:
        self.common_params = common_params
        return self

    def set_broker(self, broker: Broker) -> Self:
        self.broker = broker
        return self

    def add_generator(self, name: str, generator: ABCSoloGenerator) -> Self:
        self.generators[name] = generator
        return self

    def set_parameters_micro_language_start_date(self, parameters_micro_language_start_date: datetime) -> Self:
        self.parameters_micro_language_start_date = parameters_micro_language_start_date
        return self

    def add_protocol(self, name: str, protocol: ABCProtocol) -> Self:
        self.protocols[name] = protocol
        return self

    def add_observer(self, name: str, observer: ABCObserver) -> Self:
        self.observers[name] = observer
        return self

    def add_oracle(self, oracle: SpotOracle) -> Self:
        self.spot_oracle = oracle
        return self

    def add_agent(self, name: str, agent: ABCAgent) -> Self:
        self.agents[name] = agent
        return self

    def add_transaction_list(self, protocol_name: str, transactions: List[ABCTransaction]) -> Self:
        self.transaction_lists[protocol_name] = transactions
        return self

    def add_token(self, token: TokenMetadata) -> Self:
        self.tokens.append(token)
        return self

    def add_tokens(self, tokens: List[TokenMetadata | StateCERC20]) -> Self:
        self.tokens += tokens
        return self

    def add_micro_language_interpreter(self, language: Any) -> Self:
        self.micro_language_interpreter = language
        return self

    def set_mapping_block_number_timestamp(self, mapping_block_number_timestamp: dict[int, int]) -> Self:
        self.mapping_block_number_timestamp = mapping_block_number_timestamp
        return self

    def _verify(self) -> None:
        self._verify_basic_parameters()
        self._verify_components()
        self._verify_specialized_components()

    def _verify_basic_parameters(self) -> None:
        self._check_is_set("block_start", "Block start")
        self._check_is_set("block_end", "Block end")
        self._check_is_set("block_grid", "Block grid")
        self._check_is_not_none(self.message_dispatcher, "Message dispatcher")
        self._check_is_not_none(self.common_params, "Output parameters")
        self._check_is_not_none(self.parameters_micro_language_start_date, "date micro_language")

    def _verify_components(self) -> None:
        self._check_is_not_none_and_instance(self.broker, Broker, "Broker")
        self._check_is_not_empty(self.generators, "Generators")
        self._check_is_not_empty(self.protocols, "Protocols")
        self._check_is_not_empty(self.observers, "Observers")

    def _verify_specialized_components(self) -> None:
        self._check_is_not_none(self.micro_language_interpreter, "Micro language interpreter")
        self._check_is_not_none(self.mapping_block_number_timestamp, "Mapping block number")
        self._check_is_not_empty(self.mapping_block_number_timestamp, "Mapping block number")

    def _check_is_set(self, value: str, name: str) -> None:
        if not hasattr(self, value):
            raise ValueError(f"{name} not set")

    def _check_is_not_none(self, value: Any, name: str) -> None:
        if value is None:
            raise ValueError(f"{name} not set")

    def _check_is_not_empty(self, value: Any, name: str) -> None:
        if not value:
            raise ValueError(f"{name} not set")

    def _check_is_not_none_and_instance(self, value: Any, cls: Type[Any], name: str) -> None:
        if value is None or not isinstance(value, cls):
            raise ValueError(f"{name} should be defined and valid")

    def _set_environment(self) -> None:
        for id, agent in self.agents.items():
            agent.set_environment(
                self.tokens,
                self.protocols,
                self.message_dispatcher,
                self.params_microlanguage,
                self.common_params,
            )
        broker = cast(Broker, self.broker)
        broker.set_environment(
            self.block_end,
            self.block_grid,
            self.agents,
            self.protocols,
            self.observers,
            self.spot_oracle,
            self.params_microlanguage,
            cast(Dict[int, int], self.mapping_block_number_timestamp),
        )
        for id, protocol in self.protocols.items():
            protocol.set_environment(id)
        for id, generator in self.generators.items():
            generator.set_environment(
                env_protocol_id=id, env_message_dispatcher=self.message_dispatcher, env_observer=self.observers[id]
            )
        for id, observer in self.observers.items():
            observer.set_oracle(self.spot_oracle)
            observer.set_environment(id, self.observers)

    def _setup_micro_language(self) -> None:
        params = micro_language.Parameters(self.parameters_micro_language_start_date)
        spot_oracle = self.spot_oracle
        if spot_oracle is None:
            tokens_oracle = set()
        else:
            tokens_oracle = spot_oracle.tokens
        tokens_to_add = list(tokens_oracle.union([token.symbol for token in self.tokens]))
        params.add_common(tokens=tokens_to_add)
        params.add_agents(list(self.agents.keys()))
        for name, agent in self.agents.items():
            if isinstance(agent, BasicAgent):
                params.add_agent_variables(name, list(agent.custom_variables.keys()))
        for protocol_id, protocol in self.protocols.items():
            match protocol:
                case UniswapV3():
                    params.add_uniswap_v3_protocol(protocol_id, protocol.symbol0, protocol.symbol1)
                case Comptroller():
                    params.add_compound_v2_protocol([(token, None) for token in protocol.underlying_tokens])
                case _:
                    warnings.warn(f"Protocol {protocol_id} not supported")
        self.params_microlanguage = params.seal()

    def build(self) -> BlockchainEnv:
        self._verify()
        self._setup_micro_language()
        self._set_environment()

        return BlockchainEnv(
            block_start=self.block_start,
            block_end=self.block_end,
            message_dispatcher=self.message_dispatcher,
            common_params=cast(CommonParameters, self.common_params),
            broker=cast(Broker, self.broker),
            generators=self.generators,
            protocols=self.protocols,
            observers=self.observers,
            agents=self.agents,
            transaction_lists=self.transaction_lists,
            micro_language_interpreter=cast(micro_language, self.micro_language_interpreter),
            mapping_block_number_timestamp=cast(Dict[int, int], self.mapping_block_number_timestamp),
            params_microlanguage=self.params_microlanguage,
            block_grids=self.block_grid,
        )
