#!/bin/bash


# Para os containers existentes
echo "[1/4] Parando containers existentes..."
docker-compose down

echo "✅ Containers parados!"
echo ""

# Remove a imagem antiga
echo "[2/4] Removendo imagem antiga..."
docker rmi higiene-web 2>/dev/null || echo "⚠️  Nenhuma imagem antiga encontrada"

echo ""

# Rebuild da imagem sem cache
echo "[3/4] Construindo nova imagem (sem cache)..."
docker-compose build --no-cache

if [ $? -ne 0 ]; then
    echo "❌ Erro ao construir imagem. Abortando."
    exit 1
fi

echo "✅ Imagem construída com sucesso!"
echo ""

# Sobe os containers
echo "[4/4] Iniciando containers..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Erro ao iniciar containers. Abortando."
    exit 1
fi

echo "✅ Containers iniciados!"
echo ""

# Aguarda o container ficar pronto
echo "Aguardando container ficar pronto..."
sleep 5

# Executa migrations e collectstatic
echo "Executando migrations e coletando arquivos estáticos..."
docker-compose exec -T web python manage.py migrate --noinput
docker-compose exec -T web python manage.py collectstatic --noinput

echo ""
echo "=========================================="
echo "✅ Build concluído com sucesso!"
echo "=========================================="
echo ""
echo "📊 Status dos containers:"
docker-compose ps
echo ""
echo "🌐 Aplicação disponível em: http://localhost:8000"
echo ""
echo "💡 Comandos úteis:"
echo "   - Ver logs: docker-compose logs -f"
echo "   - Reiniciar: docker-compose restart"
echo "   - Parar: docker-compose down"
