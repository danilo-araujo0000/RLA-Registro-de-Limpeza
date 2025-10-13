# Registro Higiene - Scanner de QR Code

Aplicativo Android para leitura de QR Codes com abertura automática de links em navegador interno.

## Características

- **Scanner de QR Code**: Usa ML Kit e CameraX para detecção em tempo real
- **Navegador Interno**: WebView integrado para abrir links sem sair do app
- **Retorno Automático**: Detecta URLs de sucesso e retorna ao scanner automaticamente
- **Configurações Protegidas**: Acesso às configurações mediante senha
- **Tema Azul Personalizado**: Interface em Material Design 3 com cores da AME

## Requisitos

- Android 7.0 (API 24) ou superior
- Permissão de câmera
- Conexão com internet

## Funcionalidades

### 1. Scanner de QR Code

O app abre diretamente na tela de scanner, onde a câmera detecta automaticamente QR Codes que contenham URLs.

```kotlin
@Composable
fun CameraPreview(onQrCodeDetected: (String) -> Unit) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val cameraProviderFuture = remember { ProcessCameraProvider.getInstance(context) }
    val barcodeScanner = remember { BarcodeScanning.getClient() }

    // Configuração da câmera e análise de imagem
    val imageAnalysis = ImageAnalysis.Builder()
        .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
        .build()

    imageAnalysis.setAnalyzer(executor) { imageProxy ->
        processImageProxy(barcodeScanner, imageProxy, onQrCodeDetected)
    }
}
```

**Validação de URL:**
```kotlin
private fun isValidUrl(text: String): Boolean {
    return text.startsWith("http://", ignoreCase = true) ||
           text.startsWith("https://", ignoreCase = true)
}
```

### 2. Botão Manual

Permite acessar uma URL configurável sem precisar escanear QR Code.

**Configuração padrão:**
```kotlin
var manualUrl by remember {
    mutableStateOf(prefs.getString("manual_url", "http://172.19.0.0/") ?: "http://172.19.0.0/")
}
```

### 3. Navegador Interno (WebView)

Quando um QR Code é detectado ou o botão MANUAL é pressionado, o link abre em um WebView com recursos completos.

```kotlin
WebView(context).apply {
    webViewClient = object : WebViewClient() {
        override fun onPageFinished(view: WebView?, url: String?) {
            super.onPageFinished(view, url)
            url?.let {
                // Detecta URL de retorno
                if (returnUrl.isNotEmpty() && it.contains(returnUrl, ignoreCase = true)) {
                    Handler(Looper.getMainLooper()).postDelayed({
                        onBack()
                    }, (returnDelay * 1000).toLong())
                }
            }
        }
    }
    settings.javaScriptEnabled = true
    settings.domStorageEnabled = true
    settings.builtInZoomControls = true
    settings.displayZoomControls = false
}
```

**Recursos habilitados:**
- JavaScript
- DOM Storage
- Controles de zoom
- Wide viewport
- Navegação com botão voltar

### 4. Retorno Automático

O app pode detectar quando uma URL específica é carregada e retornar automaticamente ao scanner após um delay configurável.

**Exemplo de uso:**

Se você configurar:
- **URL de Retorno**: `sucesso`
- **Delay de Retorno**: `7` segundos

Quando o usuário acessar uma página como `http://172.19.0.0/cadastro/sucesso`, o app aguardará 7 segundos e automaticamente retornará à tela do scanner.

### 5. Configurações Protegidas por Senha

Acesso às configurações requer senha de administrador.

```kotlin
@Composable
fun PasswordDialog(
    onPasswordCorrect: () -> Unit,
    onDismiss: () -> Unit
) {
    var password by remember { mutableStateOf("") }

    AlertDialog(
        title = { Text("Senha de Administrador") },
        confirmButton = {
            Button(
                onClick = {
                    if (password == "admin123") {
                        onPasswordCorrect()
                    } else {
                        showError = true
                    }
                }
            ) {
                Text("Confirmar")
            }
        }
    )
}
```

**Senha padrão:** `admin123`

### 6. Tela de Configurações

Permite personalizar:

- **URL Manual**: Link aberto ao pressionar o botão MANUAL
- **URL de Retorno**: Padrão de URL para detectar sucesso e retornar
- **Delay de Retorno**: Tempo de espera (0-60 segundos) antes de retornar ao scanner

```kotlin
// Salvando configurações
prefs.edit().apply {
    putString("manual_url", manualUrl)
    putString("return_url", returnUrl)
    putInt("return_delay", returnDelay)
    apply()
}
```

## Tema Personalizado

O app usa um tema azul personalizado em Material Design 3:

