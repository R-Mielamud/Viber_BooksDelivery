from rest_framework.serializers import ModelSerializer
from bot.models import ViberUser, Order, Requisites, Bill
from BooksDelivery.model_fields.json import OrderedJSONFieldSerializer

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
    convers_answers_data = OrderedJSONFieldSerializer(required=False)

    class Meta:
        model = ViberUser
        fields = "__all__"

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
