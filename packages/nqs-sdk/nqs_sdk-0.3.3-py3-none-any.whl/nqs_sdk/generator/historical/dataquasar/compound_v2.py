import logging
from typing import Any, Tuple, no_type_check

import numpy as np

from nqs_sdk.generator import DTQSoloGenerator
from nqs_sdk.spot import DataLoader
from nqs_sdk.state import ABCProtocolState, StateCompoundMarket, StateComptroller, StateInterestRateModel
from nqs_sdk.state.compoundv2 import StateCERC20
from nqs_sdk.transaction import ABCTransaction, TransactionCompoundv2
from nqs_sdk.transaction.compoundv2 import (
    BorrowTransactionCompv2,
    LiquidateTransactionCompv2,
    MintTransactionCompv2,
    RedeemTransactionCompv2,
    RepayBorrowTransactionCompv2,
)

CTOKEN_ACCRUE_EVENTS = ["cErc20_evt_AccrueInterest", "cErc20Delegator_evt_AccrueInterest", "cEther_evt_AccrueInterest"]

CTOKENS_EVENTS = {
    "cerc20": {
        "accrue_interest": "cErc20_evt_AccrueInterest",
        "mint": "cErc20_evt_Mint",
        "borrow": "cErc20_evt_Borrow",
        "liquidation": " cErc20_evt_LiquidateBorrow",
        "redeem": "cErc20_evt_Redeem",
        "repay": "cErc20_evt_RepayBorrow",
    },
    "cerc20_delegator": {
        "accrue_interest": "cErc20Delegator_evt_AccrueInterest",
        "mint": "cErc20Delegator_evt_Mint",
        "borrow": "cErc20Delegator_evt_Borrow",
        "liquidation": " cErc20Delegator_evt_LiquidateBorrow",
        "redeem": "cErc20Delegator_evt_Redeem",
        "repay": "cErc20Delegator_evt_RepayBorrow",
    },
    "ceth": {
        "accrue_interest": "cEther_evt_AccrueInterest",
        "mint": "cEther_evt_Mint",
        "borrow": "cEther_evt_Borrow",
        "liquidation": " cEther_evt_LiquidateBorrow",
        "redeem": "cEther_evt_Redeem",
        "repay": "cEther_evt_RepayBorrow",
    },
}

EXCLUDED_MARKETS = ["cSAI", "cREP"]


