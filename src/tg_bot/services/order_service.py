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
            return "❌ <b>Ошибка</b>\n\nНе удалось получить детали заказа. Попробуйте позже."

        created_at = order.createdAt.strftime("%d.%m.%Y %H:%M")
        status_text = self._human_status(order.status)
        status_emoji = self._status_emoji(order.status)
        delivery = self._human_delivery(order.deliveryMethod) or "-"
        delivery_emoji = self._delivery_emoji(order.deliveryMethod)
        
        # Заголовок заказа
        lines = [
            f"📦 <b>Заказ #{order.orderId}</b>",
            "",
            f"{status_emoji} <b>Статус:</b> {status_text}",
            f"{delivery_emoji} <b>Доставка:</b> {delivery}",
            f"💰 <b>Сумма:</b> {order.total} ₽",
            f"📅 <b>Оформлен:</b> {created_at}",
        ]
        
        # Позиции заказа
        if order.items:
            lines.append("")
            lines.append("━━━━━━━━━━━━━━━━━━━━")
            lines.append("")
            lines.append("🛍️ <b>Состав заказа:</b>")
            lines.append("")
            
            # Используем названия, если они доступны, иначе используем ID
            for idx, item in enumerate(order.items, 1):
                product_display = item.productName if item.productName else item.productId
                variant_display = item.variantWeight if item.variantWeight else item.variantId
                lines.append(
                    f"{idx}. <b>{product_display}</b>\n"
                    f"   └ {variant_display} × {item.quantity} шт = <b>{item.total} ₽</b>"
                )
        
        # Комментарий
        if order.comment:
            lines.append("")
            lines.append("━━━━━━━━━━━━━━━━━━━━")
            lines.append("")
            lines.append(f"💬 <b>Комментарий:</b>\n{order.comment}")

        return "\n".join(lines)
    
    @staticmethod
    def _status_emoji(status: str) -> str:
        """Возвращает эмодзи для статуса заказа"""
        mapping = {
            "created": "🆕",
            "processing": "⏳",
            "paid": "✅",
            "fulfilled": "🎉",
            "cancelled": "❌",
            "shipped": "🚚",
        }
        return mapping.get(status, "📋")
    
    @staticmethod
    def _delivery_emoji(delivery_method: str | None) -> str:
        """Возвращает эмодзи для способа доставки"""
        mapping = {
            "courier": "🚚",
            "pickup": "🏪",
            "cdek": "📦",
        }
        return mapping.get(delivery_method or "", "📍")

    @staticmethod
    def format_order(order: OrderSummary) -> str:
        created_at = order.createdAt.strftime("%d.%m.%Y %H:%M")
        status_emoji = OrdersTextBuilder._status_emoji(order.status)
        delivery_emoji = OrdersTextBuilder._delivery_emoji(order.deliveryMethod)
        
        return (
            f"📦 <b>Заказ #{order.orderId}</b>\n"
            f"{status_emoji} <b>Статус:</b> {order.human_status}\n"
            f"{delivery_emoji} <b>Доставка:</b> {order.human_delivery}\n"
            f"💰 <b>Сумма:</b> {order.total} ₽\n"
            f"📅 <b>Оформлен:</b> {created_at}"
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
