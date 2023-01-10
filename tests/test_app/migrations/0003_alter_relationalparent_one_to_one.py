# Generated by Django 4.1.3 on 2023-01-10 00:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("test_app", "0002_relationalchild_relationalparent_foriegnchild"),
    ]

    operations = [
        migrations.AlterField(
            model_name="relationalparent",
            name="one_to_one",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="one_to_one",
                to="test_app.relationalchild",
            ),
        ),
    ]
