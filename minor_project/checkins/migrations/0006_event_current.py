# Generated by Django 3.1.7 on 2021-10-28 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkins', '0005_auto_20211026_1140'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='current',
            field=models.BooleanField(default=False, null=True),
        ),
    ]