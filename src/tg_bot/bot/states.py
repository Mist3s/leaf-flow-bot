from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class SupportStates(StatesGroup):
    waiting_message = State()


class OrderChatStates(StatesGroup):
    waiting_message = State()


class AdminOrderStatusStates(StatesGroup):
    waiting_status = State()
    waiting_comment = State()
