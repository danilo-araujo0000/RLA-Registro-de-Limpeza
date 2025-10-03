import oracledb
import json
from dotenv import load_dotenv
import os
from datetime import datetime
import shutil
from log import Logger


oracledb.init_oracle_client(lib_dir=r"c:/instantclient_23_7")

load_dotenv()

usuario = os.getenv("usuario")
senha = os.getenv("senha")
host = os.getenv("host")
porta = os.getenv("porta")
service_name = os.getenv("service_name")

dsn = oracledb.makedsn(host, porta, service_name=service_name)


logger = Logger("logs/logs.log")

def coletar_dados(pacientes):
    try:
        conexao = oracledb.connect(user=usuario, password=senha, dsn=dsn)
        cursor = conexao.cursor()

        lista_pacientes = pacientes
        
        dados_pacientes = {}

        for codigo in lista_pacientes:
            query = """
            SELECT DISTINCT 
                CD_PACIENTE_INTEGRA, 
                NM_PACIENTE, 
                TO_CHAR(DT_AGENDA, 'YYYY-MM-DD') AS DT_AGENDA, 
                DS_UNIDADE_SOLICITANTE, 
                DS_ITEM_AGENDA, 
                DS_ESPECIALIDADE,
                CD_TIPO_PLANTAO_INTEGRA
            FROM 
                mvintegra.IMV_AGENDAMENTO
            WHERE 
                CD_PACIENTE_INTEGRA = :codigo
                
            """
            logger.log(f"Iniciando coleta de dados para o paciente {codigo}")
            cursor.execute(query, {"codigo": codigo})
            resultados = cursor.fetchall()

            if resultados:
                cd_paciente = resultados[0][0]
                
                nm_paciente = None
                for row in resultados:
                    if row[1] is not None and row[1].strip():
                        nm_paciente = row[1]
                        logger.log(f"Nome válido encontrado para paciente {codigo}: {nm_paciente}")
                        break
                
                if nm_paciente is None:
                    nm_paciente = "Não encontrado"
                    logger.log(f"Nome do paciente não encontrado para o código {codigo}, usando valor padrão")
                
                dados_pacientes[cd_paciente] = {
                    "NM_PACIENTE": nm_paciente,
                    "CD_PACIENTE_INTEGRA": cd_paciente,
                    "AGENDAMENTOS": []
                }

                agendamentos_unicos = set()
                datas_retorno = []
                for row in resultados:
                    agendamento = (
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                        row[6]
                    )

                    if agendamento not in agendamentos_unicos:
                        agendamentos_unicos.add(agendamento)
                        if row[6] == "R":
                            if row[2]:
                                datas_retorno.append(row[2])
                        
                        dados_pacientes[cd_paciente]["AGENDAMENTOS"].append({
                            "DT_AGENDA": row[2] if row[2] else None,
                            "DS_UNIDADE_SOLICITANTE": row[3] if row[3] else "Não especificada",
                            "DS_ITEM_AGENDA": row[4] if row[4] else "Não especificado",
                            "DS_ESPECIALIDADE": row[5] if row[5] else "Não especificada",
                            "CD_TIPO_PLANTAO_INTEGRA": row[6] if row[6] else None
                        })

                if len(datas_retorno) == 1:
                    dados_pacientes[cd_paciente]["DATA_RETORNO"] = list(datas_retorno)[0]
                elif len(datas_retorno) > 1:
                    logger.log(f"Mais de um retorno encontrado para o paciente {codigo}")
                    dados_pacientes[cd_paciente]["DATA_RETORNO"] = "Mais de um retorno encontrado"
                else:
                    logger.log(f"Nenhum retorno encontrado para o paciente {codigo}")
                    dados_pacientes[cd_paciente]["DATA_RETORNO"] = "Nenhum retorno encontrado"

        cursor.close()
        conexao.close()

        data_arquivo = "data/dados_pacientes.json"
        
        if os.path.exists(data_arquivo):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_arquivo = f"data/dados_pacientes_{timestamp}.json"
            
            os.rename(data_arquivo, backup_arquivo)
            logger.log(f"Arquivo original renomeado para: {backup_arquivo}")
        
        with open(data_arquivo, "w", encoding="utf-8") as arquivo_json:
            json.dump(dados_pacientes, arquivo_json, ensure_ascii=False, indent=4)
        print(f"✅ Novos dados coletados e salvos em '{data_arquivo}' com sucesso!")
        logger.log(f"✅ Novos dados coletados e salvos em '{data_arquivo}' com sucesso!")

    except oracledb.DatabaseError as e:
        erro, = e.args
        logger.log(f"❌ Erro ao conectar ou executar query: {erro.message}")
        print(f"❌ Erro ao conectar ou executar query: {erro.message}")

if __name__ == "__main__":
    coletar_dados(['4650793'])