class DTQCompoundv2Generator(DTQSoloGenerator):
    def __init__(self, id: int, name: str, protocol_info: dict):
        super().__init__(id, name)
        self.market_addresses: dict[str, dict] = self.get_markets_list()
        if protocol_info.get("markets", None) is not None:
            self.market_addresses = {
                key: self.market_addresses[key] for key in protocol_info["markets"] if key in self.market_addresses
            }
        self.total_borrows: dict[str, dict] = {}
        self.underlying_prices: dict[str, dict] = {}

        self.c_address_symbol_mapping: dict[str, dict] = {}
        for key, inner_dict in self.market_addresses.items():
            address = inner_dict.get("address")
            protocol_id = inner_dict.get("id")
            self.total_borrows[key] = {}
            self.underlying_prices[key] = {}
            self.c_address_symbol_mapping[str(address)] = {"symbol": key, "id": protocol_id}
        # logger
        self.logger = logging.getLogger("DTQCompoundV2GeneratorLogger")

    def generate_ctoken_metadata(self) -> list[StateCERC20]:
        ctoken_state: list[StateCERC20] = []

        for ctoken in self.market_addresses:
            ctoken_state += [
                StateCERC20(
                    name=ctoken,
                    symbol=ctoken,
                    decimals=8,
                    # address=self.market_addresses[ctoken]["address"],
                    underlying_symbol=self.market_addresses[ctoken]["underlying"],
                    underlying_address=self.market_addresses[ctoken]["underlying_address"],
                    comptroller_id="comptroller",
                    total_supply=None,
                )
            ]
        return ctoken_state

    def get_markets_list(self) -> dict[str, dict] | Any:
        markets: dict[str, dict] = {}
        offset = 0
        market_list = DataLoader.quantlib_source().compound_v2_market_list()

        market_list = {
            ctoken: {
                "address": market_list["market_address"][i],
                "underlying_address": market_list["underlying_address"][i],
                "id": i + offset,
                "underlying": market_list["underlying_symbol"][i],
            }
            for i, ctoken in enumerate(market_list["symbol"])
        }
        # remove the legacy WBTC market (this could not be done in pyquantlib, so it is done here)
        if (
            "cWBTC" in market_list.keys()
            and market_list["cWBTC"]["address"] == "0xc11b1268c1a384e55c48c2391d8d480264a3a7f4"
        ):
            del market_list["cWBTC"]
        markets.update(market_list)

        return markets

    def generate_state_at_block(self, block_number: int, id: int = -1) -> StateComptroller:
        market_states = {}
        liquidation_incentive_mantissa, close_factor_mantissa = self._get_globals(block_number)
        for ctoken in self.market_addresses.keys():
            if ctoken in EXCLUDED_MARKETS:
                continue
            market_states[ctoken] = self._make_compound_market_state(ctoken, block_number)

        comptroller_state = StateComptroller(
            id=id,
            name="comptroller",
            block_number=block_number,
            block_timestamp=0,
            close_factor_mantissa=close_factor_mantissa,
            liquidation_incentive_mantissa=liquidation_incentive_mantissa,
            max_assets=len(market_states),  # todo - DTQ should fetch this
            market_states=market_states,
        )

        return comptroller_state

    def generate_transactions_at_block(self, block_number: int) -> list[ABCTransaction]:
        return self.generate_transactions_between_blocks(block_number, block_number)

    def generate_transactions_between_blocks(
        self, block_number_from: int, block_number_to: int
    ) -> list[ABCTransaction]:
        events = self._get_events(block_number_from, block_number_to)
        addresses_to_backtest = [ctoken["address"] for ctoken in self.market_addresses.values()]
        # only get the transactions from the markets we want to backtest
        transactions = [
            self.make_transaction(  # type: ignore
                event_type=events["event_type"][i],
                timestamp=int(events["timestamp"][i].astype(np.int64)),
                block_number=int(events["event_block_number"][i]),
                amount=int(events["amount"][i]),
                ctoken=self.c_address_symbol_mapping[events["market"][i]]["symbol"],
                ctoken_collateral=self.c_address_symbol_mapping[events["collateral_address"][i]]["symbol"]
                if events["collateral_address"][i] is not None
                else None,
                total_borrow=int(events["total_borrow"][i]) if events["total_borrow"][i] is not None else None,
            )
            for i in range(len(events["market"]))
            if events["collateral_address"][i] in addresses_to_backtest + [None]
        ]
        # remove liquidation transactions with collaterals not in the list of backtested markets
        # sort transactions by timestamp - possibly also by evt_index if needed
        transactions.sort(key=lambda x: x.block_number)
        return transactions

    @no_type_check
    def make_transaction(
        self,
        event_type: str,
        timestamp: int,
        block_number: int,
        amount: int,
        ctoken: str,
        ctoken_collateral: str | None,
        total_borrow: int | None,
    ) -> TransactionCompoundv2:
        match event_type:
            case "mint":
                transaction = MintTransactionCompv2(
                    block_number=block_number,
                    block_timestamp=timestamp,
                    protocol_id=self.name,
                    sender_wallet=None,
                    mint_amount=amount,
                    ctoken=ctoken,
                )
            case "redeem":
                transaction = RedeemTransactionCompv2(
                    block_number=block_number,
                    block_timestamp=timestamp,
                    protocol_id=self.name,
                    sender_wallet=None,
                    redeem_amount_in=amount,
                    redeem_tokens_in=0,
                    ctoken=ctoken,
                )
            case "borrow":
                self.total_borrows[ctoken][block_number] = total_borrow
                transaction = BorrowTransactionCompv2(
                    block_number=block_number,
                    block_timestamp=timestamp,
                    protocol_id=self.name,
                    sender_wallet=None,
                    borrow_amount=amount,
                    ctoken=ctoken,
                )
            case "repay":
                self.total_borrows[ctoken][block_number] = total_borrow
                transaction = RepayBorrowTransactionCompv2(
                    block_number=block_number,
                    block_timestamp=timestamp,
                    protocol_id=self.name,
                    sender_wallet=None,
                    borrow_wallet=None,
                    repay_amount=amount,
                    ctoken=ctoken,
                )
            case "liquidation":
                transaction = LiquidateTransactionCompv2(
                    block_number=block_number,
                    block_timestamp=timestamp,
                    protocol_id=self.name,
                    sender_wallet=None,
                    borrower=None,
                    repay_amount=amount,
                    ctoken_collateral=ctoken_collateral,
                    ctoken=ctoken,
                )
            case _:
                raise Exception("Unknown event")
        return transaction

    def compare_two_states(self, state_left: ABCProtocolState, state_right: ABCProtocolState) -> None:
        if not isinstance(state_left, StateComptroller) or not isinstance(state_right, StateComptroller):
            raise ValueError("States are not of type StateComptroller")

        for market in state_left.market_states.keys():
            self.logger.info(f"Comparing the info of the {market} market")
            self.compare_market_states(state_left.market_states[market], state_right.market_states[market])

    def compare_market_states(self, state_left: StateCompoundMarket, state_right: StateCompoundMarket) -> None:
        self.logger.info(
            f"Comparing the total_borrow: "
            f"{(float(state_left.total_borrows) / 10 ** state_left.underlying_decimals) :.4f} "
            f"vs {(float(state_right.total_borrows) / 10 ** state_left.underlying_decimals):.4f}"
        )
        self.logger.info(
            f"Comparing the total_reserves: "
            f"{(float(state_left.total_reserves) / 10 ** state_left.underlying_decimals) :.4f} "
            f"vs {(float(state_right.total_reserves) / 10 ** state_left.underlying_decimals):.4f}"
        )
        self.logger.info(
            f"Comparing the total_cash: {(float(state_left.total_cash) / 10 ** state_left.underlying_decimals) :.4f} "
            f"vs {(float(state_right.total_cash) / 10 ** state_left.underlying_decimals):.4f}"
        )
        self.logger.info(
            f"Comparing the total_supply: {(float(state_left.total_supply) / 10 ** state_left.decimals) :.4f} "
            f"vs {(float(state_right.total_supply) / 10 ** state_left.decimals):.4f}"
        )

    # ------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------

    def _get_events(self, block_number_from: int, block_number_to: int) -> dict:
        # get the events from the relevant markets
        events: dict[str, np.ndarray] = {}
        for ctoken in self.market_addresses:
            market_events = DataLoader.quantlib_source().compound_v2_market_events(
                market=self.market_addresses[ctoken]["address"],
                begin_block=block_number_from,
                end_block=block_number_to,
            )
            if market_events is None:
                raise ValueError(f"Cannot fetch events for the market {ctoken}")

            if not events:
                events = market_events
            else:
                events = {key: np.hstack((events[key], market_events[key])) for key in events}

        return events

    def _get_globals(self, block_number: int) -> Tuple[int, int]:
        globals = DataLoader.quantlib_source().compound_v2_globals(end_block=block_number)

        if globals is None:
            raise ValueError("Cannot fetch close factor and liquidation incentive")

        return round(globals["liquidation_incentive"][-1] * 10**18), round(globals["close_factor"][-1] * 10**18)

    def _get_market_snapshot(self, block_number: int, ctoken_symbol: str, is_initial_state: bool = False) -> Any:
        snapshot = DataLoader.quantlib_source().compound_v2_market_snapshot(
            market=self.market_addresses[ctoken_symbol]["address"],
            exclusive_upper_bound=is_initial_state,
            at_block=block_number,
        )

        if snapshot is None:
            raise ValueError(f"failed to fetch the market snapshot for {ctoken_symbol}")

        return snapshot

    def _get_borrow_index(self, block_number: int, ctoken_symbol: str) -> Tuple[int, int]:
        query_result = DataLoader.quantlib_source().compound_v2_market_borrow_index(
            self.market_addresses[ctoken_symbol]["address"],
            event_type="cErc20_evt_AccrueInterest",
            at_block=block_number,
        )

        if query_result is None:
            raise ValueError(f"failed to fetch the latest borrow index for {ctoken_symbol}")

        return int(query_result["borrow_index"]), int(query_result["block_number"])

    def _make_compound_market_state(self, ctoken_symbol: str, block_number: int) -> StateCompoundMarket:
        market_snapshot = self._get_market_snapshot(block_number, ctoken_symbol, is_initial_state=True)
        interest_rate_state = StateInterestRateModel(
            multiplier_per_block=int(market_snapshot["multiplier_per_block"]),
            base_rate_per_block=int(market_snapshot["base_rate_per_block"]),
            jump_multiplier_per_block=int(market_snapshot["jump_multiplier_per_block"]),
            kink=int(market_snapshot["kink"]),
            blocks_per_year=int(market_snapshot["blocks_per_year"]),
        )

        borrow_index, accrual_block_number = self._get_borrow_index(block_number, ctoken_symbol)
        state = StateCompoundMarket(
            id=self.id + self.market_addresses[ctoken_symbol]["id"],
            block_number=block_number,
            block_timestamp=int(market_snapshot["timestamp"]),
            interest_rate_model=interest_rate_state,
            name=self.name + f"_{ctoken_symbol}",
            symbol=ctoken_symbol,
            address=self.market_addresses[ctoken_symbol]["address"],
            underlying=ctoken_symbol.replace("c", "").replace("2", ""),
            underlying_address=self.market_addresses[ctoken_symbol]["underlying_address"],
            decimals=8,
            underlying_decimals=market_snapshot["underlying_decimals"],
            initial_exchange_rate_mantissa=int(
                market_snapshot["exchange_rate"] * 10 ** (18 - 8 + market_snapshot["underlying_decimals"])
            ),
            accrual_block_number=accrual_block_number,
            borrow_index=borrow_index,
            total_borrows=int(market_snapshot["total_borrow"] * 10 ** market_snapshot["underlying_decimals"]),
            total_supply=int(market_snapshot["total_supply"] * 10**8),
            total_reserves=int(market_snapshot["reserves"] * 10 ** market_snapshot["underlying_decimals"]),
            collateral_factor=int(market_snapshot["collateral_factor"] * 10**18),
            borrow_cap=0,  # todo this needs to be added to the fields fetched
            account_borrows={},
            total_cash=int(market_snapshot["cash"] * 10 ** market_snapshot["underlying_decimals"]),
            reserve_factor_mantissa=int(market_snapshot["reserve_factor"] * 10**18),
        )

        return state


