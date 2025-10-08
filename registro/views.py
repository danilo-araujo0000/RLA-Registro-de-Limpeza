import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import oracledb
from django.utils import timezone
from datetime import datetime, timedelta
import json
from .decorators import ip_whitelist_required

try:
    instant_client_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..',
        'instantclient-basic-windows.x64-23.7.0.25.01',
        'instantclient_23_7'
    )
    oracledb.init_oracle_client(lib_dir=instant_client_dir)
except oracledb.exceptions.ClientError as e:
    print(f"Error initializing Oracle Client: {e}")


def get_oracle_connection():
    db_config = settings.DATABASES['oracle']
    dsn = oracledb.makedsn(db_config['NAME'].split(':')[0], db_config['NAME'].split(':')[1].split('/')[0], service_name=db_config['NAME'].split('/')[1])
    return oracledb.connect(user=db_config['USER'], password=db_config['PASSWORD'], dsn=dsn)

@ip_whitelist_required()
def redirect_view(request):
    sala_id = request.GET.get('sala', 1)
    return redirect('registro_view', sala_id=sala_id)

@ip_whitelist_required()
def index_view(request, sala_id):
    conn = None
    cursor = None
    sala_data = None
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()
        query = """
            SELECT s.nome_sala, st.nome_setor, st.id_setor
            FROM if_tbl_sala_higiene s
            JOIN if_tbl_setores_higiene st ON s.id_setor = st.id_setor
            WHERE s.id_sala = :id_sala
        """
        cursor.execute(query, id_sala=sala_id)
        result = cursor.fetchone()

        if result:
            id_setor = result[2]
            sala_data = {
                'id_sala': sala_id,
                'nome_sala': result[0],
                'nome_setor': result[1],
                'setor_color': f'setor-color-{(id_setor - 1) % 16}',
            }
        else:
            return render(request, 'error.html', {'message': 'Sala não encontrada!'})

    except oracledb.Error as e:
        error_obj, = e.args
        return render(request, 'error.html', {'message': f"Erro de banco de dados: {error_obj.message}"})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render(request, 'index.html', {'sala': sala_data})

@ip_whitelist_required()
def registro_view(request, sala_id):
    conn = None
    cursor = None
    sala_data = None
    colaboradores = []
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()
        query = """
            SELECT s.nome_sala, st.nome_setor
            FROM if_tbl_sala_higiene s
            JOIN if_tbl_setores_higiene st ON s.id_setor = st.id_setor
            WHERE s.id_sala = :id_sala
        """
        cursor.execute(query, id_sala=sala_id)
        result = cursor.fetchone()

        if result:
            sala_data = {
                'id_sala': sala_id,
                'nome_sala': result[0],
                'nome_setor': result[1],
            }
        else:
            return render(request, 'error.html', {'message': 'Sala não encontrada!'})

        query_colaboradores = """
            SELECT DISTINCT NM_USUARIO
            FROM dbasgu.USUARIOS u
            WHERE u.DS_OBSERVACAO = 'HIGIENE'
            ORDER BY NM_USUARIO
        """
        cursor.execute(query_colaboradores)
        results = cursor.fetchall()

        for row in results:
            nome_completo = row[0]
            if nome_completo:
                primeiro_nome = nome_completo.split()[0]
                colaboradores.append({
                    'primeiro_nome': primeiro_nome,
                    'nome_completo': nome_completo
                })

    except oracledb.Error as e:
        error_obj, = e.args
        return render(request, 'error.html', {'message': f"Erro de banco de dados: {error_obj.message}"})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render(request, 'registro.html', {'sala': sala_data, 'colaboradores': json.dumps(colaboradores)})

