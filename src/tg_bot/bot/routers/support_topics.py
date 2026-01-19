import logging

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tg_bot.bot.states import SupportStates, OrderChatStates, AdminOrderStatusStates
from tg_bot.config import Settings
from tg_bot.services.support_topics_service import SupportTopicsService

logger = logging.getLogger(__name__)
router = Router()

# Тексты кнопок меню, которые не должны пересылаться в поддержку
MENU_TEXTS = {
    "📦 Мои заказы",
    "👨‍💻 Поддержка",
    "🛒 Открыть приложение",
}

# Команды, которые не должны пересылаться в поддержку
COMMANDS = {"/start", "/help", "/orders", "/support"}


def is_command(text: str | None) -> bool:
    """Проверяет, является ли текст командой"""
    if not text:
        return False
    text = text.strip()
    return text.startswith("/") and text.split()[0].lower() in COMMANDS


def is_menu_text(text: str | None) -> bool:
    """Проверяет, является ли текст текстом кнопки меню"""
    return text in MENU_TEXTS


@router.message(
    F.chat.type == ChatType.PRIVATE,  # Только личные сообщения
)
async def forward_user_message_to_topic(
    message: Message,
    state: FSMContext,
    support_topics_service: SupportTopicsService,
):
    """
    Catch-all хендлер для пересылки сообщений пользователя в топик поддержки.
    
    Этот хендлер должен быть подключён последним, чтобы не ломать существующие FSM/команды.
    """
    logger.debug(
        f"Получено личное сообщение от {message.from_user.id if message.from_user else None}: "
        f"{message.text[:50] if message.text else 'не текст'}"
    )
    
    # Игнорируем сообщения в FSM состояниях (они обрабатываются другими хендлерами)
    current_state = await state.get_state()
    if current_state in (SupportStates.waiting_message, OrderChatStates.waiting_message):
        logger.debug(f"Игнорируем сообщение в FSM состоянии: {current_state}")
        return

    # Проверка на команды
    if message.text and is_command(message.text):
        logger.debug(f"Игнорируем команду: {message.text}")
        return

    # Проверка на тексты меню
    if message.text and is_menu_text(message.text):
        logger.debug(f"Игнорируем текст меню: {message.text}")
        return

    logger.info(f"Пересылаем сообщение пользователя {message.from_user.id if message.from_user else None} в топик")
    await support_topics_service.forward_user_to_topic(message)


@router.message()
async def forward_admin_message_to_user(
    message: Message,
    state: FSMContext,
    support_topics_service: SupportTopicsService,
    settings: Settings,
):
    """
    Хендлер для пересылки сообщений админа из топика пользователю в личку.
    """
    if message.chat.id != settings.admin_chat_id:
        return
    
    if not message.message_thread_id:
        return
    
    # Игнорируем сообщения в FSM состояниях изменения статуса
    current_state = await state.get_state()
    if current_state in (AdminOrderStatusStates.waiting_status, AdminOrderStatusStates.waiting_comment):
        logger.debug(f"Игнорируем сообщение администратора в FSM состоянии: {current_state}")
        return
    
    logger.debug(
        f"Получено сообщение в топике: chat_id={message.chat.id}, "
        f"thread_id={message.message_thread_id}, admin_chat_id={settings.admin_chat_id}"
    )

    logger.info(f"Пересылаем сообщение админа из топика {message.message_thread_id} пользователю")
    await support_topics_service.forward_admin_to_user(message)

