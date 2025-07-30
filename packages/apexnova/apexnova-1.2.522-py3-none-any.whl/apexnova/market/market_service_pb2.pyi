from apexnova.market import market_pb2 as _market_pb2
from apexnova.stub import authorization_context_pb2 as _authorization_context_pb2
from apexnova.stub import response_pb2 as _response_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class YearPeriod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    YEAR_PERIOD_UNSPECIFIED: _ClassVar[YearPeriod]
    YEAR_PERIOD_1Y: _ClassVar[YearPeriod]
    YEAR_PERIOD_2Y: _ClassVar[YearPeriod]
    YEAR_PERIOD_3Y: _ClassVar[YearPeriod]
    YEAR_PERIOD_5Y: _ClassVar[YearPeriod]
    YEAR_PERIOD_10Y: _ClassVar[YearPeriod]

class MovementPeriod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MOVEMENT_PERIOD_UNSPECIFIED: _ClassVar[MovementPeriod]
    MOVEMENT_PERIOD_1D: _ClassVar[MovementPeriod]
    MOVEMENT_PERIOD_1W: _ClassVar[MovementPeriod]
    MOVEMENT_PERIOD_1M: _ClassVar[MovementPeriod]
    MOVEMENT_PERIOD_1Y: _ClassVar[MovementPeriod]
    MOVEMENT_PERIOD_YTD: _ClassVar[MovementPeriod]
YEAR_PERIOD_UNSPECIFIED: YearPeriod
YEAR_PERIOD_1Y: YearPeriod
YEAR_PERIOD_2Y: YearPeriod
YEAR_PERIOD_3Y: YearPeriod
YEAR_PERIOD_5Y: YearPeriod
YEAR_PERIOD_10Y: YearPeriod
MOVEMENT_PERIOD_UNSPECIFIED: MovementPeriod
MOVEMENT_PERIOD_1D: MovementPeriod
MOVEMENT_PERIOD_1W: MovementPeriod
MOVEMENT_PERIOD_1M: MovementPeriod
MOVEMENT_PERIOD_1Y: MovementPeriod
MOVEMENT_PERIOD_YTD: MovementPeriod

class ReadStockRequest(_message.Message):
    __slots__ = ("symbol", "authorization_context")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    authorization_context: _authorization_context_pb2.AuthorizationContext
    def __init__(self, symbol: _Optional[str] = ..., authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ...) -> None: ...

