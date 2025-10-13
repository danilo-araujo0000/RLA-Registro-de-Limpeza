## Visao Geral
- Plataforma web baseada em Django para registrar, consultar e auditar rotinas de limpeza hospitalar integradas em banco Oracle.
- Camada web atende paineis touch em setores restritos; acesso controlado por IP ou Device ID.
- Modulo Android (Jetpack Compose) opera como scanner de QR Code, lança WebView autenticada e reforça identificacao do dispositivo.
- Empacotamento via Docker (Ubuntu 22.04) com Oracle Instant Client e servico Gunicorn pronto para producao.
## Estrutura do Repositorio
- `higiene_project/`: configuracoes globais de Django; aponta templates externos, ativa WhiteNoise, carrega variaveis `.env`.
- `registro/`: app principal com modelos de whitelists, decoradores de seguranca e views que interagem com o Oracle (`registro/views.py:57`, `registro/views.py:274`, `registro/views.py:394`).
- `templates/` e `static/`: paginas HTML, CSS e icones utilizados pelos paineis de registro, historico, relatorio e mensagens de erro.
- `android/HIgiene/`: aplicativo Kotlin dividido em modulos de UI (scanner, WebView, configuracoes, tema).
- Scripts utilitarios na raiz (`create_superuser.py`, `coletardatav1.py`) e artefatos de deploy (`Dockerfile`, `docker-compose.yml`, `tutorial`).
## Backend Django
### Configuracao
- `higiene_project/settings.py` define `INSTALLED_APPS`, ativa WhiteNoise, configura `STATIC_ROOT` e idioma/PT-BR. Banco padrao local e SQLite para Django, mas toda logica de negocio usa conexoes Oracle gerenciadas manualmente (`registro/views.py:44`).
- Variaveis sensiveis residem em `higiene_project/.env` (SECRET_KEY, flags de debug e credenciais Oracle). O `docker-compose.yml` fornece equivalentes para execucao conteinerizada.
### Modelos de Dominio
- `registro/models.py:4` (`IPPermitido`) e `registro/models.py:42` (`DispositivoPermitido`) centralizam whitelist de rede e dispositivos, com metadados, timestamps automáticos e ordenacao por status.
- `registro/models.py:81` (`UserRelatorio`) armazena credenciais especificas do modulo de relatorios, flag `edit` que bloqueia acesso a edicao detalhada e data de criacao controlada.
### Decoradores de Seguranca
- `registro/decorators.py:32` valida IP e Device ID, registrando tentativas e redirecionando acessos nao autorizados.
- `registro/decorators.py:89` garante sessao autenticada antes de exibir o relatorio consolidado.
- `registro/decorators.py:118` bloqueia usuarios marcados com `edit=True` nas rotas sensiveis, retornando `erro_permissao.html`.
### Fluxos Principais
1. **Selecao de Sala**  
   - `/salas/` (`registro/views.py:274`) agrupa salas por setor, calcula cor dinamica e mostra ultimo registro concorrente/terminal.
2. **Registro de Limpeza**  
   - `/sala/<id>/` (`registro/views.py:57`) apresenta menu inicial da sala.
   - `/registro/<id>/` (`registro/views.py:96`) fornece formulario com colaboradores do Oracle (`dbasgu.USUARIOS`), converte nomes em formato compacto, entrega JSON para front-end.
   - POST `/salvar/` (`registro/views.py:154`) valida campos, converte vazios em `NA`, identifica dispositivo via cookie/cabecalho IP e grava em `if_tbl_registro_higiene`, incluindo timestamp `LAST_UPDATE`.
   - `/sucesso/` (`registro/views.py:270`) confirma operacao aos operadores.
3. **Historico e Relatorio**  
   - `/historico/<id>/` (`registro/views.py:394`) pagina registros via `ROW_NUMBER`, suporta carregamento incremental via AJAX e formata badges de status de limpeza e reposicao.
   - `/login-relatorio/` (`registro/views.py:579`) autentica usuarios do modelo `UserRelatorio`.
   - `/relatorio/` (`registro/views.py:597`) gera visao consolidada multi-sala filtrada por intervalo de datas, reusa map de criticidade/tipo e compartilha lista de colaboradores para filtros de front-end.
