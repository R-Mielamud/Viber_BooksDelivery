from django.http import JsonResponse
from django.views import View
from rest_framework.viewsets import ModelViewSet
from bot.models import ViberUser, Order, Requisites, Bill
from BooksDelivery.base import BaseCSVExportAPI

from api.serializers import (
    GetUserSerializer, ModUserSerializer,
    GetOrderSerializer, ModOrderSerializer,
    GetBillSerializer, ModBillSerializer,
    RequisitesSerializer
)

class UserAPIView(ModelViewSet):
    queryset = ViberUser.objects.all()

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return GetUserSerializer
        else:
            return ModUserSerializer

class OrderAPIView(ModelViewSet):
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return GetOrderSerializer
        else:
            return ModOrderSerializer

class RequisitesAPIView(ModelViewSet):
    queryset = Requisites.objects.all()
    serializer_class = RequisitesSerializer

class BillAPIView(ModelViewSet):
    queryset = Bill.objects.all()

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return GetBillSerializer
        else:
            return ModBillSerializer

class GetUserByMessengerIdAPI(View):
    def get(self, request, **kwargs):
        messenger_id = kwargs.get("messenger_id")
        user = ViberUser.objects.filter(messenger_id=messenger_id).first()

        if not user:
            return JsonResponse({
                "detail": "Not found."
            }, status=404)

        serializer = GetUserSerializer(user)
        return JsonResponse(serializer.data)

class UserCSVExport(BaseCSVExportAPI):
    model = ViberUser

class BillCSVExport(BaseCSVExportAPI):
    model = Bill

class OrderCSVExport(BaseCSVExportAPI):
    model = Order
