# Generated by Django 4.1.3 on 2022-11-15 08:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("test_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="RelationalChild",
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
                ("text", models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name="RelationalParent",
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
                ("done", models.BooleanField(default=True)),
                (
                    "many_to_many",
                    models.ManyToManyField(
                        related_name="many_to_many", to="test_app.relationalchild"
                    ),
                ),
                (
                    "one_to_one",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="one_to_one",
                        to="test_app.relationalchild",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ForiegnChild",
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
                ("text", models.CharField(max_length=1000)),
                (
                    "parent",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="test_app.relationalparent",
                    ),
                ),
            ],
        ),
    ]
