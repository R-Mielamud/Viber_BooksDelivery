from django.db.models import *
from BooksDelivery.model_fields.json import OrderedJSONField

class Dated(Model):
    created_at = DateField(auto_now=True)

class Requisites(Dated):
    delivery_phone = CharField(max_length=20, default="+000000000000")
    delivery_name = CharField(max_length=100, default="")
    post_service = CharField(max_length=300, default="")
    delivery_address = CharField(max_length=300, default="")

class ViberUser(Model):
    viber_id = CharField(max_length=50, default="1234567890A==")
    phone = CharField(max_length=20, blank=True, null=True)
    requisites = OneToOneField(Requisites, on_delete=CASCADE, blank=True, null=True)
    convers_answers_data = OrderedJSONField(default="\{\}")

class Order(Dated):
    books = JSONField(default=list)
    user = ForeignKey(to=ViberUser, on_delete=CASCADE, related_name="orders", blank=True, null=True)

class Bill(Dated):
    amount = CharField(max_length=100, default="")
    comment = TextField(max_length=500, default="")
    user = ForeignKey(to=ViberUser, on_delete=CASCADE, related_name="bills", blank=True, null=True)
