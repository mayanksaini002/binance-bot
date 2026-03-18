import argparse
import sys
from pathlib import Path

from .client import BinanceFuturesClient
from .exceptions import BinanceAPIError, NetworkError, TradingBotError, ValidationError
from .logging_config import setup_logging
from .orders import OrderService
from .validators import validate_order_inputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place Binance Futures Testnet USDT-M orders from the command line."
    )
    parser.add_argument("--symbol", required=True, help="Trading symbol, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument("--order-type", required=True, help="MARKET or LIMIT")
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", help="Price for LIMIT orders")
    parser.add_argument(
        "--recv-window",
        default=5000,
        type=int,
        help="Binance recvWindow in milliseconds",
    )
    return parser


def main() -> int:
    log_path: Path = setup_logging()
    parser = build_parser()
    args = parser.parse_args()

    try:
        validated = validate_order_inputs(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
        client = BinanceFuturesClient()
        service = OrderService(client)

        print(
            service.summarize_order(
                symbol=validated["symbol"],
                side=validated["side"],
                order_type=validated["order_type"],
                quantity=validated["quantity"],
                price=validated["price"],
            )
        )

        response = service.place_order(
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["order_type"],
            quantity=validated["quantity"],
            price=validated["price"],
            recv_window=args.recv_window,
        )

        print()
        print(service.format_response(response))
        print()
        print(f"SUCCESS: Order submitted successfully. Log file: {log_path}")
        return 0
    except ValidationError as exc:
        print(f"VALIDATION ERROR: {exc}", file=sys.stderr)
        return 2
    except BinanceAPIError as exc:
        print(f"API ERROR: {exc}", file=sys.stderr)
        print(f"Check logs for request/response details: {log_path}", file=sys.stderr)
        return 3
    except NetworkError as exc:
        print(f"NETWORK ERROR: {exc}", file=sys.stderr)
        print(f"Check logs for request/response details: {log_path}", file=sys.stderr)
        return 4
    except TradingBotError as exc:
        print(f"APPLICATION ERROR: {exc}", file=sys.stderr)
        return 5
    except Exception as exc:
        print(f"UNEXPECTED ERROR: {exc}", file=sys.stderr)
        print(f"Check logs for request/response details: {log_path}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

