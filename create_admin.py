#!/usr/bin/env python
import os
import sys
import django

# Django ayarlarını yükle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sozumsoz.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin():
    try:
        # Check if user already exists
        if User.objects.filter(username='alidoganbektas@gmail.com').exists():
            print('Admin kullanıcısı zaten mevcut!')
            return

        # Create superuser
        user = User.objects.create_superuser(
            username='alidoganbektas@gmail.com',
            email='alidoganbektas@gmail.com',
            password='admin123',
            first_name='Ali',
            last_name='Doğan'
        )
        print('Admin kullanıcısı başarıyla oluşturuldu!')
        print(f'Kullanıcı adı: {user.username}')
        print(f'E-posta: {user.email}')
        print(f'İsim: {user.get_full_name()}')

    except Exception as e:
        print(f'Hata: {e}')

if __name__ == '__main__':
    create_admin()
