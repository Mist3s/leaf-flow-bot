from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    id: str
    telegramId: int
    firstName: Optional[str]
    lastName: Optional[str]
    username: Optional[str]
    languageCode: Optional[str]
    photoUrl: Optional[str]

    def full_name(self) -> str:
        names = [name for name in [self.firstName, self.lastName] if name]
        return " ".join(names) if names else "Гость"


class OrderSummary(BaseModel):
    orderId: str
    customerName: Optional[str]
    deliveryMethod: str
    total: str
    status: str
    createdAt: datetime

    @property
    def human_status(self) -> str:
        mapping = {
            "created": "Создан",
            "processing": "В обработке",
            "paid": "Оплачен",
            "fulfilled": "Выполнен",
            "cancelled": "Отменён",
        }
        return mapping.get(self.status, self.status)

    @property
    def human_delivery(self) -> str:
        mapping = {
            "courier": "Курьер",
            "pickup": "Самовывоз",
        }
        return mapping.get(self.deliveryMethod, self.deliveryMethod)


class OrderListResponse(BaseModel):
    items: list[OrderSummary] = Field(default_factory=list)


class OrderDetails(BaseModel):
    orderId: str
    status: str
    total: str
    deliveryMethod: Optional[str] = None
    createdAt: datetime
    comment: Optional[str] = None