```kotlin
private val Blue500 = Color(0xFF2196F3)
private val Blue700 = Color(0xFF1976D2)
private val Blue200 = Color(0xFF90CAF9)

private val LightBlueColorScheme = lightColorScheme(
    primary = Blue500,
    onPrimary = Color.White,
    primaryContainer = Blue200,
    onPrimaryContainer = Blue700,
    secondary = Color(0xFF03DAC5),
    onSecondary = Color.Black,
    error = Color(0xFFB00020),
    onError = Color.White
)

@Composable
fun BlueTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = LightBlueColorScheme,
        content = content
    )
}
```

## Estrutura do Projeto

```
RegistroHigiene/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/example/RegistroHigiene/
│   │   │   │   └── MainActivity.kt
│   │   │   ├── res/
│   │   │   │   ├── mipmap-*/
│   │   │   │   │   └── ic_launcher.png (Logo AME)
│   │   │   │   ├── values/
│   │   │   │   │   ├── colors.xml
│   │   │   │   │   └── themes.xml
│   │   │   │   └── drawable/
│   │   │   └── AndroidManifest.xml
│   │   └── androidTest/
│   └── build.gradle.kts
├── gradle/
│   └── libs.versions.toml
└── gradle.properties
```

## Dependências Principais

```kotlin
// Jetpack Compose
implementation("androidx.compose.ui:ui")
implementation("androidx.compose.material3:material3")
implementation("androidx.activity:activity-compose:1.9.3")

// CameraX
implementation("androidx.camera:camera-camera2:1.4.0")
implementation("androidx.camera:camera-lifecycle:1.4.0")
implementation("androidx.camera:camera-view:1.4.0")

// ML Kit Barcode Scanning
implementation("com.google.mlkit:barcode-scanning:17.3.0")
```

## Permissões Necessárias

```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-feature android:name="android.hardware.camera" android:required="true" />
```

## Como Compilar

1. Clone o repositório
2. Abra o projeto no Android Studio
3. Aguarde o Gradle sincronizar
4. Execute o build:

```bash
./gradlew.bat assembleDebug
```

## Como Instalar

Via ADB:

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

## Fluxo de Uso

1. **Abrir app** → Permissão de câmera solicitada
2. **Scanner ativo** → Apontar para QR Code com URL
3. **QR detectado** → WebView abre automaticamente
4. **Navegar** → Usuário completa ação no site
5. **URL de sucesso detectada** → Aguarda delay configurado
6. **Retorno automático** → Volta ao scanner

## Exemplo de Integração

### Cenário: Cadastro de Higiene

1. Usuário escaneia QR Code com URL: `http://172.19.0.0/cadastro/novo`
2. WebView abre formulário de cadastro
3. Usuário preenche dados e submete
4. Sistema redireciona para: `http://172.19.0.0/cadastro/sucesso`
5. App detecta "sucesso" na URL
6. Aguarda 7 segundos
7. Retorna automaticamente ao scanner para próximo cadastro

### Configuração para esse cenário:

- **URL Manual**: `http://172.19.0.0/`
- **URL de Retorno**: `sucesso`
- **Delay de Retorno**: `7` segundos

## Personalização

### Alterar senha de administrador

Em `MainActivity.kt`, linha 219:

```kotlin
if (password == "admin123") {  // Altere aqui
    onPasswordCorrect()
}
```

### Alterar cores do tema

Em `MainActivity.kt`, linhas 40-52:

```kotlin
private val Blue500 = Color(0xFF2196F3)  // Cor primária
private val Blue700 = Color(0xFF1976D2)  // Cor primária escura
private val Blue200 = Color(0xFF90CAF9)  // Cor do container
```

### Alterar texto da interface

Exemplos:

```kotlin
// Título do scanner
title = { Text("Scanear QR Code") }

// Título do navegador
title = { Text("Pagina Web") }

// Botão manual
Text("MANUAL")
```

## Troubleshooting

### Câmera não inicia
- Verifique se a permissão foi concedida
- Logs em: `Log.e("QRScanner", "Erro ao iniciar câmera", e)`

### QR Code não detectado
- Verifique se o QR contém uma URL válida (http:// ou https://)
- Melhore iluminação
- Aproxime/afaste o QR Code

### WebView não carrega
- Verifique conexão com internet
- Verifique se a URL é acessível
- Habilite `usesCleartextTraffic` no AndroidManifest para HTTP

### Retorno automático não funciona
- Verifique se a URL de retorno está configurada
- Confirme que a URL final contém o padrão configurado
- Teste com delay maior

## Licença

Desenvolvido para AME Votuporanga.

## Contato

Para suporte ou dúvidas sobre o aplicativo, entre em contato com a equipe de desenvolvimento.
