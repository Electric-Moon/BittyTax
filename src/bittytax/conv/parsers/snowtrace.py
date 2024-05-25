# -*- coding: utf-8 -*-
# (c) Nano Nano Ltd 2021

from decimal import Decimal
from typing import TYPE_CHECKING

from typing_extensions import Unpack

from ...bt_types import TrType
from ..dataparser import DataParser, ParserArgs, ParserType
from ..datarow import TxRawPos
from ..out_record import TransactionOutRecord
from .etherscan import _get_note

if TYPE_CHECKING:
    from ..datarow import DataRow

WALLET = "Avalanche chain"
WORKSHEET_NAME = "SnowTrace"


def parse_snowtrace(data_row: "DataRow", parser: DataParser, **_kwargs: Unpack[ParserArgs]) -> None:
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["UnixTimestamp"]))
    data_row.tx_raw = TxRawPos(
        parser.in_header.index("Txhash"),
        parser.in_header.index("From"),
        parser.in_header.index("To"),
    )

    if row_dict["Status"] != "":
        # Failed transactions should not have a Value_OUT
        row_dict["Value_OUT(AVAX)"] = "0"

    if Decimal(row_dict["Value_IN(AVAX)"]) > 0:
        if row_dict["Status"] == "":
            data_row.t_record = TransactionOutRecord(
                TrType.DEPOSIT,
                data_row.timestamp,
                buy_quantity=Decimal(row_dict["Value_IN(AVAX)"]),
                buy_asset="AVAX",
                wallet=_get_wallet(row_dict["To"]),
                note=_get_note(row_dict),
            )
    elif Decimal(row_dict["Value_OUT(AVAX)"]) > 0:
        data_row.t_record = TransactionOutRecord(
            TrType.WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=Decimal(row_dict["Value_OUT(AVAX)"]),
            sell_asset="AVAX",
            fee_quantity=Decimal(row_dict["TxnFee(AVAX)"]),
            fee_asset="AVAX",
            wallet=_get_wallet(row_dict["From"]),
            note=_get_note(row_dict),
        )
    else:
        data_row.t_record = TransactionOutRecord(
            TrType.SPEND,
            data_row.timestamp,
            sell_quantity=Decimal(row_dict["Value_OUT(AVAX)"]),
            sell_asset="AVAX",
            fee_quantity=Decimal(row_dict["TxnFee(AVAX)"]),
            fee_asset="AVAX",
            wallet=_get_wallet(row_dict["From"]),
            note=_get_note(row_dict),
        )


def _get_wallet(address: str) -> str:
    return f"{WALLET}-{address.lower()[0 : TransactionOutRecord.WALLET_ADDR_LEN]}"


def parse_snowtrace_internal(
    data_row: "DataRow", parser: DataParser, **_kwargs: Unpack[ParserArgs]
) -> None:
    row_dict = data_row.row_dict
    data_row.timestamp = DataParser.parse_timestamp(int(row_dict["UnixTimestamp"]))
    data_row.tx_raw = TxRawPos(
        parser.in_header.index("Txhash"),
        parser.in_header.index("From"),
        parser.in_header.index("TxTo"),
    )

    # Failed internal transaction
    if row_dict["Status"] != "0":
        return

    if Decimal(row_dict["Value_IN(AVAX)"]) > 0:
        data_row.t_record = TransactionOutRecord(
            TrType.DEPOSIT,
            data_row.timestamp,
            buy_quantity=Decimal(row_dict["Value_IN(AVAX)"]),
            buy_asset="AVAX",
            wallet=_get_wallet(row_dict["TxTo"]),
        )
    elif Decimal(row_dict["Value_OUT(AVAX)"]) > 0:
        data_row.t_record = TransactionOutRecord(
            TrType.WITHDRAWAL,
            data_row.timestamp,
            sell_quantity=Decimal(row_dict["Value_OUT(AVAX)"]),
            sell_asset="AVAX",
            wallet=_get_wallet(row_dict["From"]),
        )


