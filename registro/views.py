import os
from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import oracledb
from django.utils import timezone
from datetime import datetime, timedelta
import json
from .decorators import ip_whitelist_required, relatorio_auth_required, relatorio_edit_blocked

try:
    if os.name == 'nt':  
        instant_client_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..',
            'instantclient-basic-windows.x64-23.7.0.25.01',
            'instantclient_23_7'
        )
        oracledb.init_oracle_client(lib_dir=instant_client_dir)
    else:  
        oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient_23_5")
except Exception as e:
    print(f"Erro ao inicializar Oracle Client: {e}")


def extrair_nome_abreviado(nome_completo):
    if not nome_completo:
        return ''

    partes_nome = nome_completo.split()
    preposicoes = ['de', 'da', 'do', 'dos', 'das']
    nome_abreviado_partes = [partes_nome[0]]  

    
    for i in range(1, len(partes_nome)):
        nome_abreviado_partes.append(partes_nome[i])
        if partes_nome[i].lower() not in preposicoes:
            break

    return ' '.join(nome_abreviado_partes)


def get_oracle_connection():
    db_name = os.environ.get('DB_NAME', '')
    db_user = os.environ.get('DB_USER', '')
    db_password = os.environ.get('DB_PASSWORD', '')
    dsn = oracledb.makedsn(db_name.split(':')[0], db_name.split(':')[1].split('/')[0], service_name=db_name.split('/')[1])
    return oracledb.connect(user=db_user, password=db_password, dsn=dsn)

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
            SELECT DISTINCT NM_USUARIO, CD_USUARIO
            FROM dbasgu.USUARIOS u
            WHERE u.DS_OBSERVACAO = 'HIGIENE' AND u.SN_ATIVO = 'S'
            ORDER BY NM_USUARIO
        """
        cursor.execute(query_colaboradores)
        results = cursor.fetchall()

        for row in results:
            nome_completo = row[0]
            cd_usuario = row[1]
            if nome_completo:
                nome_abreviado = extrair_nome_abreviado(nome_completo)
                colaboradores.append({
                    'primeiro_nome': nome_abreviado,
                    'nome_completo': nome_completo,
                    'cd_usuario': cd_usuario
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

            colaboradores_json = request.POST.get('colaboradores_json')
            if not colaboradores_json:
                return render(request, 'error.html', {'message': 'Nenhum colaborador selecionado!'})

            try:
                json.loads(colaboradores_json) 
            except json.JSONDecodeError:
                return render(request, 'error.html', {'message': 'Formato de colaboradores inválido!'})

            colaborador = colaboradores_json

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
            device_id = request.COOKIES.get('device_id')
            if not device_id:
                device_id = request.META.get('HTTP_X_DEVICE_ID')
            if not device_id:
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    device_id = x_forwarded_for.split(',')[0]
                else:
                    device_id = request.META.get('REMOTE_ADDR')

            sql = """INSERT INTO if_tbl_registro_higiene (
                ID_SALA, COLABORADOR, DATA_LIMPEZA, HORA_LIMPEZA, ID_TIPO_LIMPEZA, OBS,
                PORTAS, TETO, PAREDES, JANELAS, PISO, SUPERFICIE_MOBILIARIO, DISPENSER, ID_CRITICIDADE,
                PAPEL_HIG, PAPEL_TOALHA, ALCOOL, SABONETE, DEVICE, LAST_UPDATE
            ) VALUES (
                :id_sala, :colaborador, SYSDATE, :hora_limpeza, :id_tipo_limpeza, :obs,
                :portas, :teto, :paredes, :janelas, :piso, :superficie_mobiliario, :dispenser, :id_criticidade,
                :papel_hig, :papel_toalha, :alcool, :sabonete, :device_id, SYSDATE
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
                'device_id': device_id,
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
    setores_dict = {}

    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()

        query = """
            SELECT s.id_sala,
                   s.nome_sala,
                   st.nome_setor,
                   st.id_setor,
                   NVL(MAX(r.id_tipo_limpeza), 1) AS tipo_preferencial,
                   uc.data_limpeza AS ultima_concorrente,
                   uc.hora_limpeza AS ultima_concorrente_hora,
                   ut.data_limpeza AS ultima_terminal_data,
                   ut.hora_limpeza AS ultima_terminal_hora
            FROM if_tbl_sala_higiene s
            JOIN if_tbl_setores_higiene st ON s.id_setor = st.id_setor
            LEFT JOIN if_tbl_registro_higiene r ON r.id_sala = s.id_sala
            LEFT JOIN (
                SELECT id_sala, data_limpeza, hora_limpeza
                FROM (
                    SELECT id_sala,
                           data_limpeza,
                           hora_limpeza,
                           ROW_NUMBER() OVER (PARTITION BY id_sala ORDER BY data_limpeza DESC, hora_limpeza DESC) AS rn
                    FROM if_tbl_registro_higiene
                    WHERE id_tipo_limpeza = 1
                )
                WHERE rn = 1
            ) uc ON uc.id_sala = s.id_sala
            LEFT JOIN (
                SELECT id_sala, data_limpeza, hora_limpeza
                FROM (
                    SELECT id_sala,
                           data_limpeza,
                           hora_limpeza,
                           ROW_NUMBER() OVER (PARTITION BY id_sala ORDER BY data_limpeza DESC, hora_limpeza DESC) AS rn
                    FROM if_tbl_registro_higiene
                    WHERE id_tipo_limpeza = 2
                )
                WHERE rn = 1
            ) ut ON ut.id_sala = s.id_sala
            GROUP BY s.id_sala, s.nome_sala, st.nome_setor, st.id_setor,
                     uc.data_limpeza, uc.hora_limpeza,
                     ut.data_limpeza, ut.hora_limpeza
            ORDER BY s.id_sala ASC
        """
        cursor.execute(query)
        results = cursor.fetchall()

        for row in results:
            id_setor = row[3]
            tipo_preferencial = int(row[4]) if len(row) > 4 and row[4] is not None else 1
            tipo_descricao = 'terminal' if tipo_preferencial == 2 else 'concorrente'
            ultima_concorrente = row[5] if len(row) > 5 else None
            ultima_concorrente_hora = row[6] if len(row) > 6 else None
            ultima_terminal_data = row[7] if len(row) > 7 else None
            ultima_terminal_hora = row[8] if len(row) > 8 else None

            ultima_concorrente_fmt = ultima_concorrente.strftime('%d/%m/%Y') if ultima_concorrente else '-'
            ultima_terminal_data_fmt = ultima_terminal_data.strftime('%d/%m/%Y') if ultima_terminal_data else '-'
            if ultima_concorrente_hora:
                if hasattr(ultima_concorrente_hora, 'strftime'):
                    ultima_concorrente_hora_fmt = ultima_concorrente_hora.strftime('%H:%M')
                else:
                    hora_str = str(ultima_concorrente_hora)
                    ultima_concorrente_hora_fmt = hora_str[:5]
            else:
                ultima_concorrente_hora_fmt = ''
            if ultima_terminal_hora:
                if hasattr(ultima_terminal_hora, 'strftime'):
                    ultima_terminal_hora_fmt = ultima_terminal_hora.strftime('%H:%M')
                else:
                    hora_str = str(ultima_terminal_hora)
                    ultima_terminal_hora_fmt = hora_str[:5]
            else:
                ultima_terminal_hora_fmt = ''

            nome_setor = row[2]
            setor_color = f'setor-color-{(id_setor - 1) % 16}'
            if nome_setor not in setores_dict:
                setores_dict[nome_setor] = {
                    'nome': nome_setor,
                    'slug': slugify(nome_setor),
                    'color': setor_color
                }

            salas.append({
                'id_sala': row[0],
                'nome_sala': row[1],
                'nome_setor': row[2],
                'setor_color': setor_color,
                'setor_slug': setores_dict[nome_setor]['slug'],
                'tipo_limpeza': tipo_descricao,
                'ultima_concorrente': ultima_concorrente_fmt,
                'ultima_concorrente_hora': ultima_concorrente_hora_fmt,
                'ultima_terminal_data': ultima_terminal_data_fmt,
                'ultima_terminal_hora': ultima_terminal_hora_fmt,
            })

    except oracledb.Error as e:
        error_obj, = e.args
        return render(request, 'error.html', {'message': f"Erro de banco de dados: {error_obj.message}"})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render(request, 'salas.html', {
        'salas': salas,
        'setores': sorted(setores_dict.values(), key=lambda x: x['nome'])
    })

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
                    papel_hig, papel_toalha, alcool, sabonete,
                    ROW_NUMBER() OVER (ORDER BY data_limpeza DESC, hora_limpeza DESC) as rn
                FROM if_tbl_registro_higiene
                WHERE id_sala = :id_sala
            )
            WHERE rn > :offset AND rn <= :end_row
        """
        cursor.execute(query_registros, {'id_sala': sala_id, 'offset': offset, 'end_row': offset + limit})
        results = cursor.fetchall()

        tipo_limpeza_map = {1: 'concorrente', 2: 'terminal'}
        criticidade_map = {1: 'crítico', 2: 'semi-crítico', 3: 'não-crítico'}

        for row in results:
            colaborador_str = row[1]
            colaborador_formatado = colaborador_str
            try:
                colaboradores_dict = json.loads(colaborador_str)
                items = []
                for key in sorted(colaboradores_dict.keys(), key=lambda x: int(x)):
                    items.append(f"{key}. {colaboradores_dict[key]}")
                colaborador_formatado = "\n".join(items)
            except (json.JSONDecodeError, ValueError, AttributeError, TypeError):
                pass

            registros.append({
                'id_registro': row[0],
                'colaborador': colaborador_formatado,
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
                'papel_hig': row[14] if row[14] else 'NA',
                'papel_toalha': row[15] if row[15] else 'NA',
                'alcool': row[16] if row[16] else 'NA',
                'sabonete': row[17] if row[17] else 'NA',
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
                <div class="registro-item" data-tipo="{registro['tipo_limpeza']}">
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

                    
                    html_registros += '<div class="mt-3"><strong>Reposição:</strong><div class="d-flex flex-wrap gap-2 mt-2">'

                    if registro['papel_hig'] != 'NA':
                        html_registros += f'<span class="badge badge-{registro["papel_hig"].lower()}">Papel Higiênico: {registro["papel_hig"]}</span>'
                    if registro['papel_toalha'] != 'NA':
                        html_registros += f'<span class="badge badge-{registro["papel_toalha"].lower()}">Papel Toalha: {registro["papel_toalha"]}</span>'
                    if registro['alcool'] != 'NA':
                        html_registros += f'<span class="badge badge-{registro["alcool"].lower()}">Álcool: {registro["alcool"]}</span>'
                    if registro['sabonete'] != 'NA':
                        html_registros += f'<span class="badge badge-{registro["sabonete"].lower()}">Sabonete: {registro["sabonete"]}</span>'

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

        from .models import UserRelatorio

        try:
            user = UserRelatorio.objects.get(username=username, password=password, ativo=True)
            request.session['relatorio_user_id'] = user.id
            return redirect('relatorio_view')
        except UserRelatorio.DoesNotExist:
            return render(request, 'login_relatorio.html', {'erro': 'Usuário ou senha incorretos'})

    return render(request, 'login_relatorio.html')


def logout_relatorio_view(request):
    request.session.flush()
    return redirect('login_relatorio_view')


@relatorio_auth_required
def relatorio_view(request):
    pass

    conn = None
    cursor = None
    registros = []
    setores_dict = {}
    colaboradores = []

    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()

        
        query_colaboradores = """
            SELECT DISTINCT NM_USUARIO, CD_USUARIO
            FROM dbasgu.USUARIOS u
            WHERE u.DS_OBSERVACAO = 'HIGIENE' AND u.SN_ATIVO = 'S'
            ORDER BY NM_USUARIO
        """
        cursor.execute(query_colaboradores)
        results_colab = cursor.fetchall()

        for row in results_colab:
            nome_completo = row[0]
            cd_usuario = row[1]
            if nome_completo:
                nome_abreviado = extrair_nome_abreviado(nome_completo)
                colaboradores.append({
                    'primeiro_nome': nome_abreviado,
                    'nome_completo': nome_completo,
                    'cd_usuario': cd_usuario
                })

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
                s.nome_sala, st.nome_setor, st.id_setor,
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

        
        tipo_limpeza_map = {1: 'concorrente', 2: 'terminal'}
        criticidade_map = {1: 'crítico', 2: 'semi-crítico', 3: 'não-crítico'}

        for row in results:
            nome_setor = row[8]
            id_setor = row[9]
            if nome_setor not in setores_dict:
                setores_dict[nome_setor] = {
                    'nome': nome_setor,
                    'id': id_setor,
                    'color': f'setor-color-{(id_setor - 1) % 16}'
                }

            
            colaborador_str = row[1]
            colaborador_formatado = colaborador_str
            try:
                colaboradores_dict = json.loads(colaborador_str)
                items = []
                for key in sorted(colaboradores_dict.keys(), key=lambda x: int(x)):
                    items.append(f"{key}. {colaboradores_dict[key]}")
                colaborador_formatado = "\n".join(items)
            except (json.JSONDecodeError, ValueError, AttributeError, TypeError):
                pass  

            registros.append({
                'id_registro': row[0],
                'colaborador': colaborador_formatado,
                'data_limpeza': row[2],
                'hora_limpeza': row[3],
                'tipo_limpeza': tipo_limpeza_map.get(row[4], 'concorrente'),
                'obs': row[5],
                'criticidade': criticidade_map.get(row[6], ''),
                'nome_sala': row[7],
                'nome_setor': row[8],
                'setor_color': setores_dict[row[8]]['color'],
                'portas': row[10],
                'teto': row[11],
                'paredes': row[12],
                'janelas': row[13],
                'piso': row[14],
                'superficie_mobiliario': row[15],
                'dispenser': row[16],
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
        'setores': sorted(setores_dict.values(), key=lambda x: x['nome']),
        'colaboradores': json.dumps(colaboradores)
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
                'paredes', 'janelas', 'piso', 'superficie_mobiliario', 'dispenser',
                'papel_hig', 'papel_toalha', 'alcool', 'sabonete'
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

            
            field_mapping = {
                'tipo_limpeza': 'ID_TIPO_LIMPEZA',
                'criticidade': 'ID_CRITICIDADE',
                'data_limpeza': 'DATA_LIMPEZA'
            }

            if field == 'data_limpeza':
                query = "UPDATE if_tbl_registro_higiene SET DATA_LIMPEZA = :value, LAST_UPDATE = SYSDATE WHERE id_registro = :id"
            else:
                db_field = field_mapping.get(field, field.upper())
                query = f"UPDATE if_tbl_registro_higiene SET {db_field} = :value, LAST_UPDATE = SYSDATE WHERE id_registro = :id"

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
@relatorio_auth_required
@relatorio_edit_blocked
def obter_registro_view(request, registro_id):
    if request.method == 'GET':
        conn = None
        cursor = None

        try:
            conn = get_oracle_connection()
            cursor = conn.cursor()

            query = """
                SELECT
                    r.colaborador,
                    r.data_limpeza,
                    r.hora_limpeza,
                    r.id_tipo_limpeza,
                    r.id_criticidade,
                    r.portas,
                    r.teto,
                    r.paredes,
                    r.janelas,
                    r.piso,
                    r.superficie_mobiliario,
                    r.dispenser,
                    r.papel_hig,
                    r.papel_toalha,
                    r.alcool,
                    r.sabonete,
                    s.nome_sala,
                    st.nome_setor,
                    r.device,
                    r.obs
                FROM if_tbl_registro_higiene r
                JOIN if_tbl_sala_higiene s ON r.id_sala = s.id_sala
                JOIN if_tbl_setores_higiene st ON s.id_setor = st.id_setor
                WHERE r.id_registro = :id
            """
            cursor.execute(query, {'id': registro_id})
            result = cursor.fetchone()

            if result:
                return JsonResponse({
                    'colaborador': result[0],
                    'data_limpeza': result[1].strftime('%Y-%m-%d') if result[1] else '',
                    'hora_limpeza': result[2],
                    'tipo_limpeza': result[3],
                    'criticidade': result[4],
                    'portas': result[5] or 'NA',
                    'teto': result[6] or 'NA',
                    'paredes': result[7] or 'NA',
                    'janelas': result[8] or 'NA',
                    'piso': result[9] or 'NA',
                    'superficie_mobiliario': result[10] or 'NA',
                    'dispenser': result[11] or 'NA',
                    'papel_hig': result[12] or 'NA',
                    'papel_toalha': result[13] or 'NA',
                    'alcool': result[14] or 'NA',
                    'sabonete': result[15] or 'NA',
                    'nome_sala': result[16] or '-',
                    'nome_setor': result[17] or '-',
                    'device': result[18] or '',
                    'obs': result[19] or ''
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