@ip_whitelist_required()
def salvar_registro_view(request):
    if request.method == 'POST':
        conn = None
        cursor = None
        try:
            conn = get_oracle_connection()
            cursor = conn.cursor()

            id_sala = request.POST.get('id_sala')
            colaborador_primeiro_nome = request.POST.get('colaborador_primeiro_nome')
            colaborador_completo = request.POST.get('colaborador')
            colaborador = colaborador_primeiro_nome if colaborador_primeiro_nome else colaborador_completo.split()[0] if colaborador_completo else ''
            hora_limpeza = request.POST.get('hora_limpeza')
            id_tipo_limpeza = request.POST.get('tipo_limpeza')

            id_criticidade = request.POST.get('criticidade') if id_tipo_limpeza == '2' else None
            portas = request.POST.get('portas')
            if not portas:
                portas = 'NA'
            teto = request.POST.get('teto')
            if not teto:
                teto = 'NA'
            paredes = request.POST.get('paredes')
            if not paredes:
                paredes = 'NA'
            janelas = request.POST.get('janelas')
            if not janelas:
                janelas = 'NA'
            piso = request.POST.get('piso')
            if not piso:
                piso = 'NA'
            superficie_mobiliario = request.POST.get('superficie_mobiliario')
            if not superficie_mobiliario:
                superficie_mobiliario = 'NA'
            dispenser = request.POST.get('dispenser')
            if not dispenser:
                dispenser = 'NA'

            # Campos de reposição
            papel_hig = request.POST.get('papel_hig')
            if not papel_hig:
                papel_hig = 'NA'
            papel_toalha = request.POST.get('papel_toalha')
            if not papel_toalha:
                papel_toalha = 'NA'
            alcool = request.POST.get('alcool')
            if not alcool:
                alcool = 'NA'
            sabonete = request.POST.get('sabonete')
            if not sabonete:
                sabonete = 'NA'

            obs = request.POST.get('obs')

            sql = """INSERT INTO if_tbl_registro_higiene (
                ID_SALA, COLABORADOR, DATA_LIMPEZA, HORA_LIMPEZA, ID_TIPO_LIMPEZA, OBS,
                PORTAS, TETO, PAREDES, JANELAS, PISO, SUPERFICIE_MOBILIARIO, DISPENSER, ID_CRITICIDADE,
                PAPEL_HIG, PAPEL_TOALHA, ALCOOL, SABONETE
            ) VALUES (
                :id_sala, :colaborador, SYSDATE, :hora_limpeza, :id_tipo_limpeza, :obs,
                :portas, :teto, :paredes, :janelas, :piso, :superficie_mobiliario, :dispenser, :id_criticidade,
                :papel_hig, :papel_toalha, :alcool, :sabonete
            )"""

            cursor.execute(sql, {
                'id_sala': id_sala,
                'colaborador': colaborador,
                'hora_limpeza': hora_limpeza,
                'id_tipo_limpeza': id_tipo_limpeza,
                'obs': obs,
                'portas': portas,
                'teto': teto,
                'paredes': paredes,
                'janelas': janelas,
                'piso': piso,
                'superficie_mobiliario': superficie_mobiliario,
                'dispenser': dispenser,
                'id_criticidade': id_criticidade,
                'papel_hig': papel_hig,
                'papel_toalha': papel_toalha,
                'alcool': alcool,
                'sabonete': sabonete,
            })
            conn.commit()
            return redirect('sucesso_view')

        except oracledb.Error as e:
            error_obj, = e.args
            return render(request, 'error.html', {'message': f"Erro de banco de dados: {error_obj.message}"})
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return redirect('redirect_view')

@ip_whitelist_required()
def sucesso_view(request):
    return render(request, 'sucesso.html')

@ip_whitelist_required()
def salas_view(request):
    conn = None
    cursor = None
    salas = []

    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()

        query = """
            SELECT s.id_sala, s.nome_sala, st.nome_setor, st.id_setor
            FROM if_tbl_sala_higiene s
            JOIN if_tbl_setores_higiene st ON s.id_setor = st.id_setor
            ORDER BY s.id_sala ASC
        """
        cursor.execute(query)
        results = cursor.fetchall()

        for row in results:
            id_setor = row[3]
            salas.append({
                'id_sala': row[0],
                'nome_sala': row[1],
                'nome_setor': row[2],
                'setor_color': f'setor-color-{(id_setor - 1) % 16}',
            })

    except oracledb.Error as e:
        error_obj, = e.args
        return render(request, 'error.html', {'message': f"Erro de banco de dados: {error_obj.message}"})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render(request, 'salas.html', {'salas': salas})