class ReadStockResponse(_message.Message):
    __slots__ = ("stock", "standard_response")
    STOCK_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    stock: _market_pb2.Stock
    standard_response: _response_pb2.StandardResponse
    def __init__(self, stock: _Optional[_Union[_market_pb2.Stock, _Mapping]] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class ReadQuoteRequest(_message.Message):
    __slots__ = ("symbol", "quote_date", "authorization_context")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    QUOTE_DATE_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    quote_date: _timestamp_pb2.Timestamp
    authorization_context: _authorization_context_pb2.AuthorizationContext
    def __init__(self, symbol: _Optional[str] = ..., quote_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ...) -> None: ...

class ReadQuoteResponse(_message.Message):
    __slots__ = ("quote", "standard_response")
    QUOTE_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    quote: _market_pb2.QuoteInfo
    standard_response: _response_pb2.StandardResponse
    def __init__(self, quote: _Optional[_Union[_market_pb2.QuoteInfo, _Mapping]] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class StreamStatementsRequest(_message.Message):
    __slots__ = ("symbol", "fiscal_year", "period", "cursor", "limit", "authorization_context")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    FISCAL_YEAR_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    fiscal_year: _market_pb2.FiscalYear
    period: _market_pb2.ReportingPeriod
    cursor: str
    limit: int
    authorization_context: _authorization_context_pb2.AuthorizationContext
    def __init__(self, symbol: _Optional[str] = ..., fiscal_year: _Optional[_Union[_market_pb2.FiscalYear, str]] = ..., period: _Optional[_Union[_market_pb2.ReportingPeriod, str]] = ..., cursor: _Optional[str] = ..., limit: _Optional[int] = ..., authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ...) -> None: ...

class BalanceSheetStatementResponse(_message.Message):
    __slots__ = ("statement", "standard_response")
    STATEMENT_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    statement: _market_pb2.BalanceSheetStatement
    standard_response: _response_pb2.StandardResponse
    def __init__(self, statement: _Optional[_Union[_market_pb2.BalanceSheetStatement, _Mapping]] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class CashflowStatementResponse(_message.Message):
    __slots__ = ("statement", "standard_response")
    STATEMENT_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    statement: _market_pb2.CashflowStatement
    standard_response: _response_pb2.StandardResponse
    def __init__(self, statement: _Optional[_Union[_market_pb2.CashflowStatement, _Mapping]] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class IncomeStatementResponse(_message.Message):
    __slots__ = ("statement", "standard_response")
    STATEMENT_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    statement: _market_pb2.IncomeStatement
    standard_response: _response_pb2.StandardResponse
    def __init__(self, statement: _Optional[_Union[_market_pb2.IncomeStatement, _Mapping]] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class RevenueGrowthFilter(_message.Message):
    __slots__ = ("period", "min_growth_percentage", "max_growth_percentage")
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    MIN_GROWTH_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    MAX_GROWTH_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    period: YearPeriod
    min_growth_percentage: float
    max_growth_percentage: float
    def __init__(self, period: _Optional[_Union[YearPeriod, str]] = ..., min_growth_percentage: _Optional[float] = ..., max_growth_percentage: _Optional[float] = ...) -> None: ...

class FreeCashFlowGrowthFilter(_message.Message):
    __slots__ = ("period", "min_growth_percentage", "max_growth_percentage", "sbc_adjusted")
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    MIN_GROWTH_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    MAX_GROWTH_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    SBC_ADJUSTED_FIELD_NUMBER: _ClassVar[int]
    period: YearPeriod
    min_growth_percentage: float
    max_growth_percentage: float
    sbc_adjusted: bool
    def __init__(self, period: _Optional[_Union[YearPeriod, str]] = ..., min_growth_percentage: _Optional[float] = ..., max_growth_percentage: _Optional[float] = ..., sbc_adjusted: bool = ...) -> None: ...

class MarketCapFilter(_message.Message):
    __slots__ = ("min_market_cap", "max_market_cap")
    MIN_MARKET_CAP_FIELD_NUMBER: _ClassVar[int]
    MAX_MARKET_CAP_FIELD_NUMBER: _ClassVar[int]
    min_market_cap: float
    max_market_cap: float
    def __init__(self, min_market_cap: _Optional[float] = ..., max_market_cap: _Optional[float] = ...) -> None: ...

class TtmPeFilter(_message.Message):
    __slots__ = ("min_pe_ratio", "max_pe_ratio")
    MIN_PE_RATIO_FIELD_NUMBER: _ClassVar[int]
    MAX_PE_RATIO_FIELD_NUMBER: _ClassVar[int]
    min_pe_ratio: float
    max_pe_ratio: float
    def __init__(self, min_pe_ratio: _Optional[float] = ..., max_pe_ratio: _Optional[float] = ...) -> None: ...

class MoversFilter(_message.Message):
    __slots__ = ("period", "min_movement_percentage", "max_movement_percentage")
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    MIN_MOVEMENT_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    MAX_MOVEMENT_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    period: MovementPeriod
    min_movement_percentage: float
    max_movement_percentage: float
    def __init__(self, period: _Optional[_Union[MovementPeriod, str]] = ..., min_movement_percentage: _Optional[float] = ..., max_movement_percentage: _Optional[float] = ...) -> None: ...

class StockScreenerRequest(_message.Message):
    __slots__ = ("revenue_growth", "fcf_growth", "market_cap", "country", "ttm_pe", "exchange", "sector", "movers", "authorization_context")
    REVENUE_GROWTH_FIELD_NUMBER: _ClassVar[int]
    FCF_GROWTH_FIELD_NUMBER: _ClassVar[int]
    MARKET_CAP_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    TTM_PE_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_FIELD_NUMBER: _ClassVar[int]
    SECTOR_FIELD_NUMBER: _ClassVar[int]
    MOVERS_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    revenue_growth: RevenueGrowthFilter
    fcf_growth: FreeCashFlowGrowthFilter
    market_cap: MarketCapFilter
    country: _market_pb2.Country
    ttm_pe: TtmPeFilter
    exchange: _market_pb2.StockExchange
    sector: _market_pb2.Sector
    movers: MoversFilter
    authorization_context: _authorization_context_pb2.AuthorizationContext
    def __init__(self, revenue_growth: _Optional[_Union[RevenueGrowthFilter, _Mapping]] = ..., fcf_growth: _Optional[_Union[FreeCashFlowGrowthFilter, _Mapping]] = ..., market_cap: _Optional[_Union[MarketCapFilter, _Mapping]] = ..., country: _Optional[_Union[_market_pb2.Country, str]] = ..., ttm_pe: _Optional[_Union[TtmPeFilter, _Mapping]] = ..., exchange: _Optional[_Union[_market_pb2.StockExchange, str]] = ..., sector: _Optional[_Union[_market_pb2.Sector, str]] = ..., movers: _Optional[_Union[MoversFilter, _Mapping]] = ..., authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ...) -> None: ...

class StockScreenerResponse(_message.Message):
    __slots__ = ("stock", "standard_response")
    STOCK_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    stock: _market_pb2.Stock
    standard_response: _response_pb2.StandardResponse
    def __init__(self, stock: _Optional[_Union[_market_pb2.Stock, _Mapping]] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...
