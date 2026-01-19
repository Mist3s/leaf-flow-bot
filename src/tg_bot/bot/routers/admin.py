from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from tg_bot.api_client.orders import OrdersApi
from tg_bot.bot.keyboards.inline import admin_order_status_keyboard, admin_status_comment_keyboard
from tg_bot.bot.states import AdminOrderStatusStates
from tg_bot.config import Settings
from tg_bot.services.order_service import OrdersTextBuilder

logger = logging.getLogger(__name__)


async def _safe_callback_answer(callback: CallbackQuery, text: str | None = None) -> None:
    """Безопасный ответ на callback query с обработкой устаревших запросов"""
    try:
        await callback.answer(text)
    except TelegramBadRequest:
        # Callback query устарел или уже был обработан - игнорируем
        pass

router = Router()

# Маппинг статусов для отображения
STATUS_NAMES = {
    "created": "🆕 Создан",
    "processing": "⏳ В обработке",
    "paid": "✅ Оплачен",
    "fulfilled": "🎉 Выполнен",
    "cancelled": "❌ Отменён",
}


async def _update_order_status(
    message: Message,
    orders_api: OrdersApi,
    order_id: str,
    new_status: str,
    comment: str | None,
) -> None:
    """Вспомогательная функция для обновления статуса заказа"""
    try:
        await orders_api.update_order_status(
            order_id=order_id,
            new_status=new_status,
            comment=comment,
        )
        
        logger.info(f"Администратор {message.from_user.id if message.from_user else None} изменил статус заказа {order_id} на {new_status}")

    except Exception as e:
        logger.error(f"Ошибка при обновлении статуса заказа {order_id}: {e}", exc_info=True)
        await message.answer(
            "❌ <b>Ошибка</b>\n\n"
            "Произошла ошибка при обновлении статуса заказа."
        )


@router.callback_query(lambda c: c.data and c.data.startswith("admin:status:confirm:"))
async def admin_status_confirm_no_comment(
    callback: CallbackQuery,
    state: FSMContext,
    orders_api: OrdersApi,
    settings: Settings,
):
    """Подтверждение изменения статуса без комментария"""
    # Проверяем, что это админский чат
    if callback.message and callback.message.chat.id != settings.admin_chat_id:
        await _safe_callback_answer(callback, "❌ Эта команда доступна только администраторам")
        return
    
    data_parts = callback.data.split(":")
    if len(data_parts) < 5:
        await _safe_callback_answer(callback, "❌ Ошибка: неверный формат данных")
        return
    
    # Сразу отвечаем на callback, чтобы не было таймаута
    await _safe_callback_answer(callback)
    
    order_id = data_parts[3]
    new_status = data_parts[4]
    
    # Обновляем статус заказа без комментария
    await _update_order_status(
        callback.message,
        orders_api,
        order_id,
        new_status,
        comment=None,
    )
    await state.clear()


@router.callback_query(lambda c: c.data and c.data.startswith("admin:status:"))
async def admin_change_status_start(
    callback: CallbackQuery,
    state: FSMContext,
    settings: Settings,
):
    """Начало процесса изменения статуса заказа администратором"""
    # Проверяем, что это админский чат
    if callback.message and callback.message.chat.id != settings.admin_chat_id:
        await _safe_callback_answer(callback, "❌ Эта команда доступна только администраторам")
        return
    
    data_parts = callback.data.split(":")
    if len(data_parts) < 3:
        await _safe_callback_answer(callback, "❌ Ошибка: неверный формат данных")
        return
    
    action = data_parts[2]
    
    if action == "cancel":
        # Отмена изменения статуса
        order_id = data_parts[-1]
        await state.clear()
        await _safe_callback_answer(callback, "❌ Изменение статуса отменено")
        return
    
    if action == "select":
        # Выбор статуса
        if len(data_parts) < 5:
            await _safe_callback_answer(callback, "❌ Ошибка: неверный формат данных")
            return
        
        order_id = data_parts[3]
        new_status = data_parts[4]
        
        await state.update_data(order_id=order_id, new_status=new_status)
        await state.set_state(AdminOrderStatusStates.waiting_comment)
        
        status_name = STATUS_NAMES.get(new_status, new_status)
        await callback.message.answer(
            f"✏️ <b>Изменение статуса заказа #{order_id}</b>\n\n"
            f"Выбран статус: {status_name}\n\n"
            "Введите комментарий или нажмите кнопку ниже, чтобы пропустить:",
            reply_markup=admin_status_comment_keyboard(order_id, new_status)
        )
        await _safe_callback_answer(callback)
        return
    
    # Начало процесса - показываем клавиатуру выбора статуса
    order_id = data_parts[-1]
    await state.update_data(order_id=order_id)
    await state.set_state(AdminOrderStatusStates.waiting_status)
    
    await callback.message.answer(
        f"✏️ <b>Изменение статуса заказа #{order_id}</b>\n\n"
        "Выберите новый статус заказа:",
        reply_markup=admin_order_status_keyboard(order_id)
    )
    await _safe_callback_answer(callback)


@router.message(AdminOrderStatusStates.waiting_comment)
async def admin_status_comment(
    message: Message,
    state: FSMContext,
    orders_api: OrdersApi,
    settings: Settings,
):
    """Обработка комментария при изменении статуса заказа"""
    # Проверяем, что это админский чат
    if message.chat.id != settings.admin_chat_id:
        await state.clear()
        return
    
    data = await state.get_data()
    order_id = data.get("order_id")
    new_status = data.get("new_status")
    
    if not order_id or not new_status:
        await message.answer("❌ <b>Ошибка</b>\n\nДанные о заказе не найдены")
        await state.clear()
        return
    
    # Получаем комментарий
    comment = message.text.strip() if message.text else None
    if not comment:
        comment = None
    
    # Обновляем статус заказа
    await _update_order_status(
        message,
        orders_api,
        order_id,
        new_status,
        comment,
    )
    
    await state.clear()

