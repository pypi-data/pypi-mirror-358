from bgs_chat_app.bgs_chat.common.api_calls import DirectLineAPI
import json
import datetime
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response
import uuid
from django.core.cache import cache
from bgs_chat_app.bgs_chat.common.serializers import serialize_datetime, deserialize_datetime
from bgs_chat_app.bgs_chat.common.fern import Fern


def index(request):
    init_conversation()
    return {'message': 'Conversation started'}

@api_view(['POST'])
def init_conversation(request):
    """
    Initialise the chatbot, generate a conversation_id and individual token.
    Generate a conversation_key to reference the conversation_id and token.
    Cache the conversation_id and token so it is isolated from the front end.
    """
    print('*'*30)
    print('VIEWS/INIT_CONVERSATION')
    print('*'*30)
    bot = DirectLineAPI()
    token_and_id = bot.get_token_and_conversation_id()
    conversation_key = str(uuid.uuid4())
    # cache the token_and_id against a uuid conversation_key

    cache.set(f'chat_bot_{conversation_key}', token_and_id, timeout=3600)
    # hash the conversation key before saving to session
    hashed = Fern.encrypt(conversation_key)
    request.session['conversation_key'] = hashed
    bot.conversation_id = token_and_id['conversation_id']
    bot._token = token_and_id['token']
    bot.start_conversation()
    request.session.modified = True
    return Response({'text': 'Token successfully generated'}, status=200)


def get_bot_info(hashed_conversation_key):
    conversation_key = Fern.decrypt(hashed_conversation_key)
    if conversation_key is None:
        return Response({"error": "Error decrypting conversation key, please contact support"})
    return cache.get(f'chat_bot_{conversation_key}')


# We may want to reset this as an api_view...
# @api_view(['POST'])
def refresh_token(request):
    hashed_conversation_key = request.session.get('conversation_key')
    if not hashed_conversation_key:
        init_conversation(request)

    bot_info = get_bot_info(hashed_conversation_key)
    if not bot_info:
        request.session['conversation_key'] = None

        return Response({"error": "Bot info not found, conversation key deleted. Please start a new conversation"}, status=400)

    bot = DirectLineAPI(
        token=bot_info['token'],
        conversation_id=bot_info['conversation_id']
    )

    res = bot.refresh_token()
    if res['status_code'] == 200:
        conversation_key = Fern.decrypt(hashed_conversation_key)
        cache.set(f'chat_bot_{conversation_key}', res['token_and_id'], timeout=3600)
        return Response({"error": "Token refreshed, your new token is valid for one hour"}, status=200)
    else:
        return Response({"error": f"Could not refresh token {res['status_code']} - {res['content']}"}, status=400)


@api_view(['POST'])
@throttle_classes([AnonRateThrottle])
def send_message(request):
    print('*'*30)
    print('BGS_CHAT_APP/VIEWS.PY SEND_MESSAGE')
    print('*'*30)
    hashed_conversation_key = request.session.get('conversation_key')

    if not hashed_conversation_key:
        init_conversation(request)
        hashed_conversation_key = request.session.get('conversation_key')

    bot_info = get_bot_info(hashed_conversation_key)

    if not bot_info:
        request.session['conversation_key'] = None
        init_conversation(request)
        hashed_conversation_key = request.session.get('conversation_key')
        bot_info = get_bot_info(hashed_conversation_key)
        bot = DirectLineAPI(
            token=bot_info['token'],
            conversation_id=bot_info['conversation_id'],
        )
        bot.start_conversation()

    message = json.loads(request.body.decode('utf-8')).get("message")

    if not message:
        return Response({"error": "Missing message"})

    last_message_sent_at = request.session.get('last_message_sent_timestamp', datetime.datetime.now(datetime.timezone.utc)) or datetime.datetime.now(datetime.timezone.utc)

    bot = DirectLineAPI(
        token=bot_info['token'],
        conversation_id=bot_info['conversation_id'],
        last_message_sent_timestamp=last_message_sent_at,
    )

    bot.send_message(message)
    request.session['last_message_sent_timestamp'] = serialize_datetime(last_message_sent_at)
    request.session.modified = True

    return Response({'status': 'message sent'})


@api_view(['GET'])
def get_messages(request):
    hashed_conversation_key = request.session.get('conversation_key')

    if not hashed_conversation_key:
        return Response({"error": "No active conversation found"}, status=400)

    bot_info = get_bot_info(hashed_conversation_key)

    if not bot_info:
        # NOTE: If there's no bot info for get_response, we should prompt the
        # user to re-enter their question/raise an error
        return Response({"error": "Bot info not found"}, status=400)

    last_message_sent_at = deserialize_datetime(request.session['last_message_sent_timestamp'])
    watermark = request.session.get('watermark', None)

    bot = DirectLineAPI(
        token=bot_info['token'],
        conversation_id=bot_info['conversation_id'],
        last_message_sent_timestamp=last_message_sent_at,
        watermark=watermark
    )
    response_info = bot.get_response()
    request.session['watermark'] = bot.watermark

    request.session.modified = True
    # import pdb; pdb.set_trace()
    return Response({"text": response_info['text']}, status=status.HTTP_200_OK)