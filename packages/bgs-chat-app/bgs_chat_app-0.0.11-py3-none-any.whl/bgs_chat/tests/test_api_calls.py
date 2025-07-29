import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from ..common.api_calls import DirectLineAPI, POLLING_INTERVAL


@pytest.mark.asyncio
async def test_get_response_polls_for_response():
    """Test that the chatbot's get_response calls poll_for_response until a
    message is returned"""
    # mock poll_for_response
    async def mock_poll_for_response():
        await asyncio.sleep(5)
        return ["Bot response"]

    with patch("bgs_chat_app.common.api_calls.DirectLineAPI.get_response", new_callable=AsyncMock) as mock_polling:
        mock_polling.side_effect = mock_poll_for_response

        bot = DirectLineAPI()
        response = await bot.get_response()
        assert response == ["Bot response"]
        assert mock_polling.call_count >= 1


@pytest.mark.asyncio
async def test_get_response():
    """
    Tests the start/send/receive message conversation flow.
    Here we spoof the response rather than recreating poll_for_response again
    as it's tested above
    """
    with patch('bgs_chat_app.common.api_calls.DirectLineAPI.start_conversation') as mock_start, \
        patch('bgs_chat_app.common.api_calls.DirectLineAPI.send_message') as mock_send, \
        patch('bgs_chat_app.common.api_calls.DirectLineAPI.get_response', new_callable=AsyncMock) as mock_get_response:

        mock_start.return_value = {"conversation_id": 'fake-id'}
        mock_send.return_value = None
        mock_get_response.side_effect = [
            asyncio.sleep(POLLING_INTERVAL),
            "Hello, how can I help you today?"
        ]
        bot = DirectLineAPI()
        bot.start_conversation()
        bot.send_message('hello')
        # the first call to get_response returns the co-routine
        await bot.get_response()
        r2 = await bot.get_response()
        mock_start.assert_called_once()
        mock_send.assert_called_once()

        assert r2 == "Hello, how can I help you today?"
        assert mock_get_response.call_count == 2


def test_get_token_and_conversation_id():
    with patch('bgs_chat_app.common.api_calls.DirectLineAPI.get_token_and_conversation_id') as mock_get_token_and_conversation_id:
        mock_get_token_and_conversation_id.return_value = {
            'conversation_id': 'test_conversation_id',
            'token': 'test_token',
            }
        bot = DirectLineAPI()
        res = bot.get_token_and_conversation_id()
        assert res['token'] == 'test_token'
        assert res['conversation_id'] == 'test_conversation_id'


def test_send_message_no_conversation_id():
    """
    Tests the start/send/receive message conversation flow.
    Here we spoof the response rather than recreating poll_for_response again
    as it's tested above
    """
    with patch('bgs_chat_app.common.api_calls.DirectLineAPI.send_message') as mock_send:

        mock_send.return_value = "Failed to start conversation, no conversation id"

        bot = DirectLineAPI()

        bot.send_message('hello')