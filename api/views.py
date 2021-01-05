from django.http import JsonResponse
from rest_framework.viewsets import ModelViewSet
from bot.models import ViberUser, Order, Requisites, Bill
from api.serializers import UserSerializer, OrderSerializer, RequisitesSerializer, BillSerializer

class UserDependingAPIView(ModelViewSet):
    def user_including_request(self, request, action):
        data = request.data
        user_id = data.pop("user", None)
        user = ViberUser.objects.filter(pk=user_id).first()
        result = action(user, data)
        serializer = self.serializer_class(result)
        return JsonResponse(serializer.data)

class UserAPIView(ModelViewSet):
    queryset = ViberUser.objects.all()
    serializer_class = UserSerializer

class OrderAPIView(UserDependingAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request):
        action = lambda user, data: self.queryset.create(**data, user=user)
        return self.user_including_request(request, action)

    def get_update_action(self, pk):
        def action(user, data):
            order_set = self.queryset.filter(pk=pk)
            res = order_set.update(**data, user=user)
            return order_set.first()

        return action

    def update(self, request, pk):
        return self.user_including_request(request, self.get_update_action(pk))

    def partial_update(self, request, pk, **kwargs):
        return self.user_including_request(request, self.get_update_action(pk))

class RequisitesAPIView(ModelViewSet):
    queryset = Requisites.objects.all()
    serializer_class = RequisitesSerializer

class BillAPIView(UserDependingAPIView):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer

    def create(self, request):
        action = lambda user, data: self.queryset.create(**data, user=user)
        return self.user_including_request(request, action)

    def get_update_action(self, pk):
        def action(user, data):
            order_set = self.queryset.filter(pk=pk)
            res = order_set.update(**data, user=user)
            return order_set.first()

        return action

    def update(self, request, pk):
        return self.user_including_request(request, self.get_update_action(pk))

    def partial_update(self, request, pk, **kwargs):
        return self.user_including_request(request, self.get_update_action(pk))
