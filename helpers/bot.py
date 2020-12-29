from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.viber_requests import ViberMessageRequest, ViberConversationStartedRequest, ViberUnsubscribedRequest
from viberbot.api.messages.text_message import TextMessage
from BooksDelivery import settings

REQ_CHAT = "chat_started"
REQ_UNSUBSCRIBTION = "unsubscribtion"
REQ_MESSAGE = "message"
REQ_UNKNOWN = "unknown"

def init_bot():
    config = BotConfiguration(
        name="Books delivery",
        avatar="",
        auth_token=settings.BOT_TOKEN
    )

    bot = Api(config)
    return bot

def verify_sig(bot, data, sig):
    return bot.verify_signature(data, sig)

def get_request(bot, data):
    return bot.parse_request(data)

def get_request_type(request):
    if isinstance(request, ViberConversationStartedRequest):
        return REQ_CHAT
    elif isinstance(request, ViberMessageRequest):
        return REQ_MESSAGE
    elif isinstance(request, ViberUnsubscribedRequest):
        return REQ_UNSUBSCRIBTION

    return REQ_UNKNOWN

def send_messages(bot, uid, messages):
    return bot.send_messages(uid, messages)

def text_message(text):
    return TextMessage(text=text)

def send_text(bot, uid, text):
    message = text_message(text)
    return send_messages(bot, uid, [message])
