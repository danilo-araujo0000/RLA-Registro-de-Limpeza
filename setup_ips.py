import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'higiene_project.settings')
django.setup()

from django.contrib.auth.models import User
from registro.models import IPPermitido

# Criar superusuário se não existir
if not User.objects.using('default').filter(username='admin').exists():
    User.objects.db_manager('default').create_superuser('admin', 'admin@admin.com', 'admin')
    print('✓ Superusuário "admin" criado com senha "admin"')
else:
    print('✓ Superusuário "admin" já existe')

# Adicionar localhost aos IPs permitidos
ip, created = IPPermitido.objects.using('default').get_or_create(
    ip_address='127.0.0.1',
    defaults={'descricao': 'Localhost', 'ativo': True}
)

if created:
    print('✓ IP 127.0.0.1 (Localhost) adicionado aos IPs permitidos')
else:
    print('✓ IP 127.0.0.1 (Localhost) já existe nos IPs permitidos')

print('\nPronto! Acesse /admin com:')
print('  Usuário: admin')
print('  Senha: admin')
