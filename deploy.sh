#!/bin/bash

echo "=========================================="
echo "  Deploy - Sistema de Registro de Limpeza"
echo "=========================================="
echo ""

# Atualiza o código do repositório
echo "[1/6] Atualizando código do repositório..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Erro ao fazer git pull. Abortando deploy."
    exit 1
fi

echo "✅ Código atualizado com sucesso!"
echo ""

# Para os containers
echo "[2/6] Parando containers..."
docker-compose down

if [ $? -ne 0 ]; then
    echo "⚠️  Aviso: Erro ao parar containers (talvez não estejam rodando)"
fi

echo "✅ Containers parados!"
echo ""

# Rebuild da imagem
echo "[3/6] Reconstruindo imagem Docker..."
docker-compose build --no-cache

if [ $? -ne 0 ]; then
    echo "❌ Erro ao construir imagem. Abortando deploy."
    exit 1
fi

echo "✅ Imagem construída com sucesso!"
echo ""

# Sobe os containers
echo "[4/6] Iniciando containers..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Erro ao iniciar containers. Abortando deploy."
    exit 1
fi

echo "✅ Containers iniciados!"
echo ""

# Aguarda o container ficar pronto
echo "[5/6] Aguardando container ficar pronto..."
sleep 5

# Executa migrations
echo "[6/6] Executando migrations e coletando arquivos estáticos..."
docker-compose exec -T web python manage.py migrate --noinput
docker-compose exec -T web python manage.py collectstatic --noinput

if [ $? -ne 0 ]; then
    echo "⚠️  Aviso: Erro ao executar migrations/collectstatic"
fi

echo ""
echo "=========================================="
echo "✅ Deploy concluído com sucesso!"
echo "=========================================="
echo ""
echo "📊 Status dos containers:"
docker-compose ps
echo ""
echo "🌐 Aplicação disponível em: http://localhost:8000"
