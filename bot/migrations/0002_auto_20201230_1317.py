# Generated by Django 3.1.4 on 2020-12-30 13:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='viberuser',
            name='bills',
        ),
        migrations.RemoveField(
            model_name='viberuser',
            name='orders',
        ),
        migrations.AddField(
            model_name='bill',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bills', to='bot.viberuser'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='bot.viberuser'),
        ),
    ]
