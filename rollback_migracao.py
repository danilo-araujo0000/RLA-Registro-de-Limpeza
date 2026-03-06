#!/usr/bin/env python3
"""
Script para fazer ROLLBACK da migração
Restaura valores originais a partir do backup
"""

import oracledb

# Configuração
try:
    oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient_23_5")
except:
    pass

DB_USER = "dbasistemas"
DB_PASSWORD = "dbasistemas"
DB_DSN = "172.19.0.250:1521/prdamevo"

print("=" * 80)
print("ROLLBACK: Revertendo Migração de Reposição")
print("=" * 80)

# Conectar
connection = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
cursor = connection.cursor()

# Restaurar valores
print("\n1. Limpando colunas...")
cursor.execute("UPDATE if_tbl_registro_higiene SET papel_hig = NULL")
cursor.execute("UPDATE if_tbl_registro_higiene SET papel_toalha = NULL")
cursor.execute("UPDATE if_tbl_registro_higiene SET alcool = NULL")
cursor.execute("UPDATE if_tbl_registro_higiene SET sabonete = NULL")
connection.commit()
print("   ✓ Colunas limpas")

# Alterar de volta para VARCHAR
print("\n2. Alterando tipo para VARCHAR2(10)...")
cursor.execute("ALTER TABLE if_tbl_registro_higiene MODIFY papel_hig VARCHAR2(10)")
cursor.execute("ALTER TABLE if_tbl_registro_higiene MODIFY papel_toalha VARCHAR2(10)")
cursor.execute("ALTER TABLE if_tbl_registro_higiene MODIFY alcool VARCHAR2(10)")
cursor.execute("ALTER TABLE if_tbl_registro_higiene MODIFY sabonete VARCHAR2(10)")
print("   ✓ Tipo alterado")

# Restaurar dados originais
print("\n3. Restaurando dados originais...")
cursor.execute("UPDATE if_tbl_registro_higiene SET papel_hig = papel_hig_old")
cursor.execute("UPDATE if_tbl_registro_higiene SET papel_toalha = papel_toalha_old")
cursor.execute("UPDATE if_tbl_registro_higiene SET alcool = alcool_old")
cursor.execute("UPDATE if_tbl_registro_higiene SET sabonete = sabonete_old")
connection.commit()
print("   ✓ Dados restaurados")

print("\n✓ ROLLBACK CONCLUÍDO COM SUCESSO!")
print("✓ Dados retornaram ao estado original (S/N)")

cursor.close()
connection.close()
print("=" * 80)
