# Generated by Django 2.2.10 on 2020-10-12 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_user_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_img',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='app/'),
        ),
    ]