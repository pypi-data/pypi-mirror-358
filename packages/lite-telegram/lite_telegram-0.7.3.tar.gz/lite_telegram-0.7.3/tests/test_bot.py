import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from lite_telegram.bot import TelegramBot
from lite_telegram.models import Message, Update


@pytest.fixture
async def bot(mocker: MockerFixture) -> TelegramBot:
    client = mocker.Mock(spec=AsyncClient)
    token = "test-token"
    return TelegramBot(client=client, token=token)


@pytest.mark.asyncio
async def test_get_me(bot: TelegramBot, mocker: MockerFixture) -> None:
    mock_response = {"ok": True, "result": {"id": 123456, "is_bot": True, "first_name": "TestBot"}}
    bot.client.request.return_value.json.return_value = mock_response
    bot.client.request.return_value.is_success = True

    result = await bot.get_me()
    assert result == mock_response["result"]


@pytest.mark.asyncio
async def test_send_message(bot: TelegramBot, mocker: MockerFixture) -> None:
    chat_id = 123456
    text = "Hello, World!"
    mock_response = {"ok": True, "result": {"message_id": 1, "chat": {"id": chat_id, "type": "private"}, "text": text}}
    bot.client.request.return_value.json.return_value = mock_response
    bot.client.request.return_value.is_success = True

    message = await bot.send_message(chat_id, text)
    assert isinstance(message, Message)
    assert message.message_id == 1
    assert message.chat.id == chat_id
    assert message.text == text


@pytest.mark.asyncio
async def test_get_updates(bot: TelegramBot, mocker: MockerFixture) -> None:
    mock_response = {"ok": True, "result": [{"update_id": 1, "message": {"message_id": 1, "chat": {"id": 123456, "type": "private"}, "text": "Hello"}}]}
    bot.client.request.return_value.json.return_value = mock_response
    bot.client.request.return_value.is_success = True

    updates = await bot.get_updates()
    assert isinstance(updates, list)
    assert len(updates) == 1
    assert isinstance(updates[0], Update)
    assert updates[0].update_id == 1
    assert updates[0].message.text == "Hello"
