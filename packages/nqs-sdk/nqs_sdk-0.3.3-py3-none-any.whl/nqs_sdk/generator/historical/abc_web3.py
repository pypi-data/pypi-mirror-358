import json
import logging
import os
import time

import requests
from eth_typing.evm import ChecksumAddress
from web3 import Web3

from nqs_sdk.generator import ABCSoloGenerator
from nqs_sdk.observer import ABCObserver
from nqs_sdk.shared_kernel import MessageDispatcher
from nqs_sdk.spot import DataLoader


class Web3SoloGenerator(ABCSoloGenerator):
    """
    A class to generate protocol states and transactions using a web3 provider.
    Child classes do not need to access the web3 provider directly, but can use the
    web3 instance provided by this class available as `self.web3`.
    """

    def __init__(
        self,
        id: int,
        name: str,
    ):
        super().__init__(id, name)
        quantlib = DataLoader.quantlib_source()
        assert quantlib.alchemy_api_key() is not None, "No Alchemy API key found in the environment..."
        assert quantlib.etherscan_api_key(), "No Etherscan API key found in the environment..."
        self.web3 = Web3(Web3.HTTPProvider(f"{quantlib.alchemy_url()}{quantlib.alchemy_api_key()}"))
        self._erc20_abi = self._get_erc20_abi()
        self._protocol_id: str = ""

    def _to_checksum_address(self, address: str) -> ChecksumAddress:
        return Web3.to_checksum_address(address)

    def _get_erc20_abi(self) -> str:
        """
        Load ERC20 ABI from files as it is used by many protocols.
        """
        with open(os.path.join(os.path.dirname(__file__), "ERC20_abi.json"), "r") as f:
            abi: str = json.load(f)["result"]
        return abi

    def _get_contract_abi(self, contract_address: str) -> str | None:
        """
        A function to retrieve a contract's ABI from Etherscan.
        To improve performance, the ABI is saved in a file and loaded from there if it exists.
        """
        quantlib = DataLoader.quantlib_source()
        params = {
            "module": "contract",
            "action": "getabi",
            "address": contract_address,
            "apikey": quantlib.etherscan_api_key(),
        }
        response = requests.get(str(quantlib.etherscan_url()), params=params)
        time.sleep(1)  # on dev api keys, limit the request rate
        result = response.json()
        if result["status"] == "1":
            # Successful response
            abi: str = result["result"]
            return abi
        else:
            # Handle error
            error_message = result["message"]
            logging.info(f"Error: {error_message}")
            return None

    def set_environment(
        self, env_protocol_id: str, env_message_dispatcher: MessageDispatcher, env_observer: ABCObserver
    ) -> None:
        """
        Sets the protocol_id that maps the generator to a protocol, in the environment.
        """
        self._protocol_id = env_protocol_id
        self._message_dispatcher = env_message_dispatcher
        self._message_dispatcher.register_producer(self, "TRANSACTIONS")
