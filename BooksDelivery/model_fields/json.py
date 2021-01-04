from django.db.models import TextField
from django.core import exceptions
import json

class OrderedJSONField(TextField):
    description = "Ordered JSON dict or list. Stored as text."

    default_error_messages = {
        "invalid": "Value must be valid JSON.",
    }

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def get_prep_value(self, value):
        if value is None:
            return value

        return json.dumps(value)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)

        try:
            json.dumps(value)
        except TypeError:
            raise exceptions.ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={'value': value},
            )
