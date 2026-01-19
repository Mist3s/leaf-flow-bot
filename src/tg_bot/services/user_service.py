from tg_bot.api_client.models import UserProfile
from tg_bot.services.order_service import OrdersTextBuilder


class UserService:
    def __init__(self, *, order_builder: OrdersTextBuilder, webapp_url: str):
        self.order_builder = order_builder
        self.webapp_url = webapp_url

    def greeting_for_unknown(self, first_name: str | None) -> tuple[str, list[tuple[str, str]]]:
        name = first_name or "друг"
        text = (
            f"👋 <b>Привет, {name}!</b>\n\n"
            "Добро пожаловать в наш магазин!\n\n"
            "📱 <b>Через приложение вы можете:</b>\n"
            "• 🛍️ посмотреть каталог товаров\n"
            "• 🛒 собрать корзину\n"
            "• 📦 оформить первый заказ\n\n"
            "Нажмите кнопку ниже, чтобы открыть приложение 👇"
        )
        buttons = [("Открыть приложение", self.webapp_url)]
        return text, buttons

    @staticmethod
    def greeting_with_orders(user: UserProfile, has_orders: bool) -> tuple[str, list[str]]:
        name = user.firstName or "друг"
        if not has_orders:
            text = (
                f"👋 <b>Привет, {name}!</b>\n\n"
                "📦 У вас пока нет заказов.\n\n"
                "Вы можете сделать первый заказ через наше приложение — там удобно выбрать товар и оформить доставку.\n\n"
                "📱 <b>Используйте меню:</b>\n"
                "• 📦 Мои заказы\n"
                "• 🛒 Открыть приложение\n"
                "• 👨‍💻 Поддержка"
            )
        else:
            text = (
                f"👋 <b>Привет, {name}!</b>\n\n"
                "Чем могу помочь?\n\n"
                "📱 <b>Вы можете:</b>\n"
                "• 📦 посмотреть свои заказы\n"
                "• 👨‍💻 написать в поддержку\n"
                "• 🛒 открыть приложение с каталогом\n\n"
                "Выберите пункт в меню 👇"
            )
        return text, ["📦 Мои заказы", "🛒 Открыть приложение", "👨‍💻 Поддержка"]
