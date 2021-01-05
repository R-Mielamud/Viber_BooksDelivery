from rest_framework.serializers import ModelSerializer
from bot.models import ViberUser, Order, Requisites, Bill

class MinimalUserSerializer(ModelSerializer):
    class Meta:
        model = ViberUser
        fields = ["id", "messenger", "phone"]

class RequisitesSerializer(ModelSerializer):
    class Meta:
        model = Requisites
        fields = "__all__"

class UserSerializer(ModelSerializer):
    requisites = RequisitesSerializer(allow_null=True, required=False)

    class Meta:
        model = ViberUser
        fields = ["id", "messenger", "messenger_id", "phone", "requisites"]

class OrderSerializer(ModelSerializer):
    user = MinimalUserSerializer()

    class Meta:
        model = Order
        fields = "__all__"

class BillSerializer(ModelSerializer):
    user = MinimalUserSerializer()

    class Meta:
        model = Bill
        fields = "__all__"