# ------------------------------------------------------------
# List of queries
# ------------------------------------------------------------
query_market_list = """
WITH SUBLIST as (SELECT DISTINCT contract_address
                 from compound_v2_evts WHERE name = 'EVT_TYPE')
SELECT DISTINCT CONCAT('c', e.symbol) as symbol, symbol as underlying,
        hex(m.address) as address, 'CONTRACT_TYPE' as contract,
        hex(m.underlying_address) as underlying_address
FROM calc_compv2_markets m
LEFT JOIN erc20_tokens e ON e.address = m.underlying_address
INNER JOIN SUBLIST sb ON sb.contract_address = m.address
"""

query_globals = """
SELECT liquidation_incentive, close_factor FROM calc_compv2_globals
WHERE evt_block_number < BLOCK_NUMBER
ORDER BY evt_block_number DESC, evt_index DESC LIMIT 1
"""

query_market_snapshot = """
SELECT underlying_decimals, underlying_price_eth, underlying_price_usd, cash, evt_block_time, evt_block_number,
exchange_rate, collateral_factor, reserve_factor, reserves, total_supply, borrow_rate, total_borrow, supply_rate,
utilization, multiplier, base_rate, multiplier_per_block, jump_multiplier_per_block, blocks_per_year, kink,
base_rate_per_block
FROM calc_compv2_markets
WHERE evt_block_number OPERATOR BLOCK_NUMBER and hex(address) = 'CTOKEN_ADDRESS'
ORDER BY evt_block_number DESC, evt_index DESC LIMIT 1
"""

