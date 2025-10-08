# Controle de Acesso por Device ID

Este documento descreve como o `device_id` definido no aplicativo Android interage com a autorização realizada pelo backend (Django) para liberar ou bloquear o acesso às rotas do sistema.

## Visão Geral do Fluxo

1. **Aplicativo Android**
   - O usuário abre a tela de Configurações (ícone de engrenagem) e informa um identificador textual no campo **ID do Dispositivo** (ex.: `tablet-sala-1`).  
   - Ao salvar, esse valor é persistido localmente (SharedPreferences).  
   - Cada navegação do WebView envia o `device_id` de duas maneiras:
     - Cabeçalho HTTP `X-Device-Id`.
     - Cookie `device_id` (útil para requests subsequentes feitos pelo browser interno).

2. **Backend Django**
   - O decorator `@ip_whitelist_required` (arquivo `registro/decorators.py`) intercepta todas as views protegidas.
   - Primeiro, ele identifica o IP real do cliente e verifica se este IP está autorizado no modelo `IPPermitido` (Tabela SQLite).
   - Se o IP estiver ativo e cadastrado, o acesso é imediatamente liberado.
   - Caso o IP não esteja liberado, o decorator verifica se chegou um `device_id` e consulta a tabela `DispositivoPermitido` (também no SQLite).
   - Somente quando **nenhum dos dois** (IP ou device) estiver autorizado é que o acesso é negado e o usuário é redirecionado para `https://amevotuporanga.com.br/`.

3. **Banco de Dados**
   - O SQLite (`db.sqlite3`) mantém as tabelas de controle `IPPermitido` e `DispositivoPermitido`.  
   - O roteador de banco (`higiene_project/routers.py`) garante que esses modelos sejam lidos/escritos apenas no banco `default` (SQLite), independentemente de outros modelos usarem o Oracle.

## Como Cadastrar um Device ID

1. Acesse o **Django Admin** (`/admin/`), vá até *Dispositivos Permitidos* e crie um novo registro:
   - `identificador`: deve corresponder exatamente ao texto configurado no app.
   - `descricao`: opcional, ajuda na identificação do aparelho.
   - `ativo`: marque como verdadeiro para liberar o acesso.  
2. Anote o valor de `identificador` e configure o mesmo texto no aplicativo Android.
3. O aplicativo deve ser recompilado (após 2025-10-08) ou atualizado para a versão que contém o campo de ID (ver `android/HIgiene/app/src/main/java/com/example/higiene/MainActivity.kt`).

## Logs e Diagnóstico

O logger `registro.decorators` registra cada tentativa de acesso:

- **Permitido por IP**  
  `[INFO] ... Acesso PERMITIDO - IP: 172.19.201.2 - URL: /...`
- **Permitido por Device ID**  
  `[INFO] ... Acesso PERMITIDO - Device ID: tablet-sala-1 - URL: /...`
- **Negado** (IP e Device não cadastrados)  
  `[WARNING] ... Acesso NEGADO - IP: ... - Device ID: N/A - URL: /...`
- **Device ID inválido**  
  `[WARNING] ... Acesso NEGADO - Device ID: tablet-desconhecido nao autorizado - IP: ... - URL: /...`

Com os logs é possível identificar rapidamente se faltou cadastro do device ou se o IP não está whitelisted.

## Testando o Fluxo

1. **Cenário IP liberado:** cadastre o IP no admin (`IPPermitido`), acesse qualquer rota sem definir device; o acesso deve ser liberado.
2. **Cenário Device liberado:** remova o IP, cadastre o device, configure-o no app Android e tente acesso. O decorator deve liberar com base no `device_id`.
3. **Cenário não autorizado:** removendo ambos, o acesso deve redirecionar para `https://amevotuporanga.com.br/` e o log deve registrar como `NEGADO`.

## Referências de Código

- `registro/decorators.py` – lógica de verificação do IP e device.
- `registro/models.py` – modelos `IPPermitido` e `DispositivoPermitido`.
- `registro/admin.py` – registro dos modelos no Django Admin.
- `higiene_project/routers.py` – roteamento do SQLite vs Oracle.
- `android/HIgiene/app/src/main/java/com/example/higiene/MainActivity.kt` – fluxo do app que captura, salva e envia o `device_id`.

## Observações

- O campo `device_id` **deve** ser preenchido manualmente em cada dispositivo no app com o mesmo valor cadastrado no banco.
- O `device_id` diferencia maiúsculas de minúsculas; mantenha a mesma formatação entre app e banco.
- Caso o app esteja em uma versão antiga (sem o campo), atualize o APK para a compilação mais recente (`./gradlew assembleDebug` + `adb install -r ...`).
