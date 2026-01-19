from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from tg_bot.api_client.orders import OrdersApi
from tg_bot.api_client.users import UsersApi
from tg_bot.bot.keyboards.inline import order_actions, open_webapp_button, orders_pagination_keyboard
from tg_bot.config import Settings
from tg_bot.services.order_service import OrdersTextBuilder


async def _safe_callback_answer(callback: CallbackQuery, text: str | None = None) -> None:
    """Безопасный ответ на callback query с обработкой устаревших запросов"""
    try:
        await callback.answer(text)
    except TelegramBadRequest:
        # Callback query устарел или уже был обработан - игнорируем
        pass

router = Router()

# Лимит заказов на странице
ORDERS_PER_PAGE = 3


async def _send_orders_page(
    message_or_callback: Message | CallbackQuery,
    user_telegram_id: int,
    orders_api: OrdersApi,
    order_builder: OrdersTextBuilder,
    offset: int = 0,
) -> None:
    """Отправить страницу заказов с пагинацией"""
    orders = await orders_api.list_orders(user_telegram_id, limit=ORDERS_PER_PAGE, offset=offset)
    
    if not orders.items:
        if offset > 0:
            text = "✅ <b>Больше заказов нет</b>\n\nВы просмотрели все свои заказы."
        else:
            text = (
                "📦 <b>У вас пока нет заказов</b>\n\n"
                "Вы можете оформить первый заказ в приложении — нажмите кнопку ниже 👇"
            )
        if isinstance(message_or_callback, CallbackQuery):
            await message_or_callback.message.answer(text)
            await _safe_callback_answer(message_or_callback)
        else:
            await message_or_callback.answer(text)
        return

    # Отправляем каждый заказ отдельным сообщением
    for order in orders.items:
        if isinstance(message_or_callback, CallbackQuery):
            await message_or_callback.message.answer(
                order_builder.format_order(order), 
                reply_markup=order_actions(order.orderId)
            )
        else:
            await message_or_callback.answer(
                order_builder.format_order(order), 
                reply_markup=order_actions(order.orderId)
            )
    
    # Если вернулось ровно ORDERS_PER_PAGE заказов, возможно есть еще
    if len(orders.items) == ORDERS_PER_PAGE:
        next_offset = offset + ORDERS_PER_PAGE
        pagination_text = "📄 <b>Показать еще заказы?</b>\n\nНажмите кнопку ниже 👇"
        if isinstance(message_or_callback, CallbackQuery):
            await message_or_callback.message.answer(
                pagination_text,
                reply_markup=orders_pagination_keyboard(next_offset)
            )
            await _safe_callback_answer(message_or_callback)
        else:
            await message_or_callback.answer(
                pagination_text,
                reply_markup=orders_pagination_keyboard(next_offset)
            )


@router.message(Command("orders"))
@router.message(F.text == "📦 Мои заказы")
async def list_orders(message: Message, settings: Settings, users_api: UsersApi, orders_api: OrdersApi, order_builder: OrdersTextBuilder):
    user_profile = await users_api.get_by_telegram(message.from_user.id) if message.from_user else None
    if not user_profile:
        await message.answer(
            "📱 <b>Привет!</b>\n\n"
            "Похоже, вы ещё не открывали приложение. Нажмите кнопку ниже, чтобы перейти в него 👇",
            reply_markup=open_webapp_button(str(settings.webapp_url)),
        )
        return

    await _send_orders_page(message, user_profile.telegramId, orders_api, order_builder, offset=0)


@router.callback_query(lambda c: c.data and c.data.startswith("orders:page:"))
async def orders_pagination(callback: CallbackQuery, users_api: UsersApi, orders_api: OrdersApi, order_builder: OrdersTextBuilder):
    """Обработчик пагинации списка заказов"""
    if not callback.from_user:
        await _safe_callback_answer(callback, "❌ Ошибка: не удалось определить пользователя")
        return
    
    # Удаляем сообщение с кнопкой "Показать еще"
    if callback.message:
        try:
            await callback.message.delete()
        except Exception:
            # Если не удалось удалить (например, сообщение уже удалено), продолжаем
            pass
    
    await _safe_callback_answer(callback)
    
    user_profile = await users_api.get_by_telegram(callback.from_user.id)
    if not user_profile:
        if callback.message:
            await callback.message.answer("❌ <b>Ошибка</b>\n\nПользователь не найден")
        return
    
    try:
        offset = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        if callback.message:
            await callback.message.answer("❌ <b>Ошибка</b>\n\nНеверный формат данных")
        return
    
    await _send_orders_page(callback, user_profile.telegramId, orders_api, order_builder, offset=offset)


@router.callback_query(lambda c: c.data and c.data.startswith("order:"))
async def order_details(callback: CallbackQuery, orders_api: OrdersApi, order_builder: OrdersTextBuilder):
    # Сразу отвечаем на callback, чтобы не было таймаута
    await _safe_callback_answer(callback)
    
    order_id = callback.data.split(":", maxsplit=1)[1]
    details = await orders_api.get_order(order_id)
    await callback.message.answer(order_builder.order_details(details))


@router.callback_query(lambda c: c.data and c.data.startswith("admin:order:"))
async def admin_order_details(
    callback: CallbackQuery, 
    orders_api: OrdersApi, 
    order_builder: OrdersTextBuilder,
    settings: Settings,
):
    """Обработчик кнопки 'Подробнее' для администратора в админском чате"""
    # Проверяем, что это админский чат
    if callback.message and callback.message.chat.id != settings.admin_chat_id:
        await _safe_callback_answer(callback, "❌ Эта команда доступна только администраторам")
        return
    
    # Сразу отвечаем на callback, чтобы не было таймаута
    await _safe_callback_answer(callback)
    
    order_id = callback.data.split(":", maxsplit=2)[-1]
    details = await orders_api.get_order(order_id)
    
    if details:
        await callback.message.answer(order_builder.order_details(details))
    else:
        await callback.message.answer("❌ Заказ не найден")
