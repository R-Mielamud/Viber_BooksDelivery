from django.db.models import *

class Dated(Model):
    created_at = DateField(auto_now=True)

class Order(Dated):
    books = JSONField(default=list)

class Requisites(Dated):
    delivery_phone = CharField(max_length=20, default="+000000000000")
    delivery_name = CharField(max_length=100, default="")
    post_service = CharField(max_length=300, default="")
    delivery_address = CharField(max_length=300, default="")

class Bill(Dated):
    amount = CharField(max_length=100, default="")
    comment = TextField(max_length=500, default="")

class ViberUser(Model):
    phone = CharField(max_length=20, default="+000000000000")
    orders = ForeignKey(Order, on_delete=CASCADE, related_name="user", default=[])
    requisites = OneToOneField(Requisites, on_delete=CASCADE, blank=True, null=True)
    bills = ForeignKey(Bill, on_delete=CASCADE, related_name="user", default=[])
    convers_answers_data = JSONField(blank=True, null=True)
