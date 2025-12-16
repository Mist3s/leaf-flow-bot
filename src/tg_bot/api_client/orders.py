from __future__ import annotations

from typing import Optional

from tg_bot.api_client.base import BaseApiClient
from tg_bot.api_client.models import OrderDetails, OrderListResponse


class OrdersApi(BaseApiClient):
    async def list_orders(self, telegram_id: int, limit: int = 5, offset: int = 0) -> OrderListResponse:
        response = await self._get(
            "/api/v1/internal/orders",
            params={"telegram_id": telegram_id, "limit": limit, "offset": offset},
        )
        return OrderListResponse.model_validate(response.json())

    async def get_order(self, order_id: str) -> Optional[OrderDetails]:
        try:
            response = await self._get(f"/api/v1/internal/orders/{order_id}")
        except Exception:  # noqa: BLE001
            return None
        return OrderDetails.model_validate(response.json())

    async def update_order_status(
        self, 
        order_id: str, 
        new_status: str, 
        comment: str | None = None
    ) -> Optional[OrderDetails]:
        """
        Обновить статус заказа.
        
        Args:
            order_id: ID заказа
            new_status: Новый статус заказа
            comment: Опциональный комментарий
            
        Returns:
            OrderDetails: Обновленные детали заказа или None при ошибке
        """
        try:
            payload = {"newStatus": new_status}
            if comment:
                payload["comment"] = comment
            
            response = await self._patch(
                f"/api/v1/internal/orders/{order_id}/status",
                json=payload,
            )
            return OrderDetails.model_validate(response.json())
        except Exception:  # noqa: BLE001
            return None