query_borrow_index = """
SELECT data::$borrowIndex AS borrow_index, evt_block_number
FROM compound_v2_evts
WHERE evt_block_number < BLOCK_NUMBER and hex(contract_address) = 'CTOKEN_ADDRESS'
and name = 'EVT_NAME'
ORDER BY evt_block_number DESC, evt_index DESC LIMIT 1
"""


query_mint = """
SELECT data::$mintAmount AS amount,
       data::$mintTokens AS tokens,
       evt_block_number as block_number,
       hex(contract_address) as ctoken_address,
       evt_index,
       evt_block_time,
       'mint' as event
FROM compound_v2_evts
WHERE evt_block_number < BLOCK_NUMBER_END and evt_block_number >= BLOCK_NUMBER_START
and (name = 'cErc20_evt_Mint' or name = 'cErc20Delegator_evt_Mint' or name = 'cEther_evt_Mint')
"""

query_redeem = """
SELECT data::$redeemAmount AS amount,
       data::$redeemTokens AS tokens,
       evt_block_number as block_number,
       hex(contract_address) as ctoken_address,
       evt_index,
       evt_block_time,
       'redeem' as event
FROM compound_v2_evts
WHERE evt_block_number < BLOCK_NUMBER_END and evt_block_number >= BLOCK_NUMBER_START
and (name = 'cErc20_evt_Redeem' or name = 'cErc20Delegator_evt_Redeem' or name = 'cEther_evt_Redeem')
"""

