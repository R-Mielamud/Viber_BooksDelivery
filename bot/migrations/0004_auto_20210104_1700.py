# Generated by Django 3.1.4 on 2021-01-04 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_auto_20210104_1227'),
    ]

    operations = [
        migrations.RenameField(
            model_name='viberuser',
            old_name='viber_id',
            new_name='messenger_id',
        ),
        migrations.AddField(
            model_name='viberuser',
            name='messenger',
            field=models.CharField(default='Viber', max_length=20),
        ),
    ]
