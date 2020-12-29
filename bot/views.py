from django.views import View
from django.http import HttpResponse
from .models import ViberUser, Order, Requisites, Bill
from helpers.conversation import Conversation, ACTION, ACTION_TEXT
from viberbot.api.messages.text_message import TextMessage

from helpers.bot import (
    init_bot,
    verify_sig,
    get_request,
    get_request_type,
    send_text,
    REQ_SUBSCRIBTION,
    REQ_UNSUBSCRIBTION,
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
            "id": "fruit",
            "action": "choice_question",
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

conversations = {}

class WebHook(View):
    def post(self, request):
        data = request.body
        sig_header = request.headers.get("X-Viber-Content-Signature", None)
        sig_query = request.GET.get("sig", None)
        sig = sig_header or sig_query or ""

        if not verify_sig(bot, data, sig):
            return HttpResponse(status=FORBIDDEN)

        bot_request = get_request(bot, data)
        request_type = get_request_type(bot_request)

        if request_type == REQ_SUBSCRIBTION:
            user = bot_request.get_user
            print(user.__dict__)
            uid = user.id
            phone = user.phone_number
            ViberUser.objects.create(phone=phone)

            conversations[uid] = Conversation(manifest)
            question = conversations[uid].get_next_question()

            while question:
                send_text(bot, uid, question["text"])

                if question[ACTION] != ACTION_TEXT:
                    break

                question = conversations[uid].get_next_question()
        elif request_type == REQ_UNSUBSCRIBTION:
            user = bot_request.get_user
            phone = user.phone_number
            ViberUser.objects.delete(phone=phone)
        elif request_type == REQ_MESSAGE:
            message = bot_request.message

            if isinstance(message, TextMessage):
                text = message.text
                user = bot_request.sender
                uid = user.id
                phone = user.phone_number
                user = ViberUser.objects.filter(phone=phone).first()

                if not conversations.get(uid):
                    if user:
                        if user.convers_answers_data:
                            answers = user.convers_answers_data

                            conversations[uid] = Conversation(
                                manifest,
                                start_from_id=list(answers.keys())[-1],
                                default_answers_data=answers
                            )

                question = conversations[uid].get_next_question(text)

                while question:
                    send_text(question)

                    if question[ACTION] != ACTION_TEXT:
                        user.convers_answers_data = conversations[uid].answers
                        user.save()
                        break

                    question = conversations[uid].get_next_question(text)

                if not question:
                    # TODO: save answers data
                    user.convers_answers_data = {}
                    user.save()
                    conversations[uid] = Conversation(manifest)

        return HttpResponse(status=200)
