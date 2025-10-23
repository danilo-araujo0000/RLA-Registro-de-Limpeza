#!/bin/bash

echo "🔄 Atualizando código do repositório..."
git pull origin main

echo "🔄 Resetando para main..."
git reset --hard main/main

echo "🔄 Reiniciando container..."
docker-compose restart

echo "✅ Atualização concluída!"
echo "🌐 Aplicação disponível em: http://localhost:8005"
