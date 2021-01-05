from rest_framework.viewsets import ModelViewSet
from bot.models import ViberUser, Order, Requisites, Bill
from api.serializers import UserSerializer, OrderSerializer, RequisitesSerializer, BillSerializer

class UserAPIView(ModelViewSet):
    queryset = ViberUser.objects.all()
    serializer_class = UserSerializer

class OrderAPIView(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class RequisitesAPIView(ModelViewSet):
    queryset = Requisites.objects.all()
    serializer_class = RequisitesSerializer

class BillAPIView(ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