@ip_whitelist_required()
def historico_view(request, sala_id):
    conn = None
    cursor = None
    sala_data = None
    registros = []
    offset = int(request.GET.get('offset', 0))
    limit = 8
    is_ajax = request.GET.get('ajax', '0') == '1'

    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()

        if not is_ajax:
            query_sala = """
                SELECT s.nome_sala, st.nome_setor
                FROM if_tbl_sala_higiene s
                JOIN if_tbl_setores_higiene st ON s.id_setor = st.id_setor
                WHERE s.id_sala = :id_sala
            """
            cursor.execute(query_sala, id_sala=sala_id)
            result = cursor.fetchone()

            if result:
                sala_data = {
                    'id_sala': sala_id,
                    'nome_sala': result[0],
                    'nome_setor': result[1],
                }
            else:
                return render(request, 'error.html', {'message': 'Sala não encontrada!'})

        query_registros = """
            SELECT * FROM (
                SELECT
                    id_registro, colaborador, data_limpeza, hora_limpeza,
                    id_tipo_limpeza, obs, portas, teto, paredes, janelas,
                    piso, superficie_mobiliario, dispenser, id_criticidade,
                    ROW_NUMBER() OVER (ORDER BY data_limpeza DESC, hora_limpeza DESC) as rn
                FROM if_tbl_registro_higiene
                WHERE id_sala = :id_sala
            )
            WHERE rn > :offset AND rn <= :end_row
        """
        cursor.execute(query_registros, {'id_sala': sala_id, 'offset': offset, 'end_row': offset + limit})
        results = cursor.fetchall()

        # Mapeamento de IDs para texto
        tipo_limpeza_map = {1: 'concorrente', 2: 'terminal'}
        criticidade_map = {1: 'crítico', 2: 'semi-crítico', 3: 'não-crítico'}

        for row in results:
            registros.append({
                'id_registro': row[0],
                'colaborador': row[1],
                'data_limpeza': row[2],
                'hora_limpeza': row[3],
                'tipo_limpeza': tipo_limpeza_map.get(row[4], 'concorrente'),
                'obs': row[5],
                'portas': row[6] if row[6] else 'NA',
                'teto': row[7] if row[7] else 'NA',
                'paredes': row[8] if row[8] else 'NA',
                'janelas': row[9] if row[9] else 'NA',
                'piso': row[10] if row[10] else 'NA',
                'superficie_mobiliario': row[11] if row[11] else 'NA',
                'dispenser': row[12] if row[12] else 'NA',
                'criticidade': criticidade_map.get(row[13], ''),
            })

        query_count = """
            SELECT COUNT(*) FROM if_tbl_registro_higiene WHERE id_sala = :id_sala
        """
        cursor.execute(query_count, id_sala=sala_id)
        total = cursor.fetchone()[0]
        has_more = (offset + limit) < total

        if is_ajax:
            html_registros = ""
            for i, registro in enumerate(registros):
                badge_tipo = 'warning' if registro['tipo_limpeza'] == 'terminal' else 'info'

                html_registros += f"""
                <div class="registro-item">
                    <div class="row">
                        <div class="col-md-6">
                            <p><i class="fas fa-user"></i> <strong>Colaborador:</strong> {registro['colaborador']}</p>
                            <p><i class="fas fa-calendar"></i> <strong>Data:</strong> {registro['data_limpeza'].strftime('%d/%m/%Y')} ({['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'][registro['data_limpeza'].weekday()]})</p>
                            <p><i class="fas fa-clock"></i> <strong>Hora:</strong> {registro['hora_limpeza']}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Tipo:</strong>
                                <span class="badge bg-{badge_tipo}">
                                    {registro['tipo_limpeza'].upper()}
                                </span>
                            </p>
                """

                if registro['criticidade']:
                    html_registros += f'<p><i class="fas fa-exclamation-triangle"></i> <strong>Criticidade:</strong> {registro["criticidade"]}</p>'

                html_registros += "</div></div>"

                if registro['tipo_limpeza'] == 'terminal':
                    html_registros += '<div class="mt-3"><strong>Itens Limpos:</strong><div class="d-flex flex-wrap gap-2 mt-2">'

                    if registro['portas'] != 'NA':
                        html_registros += f'<span class="badge badge-{registro["portas"].lower()}">Portas: {registro["portas"]}</span>'
                    if registro['teto'] != 'NA':
                        html_registros += f'<span class="badge badge-{registro["teto"].lower()}">Teto: {registro["teto"]}</span>'
                    if registro['paredes'] != 'NA':
                        html_registros += f'<span class="badge badge-{registro["paredes"].lower()}">Paredes: {registro["paredes"]}</span>'
                    if registro['janelas'] != 'NA':
                        html_registros += f'<span class="badge badge-{registro["janelas"].lower()}">Janelas: {registro["janelas"]}</span>'
                    if registro['piso'] != 'NA':
                        html_registros += f'<span class="badge badge-{registro["piso"].lower()}">Piso: {registro["piso"]}</span>'
                    if registro['superficie_mobiliario'] != 'NA':
                        html_registros += f'<span class="badge badge-{registro["superficie_mobiliario"].lower()}">Superfície: {registro["superficie_mobiliario"]}</span>'
                    if registro['dispenser'] != 'NA':
                        html_registros += f'<span class="badge badge-{registro["dispenser"].lower()}">Dispenser: {registro["dispenser"]}</span>'

                    html_registros += '</div></div>'

                if registro['obs']:
                    html_registros += f"""
                    <div class="mt-3">
                        <strong>Observações:</strong>
                        <p class="mb-0">{registro['obs']}</p>
                    </div>
                    """

                html_registros += "</div>"

            return JsonResponse({
                'registros': registros,
                'has_more': has_more,
                'html': html_registros
            })

    except oracledb.Error as e:
        error_obj, = e.args
        if is_ajax:
            return JsonResponse({'error': error_obj.message}, status=500)
        return render(request, 'error.html', {'message': f"Erro de banco de dados: {error_obj.message}"})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render(request, 'historico.html', {
        'sala': sala_data,
        'registros': registros,
        'has_more': has_more,
        'offset': offset + len(registros)
    })

