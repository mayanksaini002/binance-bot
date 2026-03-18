import re
from decimal import Decimal, InvalidOperation
from typing import Optional

from .exceptions import ValidationError


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


def normalize_symbol(symbol: str) -> str:
    cleaned = symbol.strip().upper()
    if not SYMBOL_PATTERN.fullmatch(cleaned):
        raise ValidationError(
            "Invalid symbol. Use Binance futures symbols such as BTCUSDT."
        )
    return cleaned


def normalize_side(side: str) -> str:
    cleaned = side.strip().upper()
    if cleaned not in VALID_SIDES:
        raise ValidationError("Invalid side. Allowed values: BUY, SELL.")
    return cleaned


def normalize_order_type(order_type: str) -> str:
    cleaned = order_type.strip().upper()
    if cleaned not in VALID_ORDER_TYPES:
        raise ValidationError("Invalid order type. Allowed values: MARKET, LIMIT.")
    return cleaned


def parse_positive_decimal(value: str, field_name: str) -> Decimal:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(f"{field_name} must be a valid decimal number.") from exc

    if parsed <= 0:
        raise ValidationError(f"{field_name} must be greater than 0.")
    return parsed


def validate_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str],
) -> dict:
    normalized_symbol = normalize_symbol(symbol)
    normalized_side = normalize_side(side)
    normalized_order_type = normalize_order_type(order_type)
    normalized_quantity = parse_positive_decimal(quantity, "quantity")

    normalized_price = None
    if normalized_order_type == "LIMIT":
        if price is None:
            raise ValidationError("price is required for LIMIT orders.")
        normalized_price = parse_positive_decimal(price, "price")
    elif price is not None:
        raise ValidationError("price must only be supplied for LIMIT orders.")

    return {
        "symbol": normalized_symbol,
        "side": normalized_side,
        "order_type": normalized_order_type,
        "quantity": normalized_quantity,
        "price": normalized_price,
    }

