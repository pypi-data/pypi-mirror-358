"""AKShare Equity Quote Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_quote import (
    EquityQuoteData,
    EquityQuoteQueryParams,
)
from pydantic import Field
import logging
from openbb_akshare.utils.tools import setup_logger, normalize_symbol, get_symbol_base

logger = logging.getLogger(__name__)

class AKShareEquityQuoteQueryParams(EquityQuoteQueryParams):
    """AKShare Equity Quote Query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class AKShareEquityQuoteData(EquityQuoteData):
    """AKShare Equity Quote Data."""

    __alias_dict__ = {
        "symbol": "代码",
        "name": "名称",
        "exchange": "交易所",
        "last_price": "现价",
        "open": "今开",
        "close": "均价",
        "high": "最高",
        "low": "最低",
        "prev_close": "昨收",
        "year_high": "52周最高",
        "year_low": "52周最低",
        "volume": "成交量",
        "change": "涨跌",
        "participant_timestamp": "时间",
        "market_cap": "流通值",
        "pe_ratio": "市盈率(动)",
        "pe_ratio_ttm": "市盈率(TTM)",
        "turnover": "成交额",
        "currency": "货币",
    }

    market_cap: Optional[float] = Field(
        default=None,
        description="Market capitalization.",
    )
    pe_ratio: Optional[float] = Field(
        default=None,
        description="Price-to-earnings ratio.",
    )
    pe_ratio_ttm: Optional[float] = Field(
        default=None,
        description="Price-to-earnings ratio (TTM).",
    )
    turnover: Optional[float] = Field(
        default=None,
        description="Turnover of the stock.",
    )
    currency: Optional[str] = Field(
        default=None,
        description="Currency of the price.",
    )


class AKShareEquityQuoteFetcher(
    Fetcher[AKShareEquityQuoteQueryParams, List[AKShareEquityQuoteData]]
):
    """AKShare Equity Quote Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AKShareEquityQuoteQueryParams:
        """Transform the query."""
        return AKShareEquityQuoteQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: AKShareEquityQuoteQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from AKShare."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from curl_adapter import CurlCffiAdapter
        from openbb_core.provider.utils.helpers import get_requests_session
        import akshare as ak

        symbols = query.symbol.split(",")
        results = []
        fields = ['代码', 
                  '名称', 
                  '交易所', 
                  '现价', 
                  '今开',
                  '均价', 
                  '最高', 
                  '最低', 
                  '昨收', 
                  '52周最高', 
                  '52周最低', 
                  '成交量', 
                  '涨跌', 
                  '时间', 
                  '流通值', 
                  '市盈率(动)', 
                  '市盈率(TTM)',
                  '成交额', 
                  '货币']
        async def get_one(symbol):
            """Get the data for one ticker symbol."""
            result: dict = {}
            ticker: dict = {}
            try:
                symbol_b, symbol_f, market = normalize_symbol(symbol)
                if market == "SH" or market == "SZ":
                    symbol = market+symbol_b
                elif market == "BJ":
                    symbol = "NQ"+symbol_b
                ticker_df = ak.stock_individual_spot_xq(symbol)
                if ticker_df.empty:
                    logger.debug("ticker_df is empty.")
                else:
                    ticker = dict(zip(ticker_df['item'], ticker_df['value']))
            except Exception as e:
                warn(f"Error getting data for {symbol}: {e}")
            if ticker:
                for field in fields:
                    if field in ticker:
                        result[field] = ticker.get(field, None)
                if result:
                    results.append(result)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        return results

    @staticmethod
    def transform_data(
        query: AKShareEquityQuoteQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[AKShareEquityQuoteData]:
        """Transform the data."""
        return [AKShareEquityQuoteData.model_validate(d) for d in data]
