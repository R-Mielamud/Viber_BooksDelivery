# Generated by Django 3.1.4 on 2021-01-05 13:07

import BooksDelivery.model_fields.json
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0004_auto_20210104_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='viberuser',
            name='convers_answers_data',
            field=BooksDelivery.model_fields.json.OrderedJSONField(default='{}'),
        ),
    ]
