"""
TODO
from unittest.mock import patch, Mock, AsyncMock
import pytest

from ui_backend.commands import start

@pytest.mark.asyncio
async def test_star():
    # Создайте моки
    mock_get_user = AsyncMock(return_value=None)
    mock_create_user = AsyncMock()

    message = Mock()
    message.from_user.id = 123
    message.chat.id = 456
    message.from_user.first_name = "Andrei"
    message.from_user.username = "Andrei4Some"

    with patch("src.db.queries.get_user_by_telegram_user_id", mock_get_user), \
         patch("src.db.queries.create_user", mock_create_user), \
         patch("telegram.Bot.send_message", new_callable=AsyncMock) as mock_send_message:

        await start(message)

    # Проверьте, что функции были вызваны с правильными аргументами
    mock_get_user.assert_called_once_with(telegram_user_id=123)
    mock_create_user.assert_called_once_with(telegram_user_id=123, telegram_chat_id=456, telegram_username="john_doe")
    mock_send_message.assert_called()  # Дополнительные проверки на аргументы можно добавить сюда
"""