#!/usr/bin/env python

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'higiene_project.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME' )
email = os.environ.get('DJANGO_SUPERUSER_EMAIL' )
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f'usuario "{username}" criado com sucesso!')
    print(f'usuario: {username}')
    print(f'Password: {password}')
else:
    print(f' o usuario "{username}" já existe.')