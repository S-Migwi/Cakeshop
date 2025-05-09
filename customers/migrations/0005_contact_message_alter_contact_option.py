# Generated by Django 5.0.7 on 2024-12-06 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0004_contact_delete_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='message',
            field=models.TextField(default=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='option',
            field=models.CharField(choices=[('1', 'Order an accessory'), ('2', 'Order a cake'), ('3', 'Request baker information')], max_length=255),
        ),
    ]
