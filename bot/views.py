from django.views import View
from django.http import HttpResponse

from helpers.bot import (
    init_bot,
    verify_sig,
    get_request,
    get_request_type,
    send_text,
    REQ_SUBSCRIBTION,
    REQ_MESSAGE,
    REQ_UNKNOWN
)

FORBIDDEN = 403
bot = init_bot()

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
            uid = user.id
            send_text(bot, uid, "Thank you for subscribing!")
        elif request_type == REQ_MESSAGE:
            user = bot_request.sender
            uid = user.id
            send_text(bot, uid, "Hello!")

        return HttpResponse(status=200)
