from django.db.models import *
from BooksDelivery.model_fields.json import OrderedJSONField
from BooksDelivery.base import BaseCSVModel

class Dated(Model):
    created_at = DateField(auto_now=True)

class Requisites(Dated):
    delivery_phone = CharField(max_length=20, default="+000000000000")
    delivery_name = CharField(max_length=100, default="")
    post_service = CharField(max_length=300, default="")
    delivery_address = CharField(max_length=300, default="")

    def __str__(self):
        return "{} ({}) by {} to {}".format(
            self.delivery_name,
            self.delivery_phone,
            self.post_service,
            self.delivery_address,
        )

class ViberUser(Model, BaseCSVModel):
    messenger_id = CharField(max_length=50, default="1234567890A==")
    messenger = CharField(max_length=20, default="Viber")
    phone = CharField(max_length=20, blank=True, null=True)
    requisites = OneToOneField(Requisites, on_delete=CASCADE, blank=True, null=True)
    convers_answers_data = OrderedJSONField(default="{}")

    def __str__(self):
        return "{} through {}".format(self.phone, self.messenger)

    @classmethod
    def csv_schema(cls):
        return {
            "id": "ID",
            "messenger": "Messenger",
            "messenger_id": "ID in messenger database",
            "phone": "Phone number",
            "requisites.id": "Requisites ID",
            "requisites.delivery_name": "Delivery name",
            "requisites.delivery_phone": "Delivery phone",
            "requisites.post_service": "Post service",
            "requisites.delivery_address": "Delivery address",
        }

class Order(Dated, BaseCSVModel):
    books = JSONField(default=list)
    user = ForeignKey(to=ViberUser, on_delete=CASCADE, related_name="orders", blank=True, null=True)

    def __str__(self):
        return "Order by {}".format(self.user.phone)

    @classmethod
    def arrays_newline(cls):
        return True

    @classmethod
    def csv_schema(cls):
        return {
            "id": "ID",
            "user.phone": "User phone number",
            "user.messenger": "Messenger",
            "books": "Books"
        }

class Bill(Dated, BaseCSVModel):
    amount = CharField(max_length=100, default="")
    comment = TextField(max_length=500, default="")
    user = ForeignKey(to=ViberUser, on_delete=CASCADE, related_name="bills", blank=True, null=True)

    def __str__(self):
        return "{} by {}".format(self.amount, self.user.phone)

    @classmethod
    def csv_schema(cls):
        return {
            "id": "ID",
            "amount": "Amount",
            "comment": "Comment",
            "user.phone": "User phone number",
            "user.messenger": "Messenger",
        }