query_borrow = """
SELECT data::$borrowAmount AS amount,
       data::$totalBorrows AS total_borrow,
       evt_block_number as block_number,
       hex(contract_address) as ctoken_address,
       evt_index,
       evt_block_time,
       'borrow' as event
FROM compound_v2_evts
WHERE evt_block_number < BLOCK_NUMBER_END and evt_block_number >= BLOCK_NUMBER_START
and (name = 'cErc20_evt_Borrow' or name = 'cErc20Delegator_evt_Borrow' or name = 'cEther_evt_Borrow')
"""

query_repay = """
WITH LIQUIDATIONS as (SELECT evt_tx_hash
                 from compound_v2_evts
                 WHERE (name = 'cErc20_evt_LiquidateBorrow'
                            or name = 'cErc20Delegator_evt_LiquidateBorrow'
                            or name = 'cEther_evt_LiquidateBorrow') and (evt_block_number < BLOCK_NUMBER_END
                            and evt_block_number >= BLOCK_NUMBER_START)
                                       )
SELECT data::$repayAmount AS amount,
       data::$totalBorrows AS total_borrow,
       evt_block_number as block_number,
       hex(contract_address) as ctoken_address,
       evt_index,
       evt_block_time,
       'repay' as event
FROM compound_v2_evts left join LIQUIDATIONS on LIQUIDATIONS.evt_tx_hash = compound_v2_evts.evt_tx_hash
WHERE evt_block_number < BLOCK_NUMBER_END and evt_block_number >= BLOCK_NUMBER_START
and (name = 'cErc20_evt_RepayBorrow' or name = 'cErc20Delegator_evt_RepayBorrow' or name = 'cEther_evt_RepayBorrow')
and LIQUIDATIONS.evt_tx_hash is NULL
"""

query_liquidate = """
SELECT data::$repayAmount AS repay_amount,
       data::$seizeTokens AS seize_tokens,
       JSON_EXTRACT_STRING(data, 'cTokenCollateral') AS collateral_address,
       evt_block_number as block_number,
       hex(contract_address) as ctoken_address,
       evt_index,
       evt_block_time,
       'liquidation' as event
FROM compound_v2_evts
WHERE evt_block_number < BLOCK_NUMBER_END and evt_block_number >= BLOCK_NUMBER_START
and (name = 'cErc20_evt_LiquidateBorrow' or name = 'cErc20Delegator_evt_LiquidateBorrow'
or name = 'cEther_evt_LiquidateBorrow')
"""

# currently not used - not needed at the moment
query_underlying_prices = """
SELECT market.evt_block_number,
       avg(market.underlying_price_usd) AS underlying_price_usd,
       hex(market.address) AS market_address
FROM calc_compv2_markets market inner join compound_v2_evts evt on market.evt_block_number = evt.evt_block_number
WHERE market.evt_block_number < BLOCK_NUMBER_END and market.evt_block_number >= BLOCK_NUMBER_START
group by market.evt_block_number
"""
