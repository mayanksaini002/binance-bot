import hashlib
import hmac
import logging
import os
import time
from decimal import Decimal
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

from .exceptions import BinanceAPIError, NetworkError, ValidationError


load_dotenv()


class BinanceFuturesClient:
    """Minimal Binance Futures Testnet REST client for signed order requests."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 15,
    ) -> None:
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET")
        self.base_url = (base_url or os.getenv("BINANCE_BASE_URL") or "https://testnet.binancefuture.com").rstrip("/")
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.headers.update({"X-MBX-APIKEY": self.api_key or ""})

        if not self.api_key or not self.api_secret:
            raise ValidationError(
                "Missing Binance credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET."
            )

    def _sign_params(self, params: Dict[str, Any]) -> str:
        query_string = urlencode(params, doseq=True)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return f"{query_string}&signature={signature}"

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        params = params.copy() if params else {}
        url = f"{self.base_url}{path}"

        if signed:
            params["timestamp"] = int(time.time() * 1000)
            prepared_params = self._sign_params(params)
        else:
            prepared_params = urlencode(params, doseq=True)

        self.logger.info(
            "API request | method=%s | path=%s | params=%s",
            method,
            path,
            params,
        )

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=None if signed else params,
                data=prepared_params if signed and method.upper() == "POST" else None,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    **self.session.headers,
                },
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            self.logger.exception("Network failure while calling Binance")
            raise NetworkError(f"Network failure while calling Binance: {exc}") from exc

        try:
            payload = response.json()
        except ValueError:
            payload = response.text

        self.logger.info(
            "API response | status_code=%s | payload=%s",
            response.status_code,
            payload,
        )

        if response.status_code >= 400:
            self.logger.error(
                "Binance returned error | status_code=%s | payload=%s",
                response.status_code,
                payload,
            )
            raise BinanceAPIError(response.status_code, payload)

        if not isinstance(payload, dict):
            raise BinanceAPIError(response.status_code, payload)

        return payload

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Decimal,
        price: Optional[Decimal] = None,
        recv_window: int = 5000,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": format(quantity.normalize(), "f"),
            "recvWindow": recv_window,
            "newOrderRespType": "RESULT",
        }

        if order_type == "LIMIT":
            params["price"] = format(price.normalize(), "f") if price is not None else None
            params["timeInForce"] = "GTC"

        return self._request("POST", "/fapi/v1/order", params=params, signed=True)
