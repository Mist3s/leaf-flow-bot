from __future__ import annotations

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from tg_bot.bot.states import OrderChatStates
from tg_bot.services.support_topics_service import SupportTopicsService

router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith("chat:order:"))
async def start_order_chat(
    callback: CallbackQuery, 
    state: FSMContext,
    support_topics_service: SupportTopicsService,
):
    """Начало чата по заказу - используем систему топиков"""
    order_id = callback.data.split(":")[-1]
    await state.update_data(order_id=order_id)
    await state.set_state(OrderChatStates.waiting_message)
    
    # Уведомляем администратора о том, что пользователь нажал кнопку "Чат по заказу"
    if callback.from_user:
        user_fullname = callback.from_user.full_name
        await support_topics_service.notify_admin_about_order_chat(
            user_telegram_id=callback.from_user.id,
            user_fullname=user_fullname,
            order_id=order_id,
        )
    
    await callback.message.answer(
        f"💬 <b>Чат по заказу #{order_id}</b>\n\n"
        "Отправьте сообщение (текст, фото, файл и т.д.) — мы передадим его оператору.\n\n"
        "Ожидаю ваше сообщение... 👇"
    )
    await callback.answer()


@router.message(OrderChatStates.waiting_message)
async def relay_order_chat(
    message: Message,
    state: FSMContext,
    support_topics_service: SupportTopicsService,
):
    """Пересылка сообщения по заказу в топик поддержки"""
    data = await state.get_data()
    order_id = data.get("order_id")
    await support_topics_service.forward_user_to_topic(message, order_id=order_id)
    await message.answer(
        f"✅ <b>Сообщение отправлено</b>\n\n"
        f"Ваше сообщение по заказу #{order_id} передано оператору. Ответ придёт в этот чат."
    )
    await state.clear()