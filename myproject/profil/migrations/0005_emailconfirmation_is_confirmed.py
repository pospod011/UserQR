# Generated by Django 5.2.1 on 2025-05-25 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profil', '0004_remove_emailconfirmation_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailconfirmation',
            name='is_confirmed',
            field=models.BooleanField(default=False),
        ),
    ]
