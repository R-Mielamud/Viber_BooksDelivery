from BooksDelivery import settings
from django.http import JsonResponse

def check_api_key_middleware(get_response):
    def middleware(request):
        if request.path.startswith("/api"):
            authorization = request.headers.get("Authorization")
            
            if authorization != settings.API_KEY:
                return JsonResponse({
                    "message": "Invalid credential",
                }, status=403)

            return get_response(request)

    return middleware
