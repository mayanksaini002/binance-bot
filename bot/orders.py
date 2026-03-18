from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Optional

from .client import BinanceFuturesClient


class OrderService:
    """Business layer for submitting orders and formatting responses."""

    def __init__(self, client: BinanceFuturesClient) -> None:
        self.client = client

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Decimal,
        price: Optional[Decimal] = None,
        recv_window: int = 5000,
    ) -> Dict[str, Any]:
        return self.client.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            recv_window=recv_window,
        )

    @staticmethod
    def summarize_order(
        symbol: str,
        side: str,
        order_type: str,
        quantity: Decimal,
        price: Optional[Decimal] = None,
    ) -> str:
        lines = [
            "Order Request Summary",
            f"  Symbol     : {symbol}",
            f"  Side       : {side}",
            f"  Order Type : {order_type}",
            f"  Quantity   : {quantity}",
        ]
        if price is not None:
            lines.append(f"  Price      : {price}")
        return "\n".join(lines)

    @staticmethod
    def extract_avg_price(response: Dict[str, Any]) -> Optional[str]:
        avg_price = response.get("avgPrice")
        if avg_price not in (None, ""):
            try:
                avg_price_dec = Decimal(str(avg_price))
                if avg_price_dec > 0:
                    return format(avg_price_dec, "f")
            except Exception:
                return str(avg_price)

        executed_qty = response.get("executedQty")
        cum_quote = response.get("cumQuote")
        if not executed_qty or not cum_quote:
            return None

        try:
            executed_qty_dec = Decimal(str(executed_qty))
            cum_quote_dec = Decimal(str(cum_quote))
            if executed_qty_dec == 0:
                return None
            computed = (cum_quote_dec / executed_qty_dec).quantize(
                Decimal("0.00000001"),
                rounding=ROUND_HALF_UP,
            )
            return format(computed, "f")
        except Exception:
            return None

    @classmethod
    def format_response(cls, response: Dict[str, Any]) -> str:
        lines = [
            "Order Response Details",
            f"  Order ID    : {response.get('orderId', 'N/A')}",
            f"  Status      : {response.get('status', 'N/A')}",
            f"  Executed Qty: {response.get('executedQty', 'N/A')}",
        ]
        avg_price = cls.extract_avg_price(response)
        lines.append(f"  Avg Price   : {avg_price or 'N/A'}")
        return "\n".join(lines)
