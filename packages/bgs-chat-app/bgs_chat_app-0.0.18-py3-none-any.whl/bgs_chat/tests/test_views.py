from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from rest_framework.response import Response
from django.core.cache import cache
from unittest.mock import patch, AsyncMock
import asyncio
import pytest
from bgs_chat_app.views import init_conversation, send_message, get_messages
from ..common.fern import Fern
from ..common.api_calls import POLLING_INTERVAL


@pytest.mark.django_db
def test_init_generates_token_and_id():
    """
    Checks that the views init_conversation generates a (mocked) token and
    conversation id;
    Checks that a conversation key is generated and stored in session against
    a hashed conversation key
    """
    factory = RequestFactory()
    request = factory.get('/chat')

    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    with patch('bgs_chat_app.common.api_calls.DirectLineAPI.get_token_and_conversation_id', return_value = {
            'conversation_id': 'test_conversation_id',
            'token': 'test_token',
        }
    ):
        init_conversation(request)

    # this is the hashed conversation key
    assert 'conversation_key' in request.session.keys()
    decrypted_key = Fern.decrypt(request.session['conversation_key'])
    bot_info = cache.get(f'chat_bot_{decrypted_key}')
    assert bot_info['conversation_id'] == 'test_conversation_id'
    assert bot_info['token'] == 'test_token'


@pytest.mark.django_db
def test_send_message():
    """
    Test that bot.send_message a message returns ({'status': 'message sent'})
    """
    factory = RequestFactory()
    request = factory.post('/chat', data={"message": "This is a message"}, content_type="application/json")

    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    with patch('bgs_chat_app.common.api_calls.DirectLineAPI.get_token_and_conversation_id', return_value={
            'conversation_id': 'test_conversation_id',
            'token': 'test_token',
        }), \
        patch('bgs_chat_app.common.api_calls.DirectLineAPI.send_message', return_value={
            'status': 'message sent'
            }):
        init_conversation(request)
    res = send_message(request)
    assert res.status_code == 200
    assert res.data['status'] == "message sent"


@pytest.mark.django_db
@pytest.mark.asyncio
def test_get_message():
    """
    Test that get_response returns a response from the bot
    """
    factory = RequestFactory()
    request = factory.get('/chat')
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    with patch('bgs_chat_app.common.api_calls.DirectLineAPI.start_conversation') as mock_start, \
        patch('bgs_chat_app.common.api_calls.DirectLineAPI.send_message') as mock_send, \
        patch('bgs_chat_app.common.api_calls.DirectLineAPI.get_response', new_callable=AsyncMock) as mock_get_response:

        mock_start.return_value = {"conversation_id": 'fake-id'}
        mock_send.return_value = None
        mock_get_response.side_effect = [
            asyncio.sleep(POLLING_INTERVAL),
            "Hello, how can I help you today?"
        ]

    response = get_messages(request)

    assert response.status_code == 400
    assert response.data['error'] == 'No active conversation found'

# def test_send_message_no_credentials
"""
Test that a message sent with no credentials returns the expected error message
"""


# @pytest.mark.django_db
# def test_send_message_throttled(settings):
#     """
#     Test that bot.send_message throttling is working correctly
#     """
#     # assert 0
#     settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["anon"] = "1/hour"
#     factory = RequestFactory()
#     request = factory.post('/chat', data={"message": "This is a message"}, content_type="application/json")

#     middleware = SessionMiddleware(lambda req: None)
#     middleware.process_request(request)
#     request.session.save()
#     with patch('bgs_chat_app.common.api_calls.DirectLineAPI.get_token_and_conversation_id', return_value={
#             'conversation_id': 'test_conversation_id',
#             'token': 'test_token',
#         }), \
#         patch('bgs_chat_app.common.api_calls.DirectLineAPI.send_message', return_value={
#             'status': 'message sent'
#             }):
#         init_conversation(request)
#     # # Check the first message sends correctly
#     res = send_message(request)
#     assert res.status_code == 200
#     assert res.data['status'] == "message sent"

#     new_request = factory.post('/chat', data={"message": "This is another message"}, content_type="application/json")
#     middleware.process_request(new_request)
#     new_request.session.save()
#     with patch('bgs_chat_app.common.api_calls.DirectLineAPI.get_token_and_conversation_id', return_value={
#             'conversation_id': 'test_conversation_id',
#             'token': 'test_token',
#         }), \
#         patch('bgs_chat_app.common.api_calls.DirectLineAPI.send_message', return_value={
#             'status': 'message sent'
#             }):
#         init_conversation(new_request)
#     res_2 = send_message(new_request)

#     assert res_2.status_code == 429

#     settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["anon"] = "100/hr"