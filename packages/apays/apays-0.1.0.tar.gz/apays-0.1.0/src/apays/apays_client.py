import uuid
import asyncio
import hashlib
from decimal import Decimal, ROUND_HALF_UP

import httpx
from pydantic import BaseModel, HttpUrl
from typing import Optional


class APayError(Exception):
    """Базовое исключение клиента APays."""


class APayNetworkError(APayError):
    """Проблемы сети / соединения."""


class APayAPIError(APayError):
    """API вернуло некорректный статус или данные."""


class CreateOrderResponse(BaseModel):
    status: bool
    url: HttpUrl
    order_id: str


class OrderStatusResponse(BaseModel):
    status: bool
    order_status: str


class APaysClient:
    def __init__(
        self,
        client_id: int,
        secret_key: str,
        base_url: str = "https://apays.io/backend"
    ):
        self.client_id = client_id
        self.secret_key = secret_key
        self.base_url = base_url
        self._client = httpx.AsyncClient(timeout=10.0)

    async def create_order(self, amount: float) -> CreateOrderResponse:
        """
        Создание платежа.
        :param amount: Сумма с копейками, например 123.45 → 12345 (копеек)
        :return: CreateOrderResponse
        """
        dec_amount = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        amount_int = int(dec_amount * 100)

        order_id = str(uuid.uuid4())
        sign_str = f"{order_id}:{amount_int}:{self.secret_key}"
        sign = hashlib.md5(sign_str.encode()).hexdigest()

        params = {
            "client_id": self.client_id,
            "order_id": order_id,
            "amount": amount_int,
            "sign": sign,
        }
        url = f"{self.base_url}/create_order"

        resp = await self._client.get(f"{self.base_url}/create_order", params=params)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise APayAPIError(f"HTTP {e.response.status_code}: {e.response.text}") from e

        try:
            data = resp.json()
        except ValueError:
            raise APayAPIError("Invalid JSON")

        if "error" in data:
            raise APayAPIError(f"API error: {data['error']}")

        for fld in ("status", "url"):
            if fld not in data:
                raise APayAPIError(f"Missing `{fld}` in response")

        from pydantic import ValidationError
        try:
            return CreateOrderResponse(order_id=order_id, **data)
        except ValidationError as e:
            raise APayAPIError(f"Bad model: {e}") from e

    async def get_order(self, order_id: str) -> OrderStatusResponse:
        """
        Проверка статуса платежа по ID.
        :param order_id: UUID заказа
        """
        sign_str = f"{order_id}:{self.secret_key}"
        sign = hashlib.md5(sign_str.encode()).hexdigest()

        params = {
            "client_id": self.client_id,
            "order_id": order_id,
            "sign": sign,
        }
        url = f"{self.base_url}/get_order"

        try:
            resp = await self._client.get(url, params=params)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise APayAPIError(f"Bad response {e.response.status_code}: {e.response.text}") from e
        except httpx.RequestError as e:
            raise APayNetworkError(f"Network error: {e}") from e

        try:
            return OrderStatusResponse(**resp.json())
        except ValueError as e:
            raise APayAPIError("Invalid JSON in status response") from e

    async def start_order_polling(
        self,
        order_id: str,
        interval: float = 2.0,
        timeout: Optional[float] = 60.0
    ) -> OrderStatusResponse:
        """
        Ожидает, пока статус заказа перестанет быть 'pending'.
        :param order_id: UUID ранее созданного заказа.
        :param interval: задержка между опросами (в секундах).
        :param timeout: максимальное время ожидания (в секундах).
        :raises APayAPIError: если таймаут вышел или API вернул ошибку.
        """
        start = asyncio.get_event_loop().time()
        while True:
            resp = await self.get_order(order_id)
            if resp.order_status != "pending":
                return resp

            if timeout is not None and (asyncio.get_event_loop().time() - start) > timeout:
                raise APayAPIError(f"Timeout waiting for order {order_id}")

            await asyncio.sleep(interval)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self) -> None:
        """Закрывает HTTP-сессии."""
        await self._client.aclose()
