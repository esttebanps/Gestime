# Generated by Django 4.1.6 on 2023-03-10 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('managementime', '0013_alter_tiempojuego_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tiempojuego',
            name='is_active',
            field=models.BooleanField(),
        ),
    ]
