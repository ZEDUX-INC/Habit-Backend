# Generated by Django 3.2.2 on 2022-04-12 17:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0002_alter_customuser_managers"),
    ]

    operations = [
        migrations.RenameField(
            model_name="customuser",
            old_name="dob",
            new_name="date_of_birth",
        ),
    ]