def login_relatorio_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == 'admin' and password == 'hgn':
            request.session['relatorio_autenticado'] = True
            return redirect('relatorio_view')
        else:
            return render(request, 'login_relatorio.html', {'erro': 'Usuário ou senha incorretos'})

    return render(request, 'login_relatorio.html')


def relatorio_view(request):
    if not request.session.get('relatorio_autenticado'):
        return redirect('login_relatorio_view')

    conn = None
    cursor = None
    registros = []
    setores = set()

    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()

        data_inicio_param = request.GET.get('data_inicio')
        data_fim_param = request.GET.get('data_fim')

        if data_inicio_param:
            data_inicio = datetime.strptime(data_inicio_param, '%Y-%m-%d')
        else:
            data_inicio = datetime.now() - timedelta(days=30)

        query_params = {'data_inicio': data_inicio}
        where_clause = "WHERE r.data_limpeza >= :data_inicio"

        if data_fim_param:
            data_fim = datetime.strptime(data_fim_param, '%Y-%m-%d')
            where_clause += " AND r.data_limpeza <= :data_fim"
            query_params['data_fim'] = data_fim

        query = f"""
            SELECT
                r.id_registro, r.colaborador, r.data_limpeza, r.hora_limpeza,
                r.id_tipo_limpeza, r.obs, r.id_criticidade,
                s.nome_sala, st.nome_setor,
                r.portas, r.teto, r.paredes, r.janelas, r.piso,
                r.superficie_mobiliario, r.dispenser
            FROM if_tbl_registro_higiene r
            JOIN if_tbl_sala_higiene s ON r.id_sala = s.id_sala
            JOIN if_tbl_setores_higiene st ON s.id_setor = st.id_setor
            {where_clause}
            ORDER BY r.data_limpeza DESC, r.hora_limpeza DESC
        """
        cursor.execute(query, query_params)
        results = cursor.fetchall()

        # Mapeamento de IDs para texto
        tipo_limpeza_map = {1: 'concorrente', 2: 'terminal'}
        criticidade_map = {1: 'crítico', 2: 'semi-crítico', 3: 'não-crítico'}

        for row in results:
            setores.add(row[8])
            registros.append({
                'id_registro': row[0],
                'colaborador': row[1],
                'data_limpeza': row[2],
                'hora_limpeza': row[3],
                'tipo_limpeza': tipo_limpeza_map.get(row[4], 'concorrente'),
                'obs': row[5],
                'criticidade': criticidade_map.get(row[6], ''),
                'nome_sala': row[7],
                'nome_setor': row[8],
                'portas': row[9],
                'teto': row[10],
                'paredes': row[11],
                'janelas': row[12],
                'piso': row[13],
                'superficie_mobiliario': row[14],
                'dispenser': row[15],
            })

    except oracledb.Error as e:
        error_obj, = e.args
        return render(request, 'error.html', {'message': f"Erro de banco de dados: {error_obj.message}"})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render(request, 'relatorio.html', {
        'registros': registros,
        'setores': sorted(setores)
    })

