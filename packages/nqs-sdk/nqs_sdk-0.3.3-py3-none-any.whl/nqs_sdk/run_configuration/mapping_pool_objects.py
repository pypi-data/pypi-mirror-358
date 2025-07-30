# ruff: noqa: E501
from typing import Any

from nqs_sdk.generator import DTQCompoundv2Generator, DTQUniswapV3Generator
from nqs_sdk.observer.protocol.cex import CEXObserver
from nqs_sdk.observer.protocol.compoundv2 import ComptrollerObserver
from nqs_sdk.observer.protocol.uniswapv3 import UniswapV3Observer
from nqs_sdk.protocol import Comptroller, UniswapV3
from nqs_sdk.protocol.cex import CEX

mapping_protocols_objects: dict[str, Any] = {
    "uniswap_v3": {"generator": DTQUniswapV3Generator, "protocol": UniswapV3, "observer": UniswapV3Observer},
    "compound_v2": {"generator": DTQCompoundv2Generator, "protocol": Comptroller, "observer": ComptrollerObserver},
    "cex": {"generator": None, "protocol": CEX, "observer": CEXObserver},
}

mapping_address_protocol: dict[str, Any] = {}
