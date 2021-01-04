from django.views import View
from django.http import HttpResponse
from .models import ViberUser, Order, Requisites, Bill
from helpers.conversation import Conversation, ACTION, ACTION_TEXT
from viberbot.api.messages.text_message import TextMessage
from helpers.conversation import ConversationsStorage, Conversation

from helpers.bot import (
    init_bot,
    verify_sig,
    get_request,
    get_request_type,
    send_text,
    REQ_CHAT,
    REQ_MESSAGE,
    REQ_UNKNOWN
)

FORBIDDEN = 403
bot = init_bot()

manifest = {
    "conversation": [
        {
            "id": "hello",
            "action": "text",
            "text": "Hello!"
        },
        {
            "id": "how_help",
            "action": "text_question",
            "text": "How can I help you?"
        },
        {
            "id": "vegetables_text",
            "action": "text",
            "text": "What vegetables do you like?"
        },
        {
            "id": "vegetables",
            "action": "list_question",
            "text": "Vegetable ",
            "start_number": 1,
            "stop_command": "000"
        },
        {
            "id": "fruit",
            "action": "choices_question",
            "text": "What do you like?\nIf apples, enter 1;\nIf lemons, enter 2\niIf carrots, enter 3",
            "choices": {
                "1": "apple",
                "2": "lemon",
                "3": "carrot"
            },
            "on_choices": {
                "apple": [{
                    "id": "apple",
                    "action": "text",
                    "text": "I like them too!"
                }],
                "lemon": [{
                    "id": "lemon",
                    "action": "text",
                    "text": "I eat them only with sugar."
                }],
                "carrot": [{
                    "id": "carrot",
                    "action": "text",
                    "text": "But they're not tasty!"
                }]
            },
            "on_invalid_choice": "If apples, enter 1;\nIf lemons, enter 2\niIf carrots, enter 3"
        },
        {
            "id": "bye",
            "action": "text",
            "text": "Bye!"
        }
    ],
    "stop_command": "STOP"
}

conversations_storage = ConversationsStorage()

class WebHook(View):
    def success(self):
        return HttpResponse(status=200)

    def send_until_question(self, send, conversation, prev_answer):
        question = conversation.get_next_question(prev_answer)

        while question:
            send(question.text)

            if not question.skip:
                break

            question = conversation.get_next_question(prev_answer)

        return conversation, question

    def post(self, request):
        data = request.body
        sig_header = request.headers.get("X-Viber-Content-Signature", None)
        sig_query = request.GET.get("sig", None)
        sig = sig_header or sig_query or ""

        if not verify_sig(bot, data, sig):
            return HttpResponse(status=FORBIDDEN)

        bot_request = get_request(bot, data)
        request_type = get_request_type(bot_request)

        if request_type == REQ_CHAT:
            request_user = bot_request.user
            uid = request_user.id
            user, created = ViberUser.objects.get_or_create(viber_id=uid)

            if not created:
                user.phone = None
                user.save()

            send_text(bot, uid, "Welcome to fruit bot! Enter your phone number:")
        elif request_type == REQ_MESSAGE:
            message = bot_request.message

            if not isinstance(message, TextMessage):
                return self.success()

            text = message.text
            prev_answer = text
            request_user = bot_request.sender
            uid = request_user.id
            user = ViberUser.objects.filter(viber_id=uid).first()

            if not user:
                user = ViberUser.objects.create(viber_id=uid, phone=text)
                prev_answer = None
            elif not user.phone:
                user.phone = text
                user.convers_answers_data = {}
                user.save()
                prev_answer = None

            send = lambda text: send_text(bot, uid, text)

            if not conversations_storage.exists(uid):
                conversations_storage.add(uid, manifest, default_answers=user.convers_answers_data)

            conversation = conversations_storage.get(uid)
            conversation, question = self.send_until_question(send, conversation, prev_answer)

            if (not question) or conversation.answers.stopped:
                user.convers_answers_data = {}
                user.save()
                conversation, _ = self.send_until_question(send, Conversation(manifest), None)
            elif not question.skip:
                user.convers_answers_data = conversation.answers.data
                user.save()

            conversations_storage.set(uid, conversation)

        return self.success()
