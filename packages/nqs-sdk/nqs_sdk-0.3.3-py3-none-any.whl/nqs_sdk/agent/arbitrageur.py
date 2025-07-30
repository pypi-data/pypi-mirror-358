from typing import Any, List, Optional, Tuple

from nqs_pycore import TokenMetadata

from nqs_sdk.agent import ABCAgent, AgentAction
from nqs_sdk.agent.agent_action import CustomVariable
from nqs_sdk.protocol import ABCProtocol
from nqs_sdk.run_configuration.parameters import CommonParameters
from nqs_sdk.shared_kernel import MessageDispatcher, MessageProducer, PickableGenerator, StatefulGenerator
from nqs_sdk.state import StateCERC20
from nqs_sdk.wallet.arbitrageur_wallet import Arbitrageur_NAME, ArbitrageurWallet


class Arbitrageur(ABCAgent, MessageProducer):
    def __init__(
        self,
        tokens_metadata: list[TokenMetadata | StateCERC20],
        arbitrage_block_frequency: Optional[int] = None,
    ):
        self._wallet = ArbitrageurWallet(
            holdings={token_metadata.symbol: 0 for token_metadata in tokens_metadata},
            tokens_metadata={token_metadata.symbol: token_metadata for token_metadata in tokens_metadata},
        )
        super().__init__(self._wallet, [])
        super(ABCAgent, self).__init__("arbitrageur")
        self._name = Arbitrageur_NAME
        self._tokens_metadata = tokens_metadata
        self._arbitrage_block_frequency = arbitrage_block_frequency
        self._last_arbitraged_block: int = 0
        self._validate()

    def _validate(self) -> None:
        if self._arbitrage_block_frequency is None:
            raise ValueError("The arbitrageur needs to have the block frequency on which to operate")

    def get_list_tokens_wallet(self) -> list[TokenMetadata | StateCERC20]:
        return [self._wallet.tokens_metadata[token] for token in self._wallet.get_list_tokens()]

    def set_environment(
        self,
        env_tokens: list[TokenMetadata],
        env_protocols: dict[str, ABCProtocol],
        env_message_dispatcher: MessageDispatcher,
        env_params_microlanguage: Optional[Any],
        env_common_parameters: CommonParameters,
    ) -> None:
        """
        Use the set_environment method to check validity of the tokens in wallet and of the protocols the arbitrageur
        operates on. Set arbitrageur transactions block timestamps
        """

        # register as message producer
        self._message_dispatcher = env_message_dispatcher
        self._message_dispatcher.register_producer(self, "TRANSACTIONS")

    def _instantiate_policy(self, *args: Any) -> None:
        raise NotImplementedError

    def update_custom_variables(self, custom_variables: list[CustomVariable] | None) -> None:
        raise NotImplementedError

    @property
    def custom_variables(self) -> dict[str, CustomVariable]:
        raise NotImplementedError

    def produce_next_message(self, **kwargs: Any) -> PickableGenerator:
        policy: list[AgentAction] = self.get_policy()

        def update(
            state: Tuple[Arbitrageur, List[AgentAction], int],
        ) -> Tuple[Tuple[Arbitrageur, List[AgentAction], int], None]:
            raise StopIteration

        return StatefulGenerator((self, policy, 0), update)

    @property
    def arbitrage_block_frequency(self) -> Optional[int]:
        return self._arbitrage_block_frequency

    @property
    def last_arbitraged_block(self) -> int:
        return self._last_arbitraged_block

    @last_arbitraged_block.setter
    def last_arbitraged_block(self, block: int) -> None:
        self._last_arbitraged_block = block
