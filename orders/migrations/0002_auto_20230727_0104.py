# Generated by Django 3.1 on 2023-07-26 19:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='emsil',
            new_name='email',
        ),
    ]