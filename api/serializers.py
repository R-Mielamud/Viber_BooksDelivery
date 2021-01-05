from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
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

class GetUserSerializer(ModelSerializer):
    requisites = RequisitesSerializer(allow_null=True, required=False)
    convers_answers_data = OrderedJSONFieldSerializer(required=False)

    class Meta:
        model = ViberUser
        fields = "__all__"

class ModUserSerializer(ModelSerializer):
    requisites = PrimaryKeyRelatedField(allow_null=True, required=False, queryset=Requisites.objects.all())
    convers_answers_data = OrderedJSONFieldSerializer(required=False)

    class Meta:
        model = ViberUser
        fields = "__all__"

class GetOrderSerializer(ModelSerializer):
    user = MinimalUserSerializer()

    class Meta:
        model = Order
        fields = "__all__"

class ModOrderSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(queryset=ViberUser.objects.all())

    class Meta:
        model = Order
        fields = "__all__"

class GetBillSerializer(ModelSerializer):
    user = MinimalUserSerializer()

    class Meta:
        model = Bill
        fields = "__all__"

class ModBillSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(queryset=ViberUser.objects.all())

    class Meta:
        model = Bill
        fields = "__all__"
