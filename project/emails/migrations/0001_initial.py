# Generated by Django 5.0.7 on 2024-07-22 05:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="EmailAccount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("password", models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name="EmailMessage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("subject", models.CharField(max_length=255)),
                ("send_date", models.DateTimeField()),
                ("received_date", models.DateTimeField()),
                ("body", models.TextField()),
                ("attachments", models.JSONField(default=list)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="emails.emailaccount",
                    ),
                ),
            ],
        ),
    ]
