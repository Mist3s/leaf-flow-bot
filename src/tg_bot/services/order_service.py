from __future__ import annotations

from tg_bot.api_client.models import OrderDetails, OrderListResponse, OrderSummary


class OrdersTextBuilder:
    def __init__(self, *, webapp_url: str):
        self.webapp_url = webapp_url

    def orders_overview(self, orders: OrderListResponse) -> list[str]:
        messages = []
        for order in orders.items:
            messages.append(self.format_order(order))
        return messages

    def order_details(self, order: OrderDetails | None) -> str:
        if not order:
            return "Не удалось получить детали заказа. Попробуйте позже."

        created_at = order.createdAt.strftime("%d.%m.%Y %H:%M")
        status_text = self._human_status(order.status)
        delivery = self._human_delivery(order.deliveryMethod) or "-"
        lines = [
            f"Заказ #{order.orderId}",
            f"Статус: {status_text}",
            f"Доставка: {delivery}",
            f"Сумма: {order.total}",
            f"Оформлен: {created_at}",
            f"------------------------\n"
        ]

        items = [f'# {_.productId} ({_.variantId}) {_.quantity} шт - {_.total}' for _ in order.items]

        if order.comment:
            lines.append(f"Комментарий: {order.comment}")

        return "\n".join(lines) + "\n".join(items)

    @staticmethod
    def format_order(order: OrderSummary) -> str:
        created_at = order.createdAt.strftime("%d.%m.%Y %H:%M")
        return (
            f"Заказ #{order.orderId}\n"
            f"Статус: {order.human_status}\n"
            f"Доставка: {order.human_delivery}\n"
            f"Сумма: {order.total}\n"
            f"Оформлен: {created_at}"
        )

    @staticmethod
    def _human_status(status: str) -> str:
        mapping = {
            "created": "Создан",
            "processing": "В обработке",
            "paid": "Оплачен",
            "fulfilled": "Выполнен",
            "cancelled": "Отменён",
            "shipped": "Отправлен",
        }
        return mapping.get(status, status)

    @staticmethod
    def _human_delivery(deliveryMethod) -> str:
        mapping = {
            "courier": "Курьер",
            "pickup": "Самовывоз",
        }
        return mapping.get(deliveryMethod, deliveryMethod)
