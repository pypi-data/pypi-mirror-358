"""
API calls for interacting with the BGS chat
"""
import asyncio
import requests
from django.conf import settings
#import bgs_chat_site.settings as bgs_settings
import datetime
from dateutil import parser


DIRECT_LINE_URL = settings.DIRECT_LINE_URL
CONVERSATION_URL = 'https://directline.botframework.com/v3/directline/conversations'
POLLING_INTERVAL = 5
"""
shell commands
from bgs_chat_app.common.api_calls import DirectLineAPI
bot = DirectLineAPI()
token_and_id = bot.get_token_and_conversation_id()
currently not getting DIRECT_LINE_URL, manually set using export DIRECT_LINE_URL='....'
bot.start_conversation()
bot.send_message('test')
bot.get_response()
"""


class DirectLineAPI(object):
    def __init__(self, token=None, conversation_id=None, watermark=None, last_message_sent_timestamp=None):
        self._token = token
        self.conversation_id = conversation_id
        self.watermark = watermark
        self.last_message_sent_timestamp = last_message_sent_timestamp
        self.last_message_received_timestamp = None
        self.headers = {
            "Content-Type": "application/json"
        }

    @staticmethod
    def get_token_and_conversation_id():
        """
        Get token and conversation ID.
        This does not start a conversation.
        """
        url = DIRECT_LINE_URL
        res = requests.get(url)
        res.raise_for_status()
        if res.status_code == 200:
            json_res = res.json()

            return {
                "conversation_id": json_res['conversationId'],
                'token': json_res['token']
            }
        else:
            return res.status_code

    def refresh_token(self):
        """
        Refreshing a token requires the original token to still be valid.
        A prompt on the front end should be added for this.
        If the conversation/token expires, the conversation cannot (currently)
        be 'reactivated'
        """
        print('*'*30)
        print('REFRESH_TOKEN')
        url = 'https://directline.botframework.com/v3/directline/tokens/refresh'
        res = requests.post(url, headers=self.headers, json={'conversationId': self.conversation_id})
        # import pdb; pdb.set_trace()
        if res.status_code == 200:
            json_res = res.json()
            if self.conversation_id != json_res['conversationId']:
                return "Error refreshing token, conversation IDs do not match"
            self._token = json_res['token']
            print('SUCCESS')
            print('*'*30)
            return {
                "status_code": res.status_code,
                "token_and_id": {
                    "conversation_id": self.conversation_id,
                    'token': json_res['token']
                },
            }
        else:
            print('FAILED')
            print('*'*30)
            return {
                "status_code": res.status_code,
                "content": res.content
            }

    def start_conversation(self):
        """
        Start a conversation using the generated conversationId and token
        """
        print('*'*80)
        print('START CONVERSATION')
        if not self.conversation_id:
            # NOTE: we can't regenerate conversation id here as it won't be
            # saved to cache
            return {
                "error": "Failed to start conversation, no conversation id"
            }
        payload = {
            "type": "event",
            "name": "startConversation"
        }
        self.headers.update(
            {"Authorization": f"Bearer {self._token}"}
        )
        url = CONVERSATION_URL
        res = requests.post(url, headers=self.headers, json=payload)
        if res.status_code == 201:
            print('SUCCESS')
            print('*'*80)
            return {
                "conversation_id": self.conversation_id
            }
        else:
            print('FAILED')
            print('*'*80)
            return {
                "error": f"Failed to start conversation, {res.status_code} - {res.content}"
            }

    def send_message(self, text):
        """
        Send a message
        """
        if self.conversation_id is None:
            # NOTE: we can't regenerate conversation id here as it won't be
            # saved to cache
            return {
                "error": "Failed to start conversation, no conversation id"
            }

        url = '/'.join([CONVERSATION_URL, self.conversation_id, 'activities'])

        payload = {
            'type': 'message',
            'text': text
        }
        self.headers.update(
            {"Authorization": f"Bearer {self._token}"}
        )
        res = requests.post(url, headers=self.headers, json=payload)

        if res.status_code == 200:
            print('*******************')
            print('** MESSAGE SENT **')
            print(f'** {text} **')
            print('*******************')
            return res
        else:
            return {
                "error": f"Failed to send message, {res.status_code} - {res.content}"
            }

    def _poll_for_response(self):
        url = '/'.join([
            CONVERSATION_URL,
            self.conversation_id,
            'activities',
            f'?watermark {self.watermark}' if self.watermark else ''
        ])
        self.headers.update(
            {"Authorization": f"Bearer {self._token}"}
        )
        res = requests.get(url, headers=self.headers)
        bot_responses = []
        if res.status_code == 200:
            json_res = res.json()
            self.watermark = json_res.get('watermark', self.watermark)
            activities = json_res['activities']
            try:
                last_message = next(
                    activity for activity in reversed(activities)
                    if activity['type'] == 'message'
                    and activity['from'].get('role') == 'bot'
                    )
                deserialized_datetime = parser.isoparse(last_message['timestamp'])

                last_message_details = {
                    'status_code': res.status_code,
                    'timestamp': deserialized_datetime,
                    'text': last_message['text'],
                }

                self.last_message_received_timestamp = deserialized_datetime
                bot_responses.append(last_message_details)
                return last_message_details

            except StopIteration:
                return {"text": "No response found"}

        return bot_responses

    def get_response(self):
        """
        get_response runs an async loop over _poll_for_response
        until self.last_message_received_timestamp is greater than
        self.last_message_sent_timestamp
        """
        # reset the last_message_received timestamp to None to ignore old
        # messages
        self.last_message_received_timestamp = None
        # check if we have message sent timestamp. If not, use current time
        if self.last_message_sent_timestamp is None:
            self.last_message_sent_timestamp = datetime.datetime.now(datetime.timezone.utc)

        async def poll_for_latest_response():
            while True:
                bot_responses = self._poll_for_response()
                if self.last_message_received_timestamp is not None and self.last_message_received_timestamp > self.last_message_sent_timestamp:
                    self.last_message_sent_timestamp = None
                    self.last_message_received_timestamp = None
                    print('*'*30)
                    print('GET_RESPONSE CRITERIA MET')
                    print(f'{bot_responses}')
                    print('*'*30)
                    return bot_responses
                await asyncio.sleep(POLLING_INTERVAL)

        return asyncio.run(poll_for_latest_response())