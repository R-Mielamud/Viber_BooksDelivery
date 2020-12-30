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

conversations = {}

class WebHook(View):
    def success(self):
        return HttpResponse(status=200)

    def send_until_question(self, bot, uid, user, prev_answer):
        question = conversations[uid].get_next_question(prev_answer)

        while question:
            send_text(bot, uid, question["text"])

            if not question["skip"]:
                if conversations[uid].answers["stopped"]:
                    user.convers_answers_data = {}
                    user.save()
                    conversations[uid] = Conversation(manifest)
                    return send_until_question(bot, uid, user, prev_answer)
                else:
                    user.convers_answers_data = conversations[uid].answers["data"]
                    user.save()
                    break

            question = conversations[uid].get_next_question(prev_answer)

        if not question:
            return True

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
            user = bot_request.user
            uid = user.id
            ViberUser.objects.get_or_create(viber_id=uid)
            send_text(bot, uid, "Welcome to fruit bot! Enter your phone number:")
        elif request_type == REQ_MESSAGE:
            message = bot_request.message

            if not isinstance(message, TextMessage):
                return self.success()

            text = message.text
            prev_answer = text
            user = bot_request.sender
            uid = user.id
            user = ViberUser.objects.filter(viber_id=uid).first()

            if not user:
                user = ViberUser.objects.create(viber_id=uid, phone=text)
                prev_answer = None
            elif not user.phone:
                user.phone = text
                user.save()
                prev_answer = None

            if not conversations.get(uid) and user.convers_answers_data is not None:
                answers = user.convers_answers_data
                keys = list(answers.keys())

                conversations[uid] = Conversation(
                    manifest,
                    start_from_id=keys[-1] if len(keys) > 0 else None,
                    default_answers_data=answers
                )

            finished_convers = self.send_until_question(bot, uid, user, prev_answer)

            if finished_convers:
                # TODO: save answers data

                user.convers_answers_data = {}
                user.save()
                conversations[uid] = Conversation(manifest)
                self.send_until_question(bot, uid, user, None)

        return self.success()
