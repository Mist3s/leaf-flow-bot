from __future__ import annotations

from tg_bot.api_client.models import OrderDetails, OrderListResponse, OrderSummary


class OrdersTextBuilder:
    def __init__(self, *, webapp_url: str):
        self.webapp_url = webapp_url

    def orders_overview(self, orders: OrderListResponse) -> list[str]:
        messages = []
        for order in orders.items:
            messages.append(self._format_order(order))
        return messages

    def order_details(self, order: OrderDetails | None) -> str:
        if not order:
            return "Не удалось получить детали заказа. Попробуйте позже."
        created_at = order.createdAt.strftime("%d.%m.%Y %H:%M")
        status_text = self._human_status(order.status)
        delivery = order.deliveryMethod or "-"
        lines = [
            f"Заказ №{order.orderId}",
            f"Статус: {status_text}",
            f"Доставка: {delivery}",
            f"Сумма: {order.total}",
            f"Оформлен: {created_at}",
        ]
        if order.comment:
            lines.append(f"Комментарий: {order.comment}")
        return "\n".join(lines)

    def _format_order(self, order: OrderSummary) -> str:
        created_at = order.createdAt.strftime("%d.%m.%Y %H:%M")
        return (
            f"Заказ №{order.orderId}\n"
            f"Статус: {order.human_status}\n"
            f"Доставка: {order.human_delivery}\n"
            f"Сумма: {order.total}\n"
            f"Оформлен: {created_at}"
        )

    def _human_status(self, status: str) -> str:
        mapping = {
            "created": "Создан",
            "processing": "В обработке",
            "paid": "Оплачен",
            "fulfilled": "Выполнен",
            "cancelled": "Отменён",
            "shipped": "Отправлен",
        }
        return mapping.get(status, status)