# Token and NFT transactions have the same header as Etherscan
avax_txns = DataParser(
    ParserType.EXPLORER,
    "SnowTrace (AVAX Transactions)",
    [
        lambda c: c in ("Txhash", "Transaction Hash"),  # Renamed
        "Blockno",
        "UnixTimestamp",
        lambda c: c in ("DateTime", "DateTime (UTC)"),  # Renamed
        "From",
        "To",
        "ContractAddress",
        "Value_IN(AVAX)",
        "Value_OUT(AVAX)",
        None,
        "TxnFee(AVAX)",
        "TxnFee(USD)",
        "Historical $Price/AVAX",
        "Status",
        "ErrCode",
        "Method",  # New field
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_snowtrace,
)

DataParser(
    ParserType.EXPLORER,
    "SnowTrace (AVAX Transactions)",
    [
        lambda c: c in ("Txhash", "Transaction Hash"),  # Renamed
        "Txhash",
        "Blockno",
        lambda c: c in ("DateTime", "DateTime (UTC)"),  # Renamed
        "From",
        "To",
        "ContractAddress",
        "Value_IN(AVAX)",
        "Value_OUT(AVAX)",
        None,
        "TxnFee(AVAX)",
        "TxnFee(USD)",
        "Historical $Price/AVAX",
        "Status",
        "ErrCode",
        "Method",  # New field
        "PrivateNote",
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_snowtrace,
)

DataParser(
    ParserType.EXPLORER,
    "SnowTrace (AVAX Transactions)",
    [
        "Txhash",
        "Blockno",
        "UnixTimestamp",
        "DateTime",
        "From",
        "To",
        "ContractAddress",
        "Value_IN(AVAX)",
        "Value_OUT(AVAX)",
        None,
        "TxnFee(AVAX)",
        "TxnFee(USD)",
        "Historical $Price/AVAX",
        "Status",
        "ErrCode",
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_snowtrace,
)

DataParser(
    ParserType.EXPLORER,
    "SnowTrace (AVAX Transactions)",
    [
        "Txhash",
        "Blockno",
        "UnixTimestamp",
        "DateTime",
        "From",
        "To",
        "ContractAddress",
        "Value_IN(AVAX)",
        "Value_OUT(AVAX)",
        None,
        "TxnFee(AVAX)",
        "TxnFee(USD)",
        "Historical $Price/AVAX",
        "Status",
        "ErrCode",
        "PrivateNote",
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_snowtrace,
)

avax_int = DataParser(
    ParserType.EXPLORER,
    "SnowTrace (AVAX Internal Transactions)",
    [
        lambda c: c in ("Txhash", "Transaction Hash"),  # Renamed
        "Blockno",
        "UnixTimestamp",
        lambda c: c in ("DateTime", "DateTime (UTC)"),  # Renamed
        "ParentTxFrom",
        "ParentTxTo",
        "ParentTxETH_Value",
        "From",
        "TxTo",
        "ContractAddress",
        "Value_IN(AVAX)",
        "Value_OUT(AVAX)",
        None,
        "Historical $Price/AVAX",
        "Status",
        "ErrCode",
        "Type",
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_snowtrace_internal,
)

DataParser(
    ParserType.EXPLORER,
    "SnowTrace (AVAX Internal Transactions)",
    [
        lambda c: c in ("Txhash", "Transaction Hash"),  # Renamed
        "Blockno",
        "UnixTimestamp",
        lambda c: c in ("DateTime", "DateTime (UTC)"),  # Renamed
        "ParentTxFrom",
        "ParentTxTo",
        "ParentTxETH_Value",
        "From",
        "TxTo",
        "ContractAddress",
        "Value_IN(AVAX)",
        "Value_OUT(AVAX)",
        None,
        "Historical $Price/AVAX",
        "Status",
        "ErrCode",
        "Type",
        "PrivateNote",
    ],
    worksheet_name=WORKSHEET_NAME,
    row_handler=parse_snowtrace_internal,
)
