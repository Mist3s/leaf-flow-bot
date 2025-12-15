from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from tg_bot.bot.keyboards.reply import main_menu
from tg_bot.services.user_service import UserService
from tg_bot.api_client.orders import OrdersApi
from tg_bot.api_client.users import UsersApi
from tg_bot.api_client.models import RegisterUserRequest
from tg_bot.config import Settings

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def start_command(message: Message, settings: Settings, users_api: UsersApi, orders_api: OrdersApi, user_service: UserService):
    if not message.from_user:
        await message.answer("Ошибка: не удалось определить пользователя")
        return
    
    # Пытаемся получить существующего пользователя
    user_profile = await users_api.get_by_telegram(message.from_user.id)

    # Если пользователь не найден, регистрируем его
    if not user_profile:
        try:
            # Получаем фото профиля, если доступно
            photo_url = None
            try:
                photos = await message.bot.get_user_profile_photos(message.from_user.id, limit=1)
                if photos.total_count > 0 and photos.photos:
                    # Используем file_id самого большого фото
                    photo_url = photos.photos[0][-1].file_id
            except Exception as e:
                logger.debug(f"Не удалось получить фото профиля для пользователя {message.from_user.id}: {e}")
            
            # Создаем запрос на регистрацию
            register_request = RegisterUserRequest(
                telegramId=message.from_user.id,
                firstName=message.from_user.first_name,
                lastName=message.from_user.last_name,
                username=message.from_user.username,
                languageCode=message.from_user.language_code,
                photoUrl=photo_url,
            )
            
            # Регистрируем пользователя
            user_profile = await users_api.register(register_request)
            logger.info(f"Пользователь {message.from_user.id} успешно зарегистрирован")
        except Exception as e:
            logger.error(f"Ошибка при регистрации пользователя {message.from_user.id}: {e}", exc_info=True)
            # Продолжаем работу даже если регистрация не удалась
            text, _ = user_service.greeting_for_unknown(message.from_user.first_name)
            await message.answer(text, reply_markup=main_menu(webapp_url=str(settings.webapp_url)))
            return

    # Получаем заказы пользователя
    orders = await orders_api.list_orders(user_profile.telegramId)
    has_orders = len(orders.items) > 0
    text, _ = user_service.greeting_with_orders(user_profile, has_orders)
    await message.answer(text, reply_markup=main_menu(webapp_url=str(settings.webapp_url)))