4. **Administracao de Registros**  
   - PATCH-like `/atualizar-registro/<id>/` (`registro/views.py:726`) aceita JSON com campo alvo, valida lista branca de colunas, converte datas e atualiza `LAST_UPDATE`.
   - POST `/excluir-registro/<id>/` (`registro/views.py:790`) remove o registro.
   - GET `/obter-registro/<id>/` (`registro/views.py:822`) devolve JSON detalhado, restringido por `relatorio_edit_blocked`.
## Integracao com Oracle
- Driver `oracledb` inicializa Instant Client dinamicamente (Windows vs Linux) logo no load do modulo (`registro/views.py:12`).
- `get_oracle_connection` monta DSN com `DB_NAME` (`host:porta/servico`) e conecta usando credenciais de ambiente.
- SQLs cobrem leitura de salas (`if_tbl_sala_higiene`, `if_tbl_setores_higiene`), colaboradores (`dbasgu.USUARIOS`), historicos e `INSERT/UPDATE/DELETE` sobre `if_tbl_registro_higiene`.
- Todos os cursores sao fechados em `finally` e excecoes retornam `error.html` com mensagem amigavel.
## Templates e Estilos
- `templates/base.html` aplica layout com Bootstrap, barra superior e area de conteudo.
- Paginas especificas (`templates/index.html`, `templates/registro.html`, `templates/historico.html`, `templates/relatorio.html`, etc.) usam CSS dedicado em `static/css/` para otimizar uso em tablets.
- `templates/error.html` e `templates/erro_permissao.html` mostram estados de falha (acesso negado, excecoes Oracle).
- Sucesso e login tem paginas proprias para fluxo orientado touch.
## Scripts e Utilitarios
- `create_superuser.py` cria administradores Django a partir de variaveis `DJANGO_SUPERUSER_*`, permitindo seed automatico na subida do container.
- `coletardatav1.py` coleta dados de pacientes em Oracle, gera JSON versionado em `data/` e registra atividades via `log.Logger` (utilizado fora do app web).
- `tutorial` apresenta comandos docker padrao (`docker build`, `docker-compose up`, `docker run` com `--env-file`).
## Deploy e Execucao
- **Requisitos**: Python 3.11, Oracle Instant Client e dependencias de `requirements.txt` (Django, python-dotenv, oracledb, gunicorn, whitenoise).
- **Local**: exportar variaveis apontadas em `.env`, executar `python manage.py runserver`. Necessario copiar bibliotecas Oracle para o caminho configurado em `registro/views.py`.
- **Docker**: `Dockerfile` instala Python, baixa Instant Client 23.5, roda `collectstatic`, aplica `migrate`, executa `create_superuser.py` e inicia gunicorn. `docker-compose.yml` define volume persistente para `staticfiles` e injeta credenciais.
- **Android**: projeto `android/HIgiene/` utiliza ML Kit e CameraX para ler QR Codes, configurar Device ID e abrir WebView (`android/.../QRCodeScannerScreen.kt`, `android/.../WebViewScreen.kt`). Aplicativo preenche header `X-Device-Id` e cookie `device_id`, respeitando politica de whitelist no backend.
## Consideracoes de Segurança e Operacao
- Atualizar variaveis de ambiente para remover credenciais default antes de subir em producao.
- A whitelist de IP/Device deve ser mantida via admin Django (modelos `IPPermitido`, `DispositivoPermitido`) ou scripts customizados.
- Garantir que o Oracle Instant Client esteja acessivel tanto no host quanto no container, seguindo caminhos definidos.
- Para auditoria, logs gerados por `registro/decorators.py` sao enviados ao console (ou stdout do container) com formato `[LEVEL] timestamp - logger - mensagem`, facilitando ingestao em stacks de observabilidade.
## Proximos Passos Sugeridos
- Implementar interface administrativa para gerenciar usuarios `UserRelatorio` com hash de senha (atualmente texto plano).
- Adicionar testes automatizados em `registro/tests.py` para validar fluxo de whitelists e consultas historicas.
- Documentar strategy de atualizacao do Oracle Instant Client