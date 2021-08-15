# Generated by Django 3.2.6 on 2021-08-15 06:10

import account.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False, unique=True)),
                ('username', models.CharField(max_length=50, unique=True)),
                ('is_active', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('full_name', models.CharField(blank=True, max_length=50)),
                ('image', models.ImageField(default='pr.jpg', upload_to='profile')),
                ('activation_code', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', account.models.UserManager()),
            ],
        ),
    ]