@csrf_exempt
@ip_whitelist_required()
def atualizar_registro_view(request, registro_id):
    if request.method == 'POST':
        conn = None
        cursor = None

        try:
            data = json.loads(request.body)
            field = data.get('field')
            value = data.get('value')

            allowed_fields = [
                'colaborador', 'obs', 'data_limpeza', 'hora_limpeza',
                'tipo_limpeza', 'criticidade', 'portas', 'teto',
                'paredes', 'janelas', 'piso', 'superficie_mobiliario', 'dispenser'
            ]
            if field not in allowed_fields:
                return JsonResponse({'error': 'Campo não permitido'}, status=400)

            conn = get_oracle_connection()
            cursor = conn.cursor()

            if value == '' or value == 'null' or value is None:
                value = None
            elif field == 'data_limpeza' and value:
                try:
                    date_obj = datetime.strptime(value, '%Y-%m-%d')
                    value = date_obj
                except Exception as e:
                    return JsonResponse({'error': 'Formato de data inválido'}, status=400)

            # Mapear nomes de campos para os nomes corretos no banco
            field_mapping = {
                'tipo_limpeza': 'ID_TIPO_LIMPEZA',
                'criticidade': 'ID_CRITICIDADE',
                'data_limpeza': 'DATA_LIMPEZA'
            }

            if field == 'data_limpeza':
                query = "UPDATE if_tbl_registro_higiene SET DATA_LIMPEZA = :value WHERE id_registro = :id"
            else:
                db_field = field_mapping.get(field, field.upper())
                query = f"UPDATE if_tbl_registro_higiene SET {db_field} = :value WHERE id_registro = :id"

            cursor.execute(query, {'value': value, 'id': registro_id})
            conn.commit()

            return JsonResponse({'success': True})

        except oracledb.Error as e:
            error_obj, = e.args
            return JsonResponse({'error': error_obj.message}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
@ip_whitelist_required()
def excluir_registro_view(request, registro_id):
    if request.method == 'POST':
        conn = None
        cursor = None

        try:
            conn = get_oracle_connection()
            cursor = conn.cursor()

            query = "DELETE FROM if_tbl_registro_higiene WHERE id_registro = :id"
            cursor.execute(query, {'id': registro_id})
            conn.commit()

            return JsonResponse({'success': True})

        except oracledb.Error as e:
            error_obj, = e.args
            return JsonResponse({'error': error_obj.message}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
@ip_whitelist_required()
def obter_registro_view(request, registro_id):
    if request.method == 'GET':
        conn = None
        cursor = None

        try:
            conn = get_oracle_connection()
            cursor = conn.cursor()

            query = """
                SELECT colaborador, data_limpeza, hora_limpeza, id_tipo_limpeza,
                       id_criticidade, portas, teto, paredes, janelas, piso,
                       superficie_mobiliario, dispenser, obs
                FROM if_tbl_registro_higiene
                WHERE id_registro = :id
            """
            cursor.execute(query, {'id': registro_id})
            result = cursor.fetchone()

            if result:
                # Converter IDs de volta para valores numéricos (1, 2, 3)
                return JsonResponse({
                    'colaborador': result[0],
                    'data_limpeza': result[1].strftime('%Y-%m-%d') if result[1] else '',
                    'hora_limpeza': result[2],
                    'tipo_limpeza': result[3] or 1,  # ID do tipo de limpeza
                    'criticidade': result[4] or 1,  # ID da criticidade
                    'portas': result[5] or 'NA',
                    'teto': result[6] or 'NA',
                    'paredes': result[7] or 'NA',
                    'janelas': result[8] or 'NA',
                    'piso': result[9] or 'NA',
                    'superficie_mobiliario': result[10] or 'NA',
                    'dispenser': result[11] or 'NA',
                    'obs': result[12] or ''
                })
            else:
                return JsonResponse({'error': 'Registro não encontrado'}, status=404)

        except oracledb.Error as e:
            error_obj, = e.args
            return JsonResponse({'error': error_obj.message}, status=500)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return JsonResponse({'error': 'Método não permitido'}, status=405)

