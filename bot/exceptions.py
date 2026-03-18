class TradingBotError(Exception):
    """Base exception for the trading bot."""


class ValidationError(TradingBotError):
    """Raised when CLI input or order parameters are invalid."""


class BinanceAPIError(TradingBotError):
    """Raised when Binance returns an API error response."""

    def __init__(self, status_code: int, payload: object):
        self.status_code = status_code
        self.payload = payload
        message = f"Binance API error (status={status_code}): {payload}"
        super().__init__(message)


class NetworkError(TradingBotError):
    """Raised when the request cannot reach Binance."""

