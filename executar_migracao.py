#!/usr/bin/env python3
"""
Script para executar migração de reposição via Python
Executa o SQL de migração no Oracle
"""

import oracledb
import os

# Configuração do Oracle Client
try:
    oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient_23_5")
except Exception as e:
    print(f"Oracle Client já inicializado ou erro: {e}")

# Credenciais do banco
DB_USER = "dbasistemas"
DB_PASSWORD = "dbasistemas"
DB_DSN = "172.19.0.250:1521/prdamevo"

# Ler o script SQL
script_path = "/app/migration_reposicao_quantidade.sql"

print("=" * 80)
print("MIGRAÇÃO: Reposição de Itens - SIM/NÃO para Quantidades")
print("=" * 80)
print(f"\nLendo script: {script_path}")

try:
    with open(script_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    print(f"✓ Script carregado ({len(sql_content)} caracteres)")

except FileNotFoundError:
    print(f"✗ ERRO: Arquivo não encontrado: {script_path}")
    exit(1)

# Conectar ao banco
print(f"\nConectando ao Oracle: {DB_DSN}")

try:
    connection = oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN
    )
    print("✓ Conectado com sucesso!")

except Exception as e:
    print(f"✗ ERRO ao conectar: {e}")
    exit(1)

# Processar e executar o SQL
cursor = connection.cursor()

# Dividir em statements individuais (separados por ;)
# Remover comentários de bloco /* */
import re
sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)

# Separar statements
statements = []
current_statement = []

for line in sql_content.split('\n'):
    # Ignorar comentários de linha
    if line.strip().startswith('--'):
        continue

    # Ignorar linhas vazias
    if not line.strip():
        continue

    current_statement.append(line)

    # Se linha termina com ;, é fim de statement
    if line.strip().endswith(';'):
        stmt = '\n'.join(current_statement).strip()
        if stmt and stmt != ';':
            statements.append(stmt.rstrip(';'))
        current_statement = []

print(f"\n✓ {len(statements)} comandos SQL encontrados")
print("\n" + "=" * 80)
print("EXECUTANDO MIGRAÇÃO...")
print("=" * 80 + "\n")

# Executar cada statement
executed = 0
errors = 0

for i, stmt in enumerate(statements, 1):
    # Mostrar apenas primeiras 60 caracteres
    preview = stmt.replace('\n', ' ')[:60] + "..."

    try:
        # Verificar se é SELECT
        if stmt.strip().upper().startswith('SELECT'):
            cursor.execute(stmt)
            rows = cursor.fetchall()

            print(f"[{i}/{len(statements)}] SELECT executado:")

            # Mostrar resultados
            if rows:
                for row in rows[:10]:  # Mostrar até 10 linhas
                    print(f"  → {row}")
                if len(rows) > 10:
                    print(f"  ... e mais {len(rows) - 10} linhas")
            else:
                print("  → Nenhum resultado")
        else:
            # Executar DDL/DML
            cursor.execute(stmt)

            # Verificar se afetou linhas
            if cursor.rowcount > 0:
                print(f"[{i}/{len(statements)}] ✓ {cursor.rowcount} linhas afetadas")
            else:
                print(f"[{i}/{len(statements)}] ✓ Executado")

        executed += 1

    except Exception as e:
        print(f"[{i}/{len(statements)}] ✗ ERRO: {e}")
        print(f"  Statement: {preview}")
        errors += 1

        # Se erro crítico, parar
        if "invalid" in str(e).lower() or "does not exist" in str(e).lower():
            print("\n⚠️  ERRO CRÍTICO - Parando execução")
            break

print("\n" + "=" * 80)
print("RESUMO DA MIGRAÇÃO")
print("=" * 80)
print(f"Total de comandos: {len(statements)}")
print(f"Executados com sucesso: {executed}")
print(f"Erros: {errors}")

if errors == 0:
    print("\n✓ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")

    # Fazer COMMIT final
    connection.commit()
    print("✓ COMMIT realizado")
else:
    print(f"\n⚠️  Migração concluída com {errors} erro(s)")
    print("⚠️  Recomenda-se revisar os erros acima")

    # Perguntar se quer fazer commit
    print("\nDeseja fazer COMMIT mesmo assim? (digite 'sim' para confirmar)")
    # Note: em produção, melhor não fazer commit se houver erros

# Fechar conexão
cursor.close()
connection.close()

print("\n✓ Conexão fechada")
print("=" * 80)
