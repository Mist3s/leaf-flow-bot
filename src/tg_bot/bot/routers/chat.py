from __future__ import annotations

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from tg_bot.bot.states import OrderChatStates
from tg_bot.services.support_service import SupportService
from tg_bot.services.chat_service import ChatService

router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith("chat:order:"))
async def start_order_chat(callback: CallbackQuery, state: FSMContext):
    order_id = callback.data.split(":")[-1]
    await state.update_data(order_id=order_id)
    await state.set_state(OrderChatStates.waiting_message)
    await callback.message.answer(
        f"Вы пишете по заказу №{order_id}.\nОтправьте сообщение (можно текст, фото, файл и т.д.)"
    )
    await callback.answer()


@router.message(OrderChatStates.waiting_message)
async def relay_order_chat(message: Message, state: FSMContext, support_service: SupportService):
    data = await state.get_data()
    order_id = data.get("order_id")
    await support_service.forward_support(message, order_id=order_id)
    await message.answer(f"Ваше сообщение по заказу №{order_id} отправлено оператору.")
    await state.clear()


@router.callback_query(lambda c: c.data and c.data.startswith("reply:"))
async def process_reply_callback(callback: CallbackQuery, chat_service: ChatService):
    await chat_service.handle_reply_callback(callback)


@router.message()
async def catch_admin_replies(message: Message, chat_service: ChatService):
    handled = await chat_service.maybe_forward_admin_reply(message)
    if handled:
        return
