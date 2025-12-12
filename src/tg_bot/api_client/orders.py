from __future__ import annotations

from typing import Optional

from tg_bot.api_client.base import BaseApiClient
from tg_bot.api_client.models import OrderDetails, OrderListResponse


class OrdersApi(BaseApiClient):
    async def list_orders(self, telegram_id: int, limit: int = 5, offset: int = 0) -> OrderListResponse:
        response = await self._get(
            "/api/v1/internal/orders",
            params={"telegramId": telegram_id, "limit": limit, "offset": offset},
        )
        return OrderListResponse.model_validate(response.json())

    async def get_order(self, order_id: str) -> Optional[OrderDetails]:
        try:
            response = await self._get(f"/api/v1/internal/orders/{order_id}")
        except Exception:  # noqa: BLE001
            return None
        return OrderDetails.model_validate(response.json())
