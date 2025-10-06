package com.example.higiene

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.material3.lightColorScheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.common.InputImage
import java.util.concurrent.Executors

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

class MainActivity : ComponentActivity() {
    private val cameraPermissionRequest = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            setContent {
                QRCodeScannerApp()
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        when {
            ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.CAMERA
            ) == PackageManager.PERMISSION_GRANTED -> {
                setContent {
                    QRCodeScannerApp()
                }
            }
            else -> {
                cameraPermissionRequest.launch(Manifest.permission.CAMERA)
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun QRCodeScannerApp() {
    val context = LocalContext.current
    val prefs = remember { context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE) }

    var currentUrl by remember { mutableStateOf<String?>(null) }
    var lastScannedUrl by remember { mutableStateOf<String?>(null) }
    var showSettings by remember { mutableStateOf(false) }

    var manualUrl by remember { mutableStateOf(prefs.getString("manual_url", "http://172.19.0.0/") ?: "http://172.19.0.0/") }
    var returnUrl by remember { mutableStateOf(prefs.getString("return_url", "") ?: "") }
    var returnDelay by remember { mutableStateOf(prefs.getInt("return_delay", 7)) }
    var showPasswordDialog by remember { mutableStateOf(false) }

    BlueTheme {
        when {
            showPasswordDialog -> {
                PasswordDialog(
                    onPasswordCorrect = {
                        showPasswordDialog = false
                        showSettings = true
                    },
                    onDismiss = { showPasswordDialog = false }
                )
            }
            showSettings -> {
                SettingsScreen(
                    manualUrl = manualUrl,
                    returnUrl = returnUrl,
                    returnDelay = returnDelay,
                    onManualUrlChange = { manualUrl = it },
                    onReturnUrlChange = { returnUrl = it },
                    onReturnDelayChange = { returnDelay = it },
                    onSave = {
                        prefs.edit().apply {
                            putString("manual_url", manualUrl)
                            putString("return_url", returnUrl)
                            putInt("return_delay", returnDelay)
                            apply()
                        }
                        showSettings = false
                    },
                    onBack = { showSettings = false }
                )
            }
            currentUrl != null -> {
                WebViewScreen(
                    url = currentUrl!!,
                    returnUrl = returnUrl,
                    returnDelay = returnDelay,
                    onBack = {
                        currentUrl = null
                        lastScannedUrl = null
                    }
                )
            }
            else -> {
                Scaffold(
                    topBar = {
                        TopAppBar(
                            title = { Text("Scanear QR Code") },
                            actions = {
                                IconButton(onClick = { showPasswordDialog = true }) {
                                    Icon(Icons.Default.Settings, contentDescription = "Configurações")
                                }
                            },
                            colors = TopAppBarDefaults.topAppBarColors(
                                containerColor = MaterialTheme.colorScheme.primaryContainer,
                                titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer
                            )
                        )
                    }
                ) { paddingValues ->
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(paddingValues)
                    ) {
                        CameraPreview(
                            onQrCodeDetected = { url ->
                                if (url != lastScannedUrl && isValidUrl(url)) {
                                    lastScannedUrl = url
                                    currentUrl = url
                                }
                            }
                        )

                        Column(
                            modifier = Modifier
                                .align(Alignment.BottomCenter)
                                .fillMaxWidth()
                                .padding(16.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text(
                                text = "Aponte a câmera para um QR Code",
                                style = MaterialTheme.typography.bodyLarge,
                                color = MaterialTheme.colorScheme.onSurface
                            )

                            Button(
                                onClick = { currentUrl = manualUrl },
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Text("MANUAL")
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun PasswordDialog(
    onPasswordCorrect: () -> Unit,
    onDismiss: () -> Unit
) {
    var password by remember { mutableStateOf("") }
    var showError by remember { mutableStateOf(false) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Senha de Administrador") },
        text = {
            Column {
                OutlinedTextField(
                    value = password,
                    onValueChange = {
                        password = it
                        showError = false
                    },
                    label = { Text("Senha") },
                    singleLine = true,
                    isError = showError
                )
                if (showError) {
                    Text(
                        text = "Senha incorreta",
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
        },
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
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancelar")
            }
        }
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    manualUrl: String,
    returnUrl: String,
    returnDelay: Int,
    onManualUrlChange: (String) -> Unit,
    onReturnUrlChange: (String) -> Unit,
    onReturnDelayChange: (Int) -> Unit,
    onSave: () -> Unit,
    onBack: () -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Configurações") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Voltar")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer
                )
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "Configurações",
                style = MaterialTheme.typography.headlineSmall
            )

            OutlinedTextField(
                value = manualUrl,
                onValueChange = onManualUrlChange,
                label = { Text("URL Manual") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )

            OutlinedTextField(
                value = returnUrl,
                onValueChange = onReturnUrlChange,
                label = { Text("URL de Retorno (quando detectada, voltara ao scanner)") },
                placeholder = { Text("Ex: https://172.19.0.0/sucesso") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )

            OutlinedTextField(
                value = returnDelay.toString(),
                onValueChange = {
                    it.toIntOrNull()?.let { delay ->
                        if (delay in 0..60) onReturnDelayChange(delay)
                    }
                },
                label = { Text("Delay de Retorno (segundos)") },
                placeholder = { Text("7") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )

            Button(
                onClick = onSave,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Salvar")
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WebViewScreen(url: String, returnUrl: String, returnDelay: Int, onBack: () -> Unit) {
    var webView by remember { mutableStateOf<WebView?>(null) }

    BackHandler {
        if (webView?.canGoBack() == true) {
            webView?.goBack()
        } else {
            onBack()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Pagina Web") },
                navigationIcon = {
                    IconButton(onClick = {
                        if (webView?.canGoBack() == true) {
                            webView?.goBack()
                        } else {
                            onBack()
                        }
                    }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Voltar")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer
                )
            )
        }
    ) { paddingValues ->
        AndroidView(
            factory = { context ->
                WebView(context).apply {
                    webViewClient = object : WebViewClient() {
                        override fun onPageFinished(view: WebView?, url: String?) {
                            super.onPageFinished(view, url)
                            url?.let {
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
                    settings.loadWithOverviewMode = true
                    settings.useWideViewPort = true
                    settings.builtInZoomControls = true
                    settings.displayZoomControls = false
                    loadUrl(url)
                    webView = this
                }
            },
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        )
    }
}

@Composable
fun CameraPreview(onQrCodeDetected: (String) -> Unit) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val cameraProviderFuture = remember { ProcessCameraProvider.getInstance(context) }
    val executor = remember { Executors.newSingleThreadExecutor() }
    val barcodeScanner = remember { BarcodeScanning.getClient() }

    AndroidView(
        factory = { ctx ->
            val previewView = PreviewView(ctx)
            val cameraProvider = cameraProviderFuture.get()
            val preview = Preview.Builder().build()
            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA

            preview.setSurfaceProvider(previewView.surfaceProvider)

            val imageAnalysis = ImageAnalysis.Builder()
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()

            imageAnalysis.setAnalyzer(executor) { imageProxy ->
                processImageProxy(barcodeScanner, imageProxy, onQrCodeDetected)
            }

            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(
                    lifecycleOwner,
                    cameraSelector,
                    preview,
                    imageAnalysis
                )
            } catch (e: Exception) {
                Log.e("QRScanner", "Erro ao iniciar câmera", e)
            }

            previewView
        },
        modifier = Modifier.fillMaxSize()
    )
}

@androidx.camera.core.ExperimentalGetImage
private fun processImageProxy(
    barcodeScanner: com.google.mlkit.vision.barcode.BarcodeScanner,
    imageProxy: ImageProxy,
    onQrCodeDetected: (String) -> Unit
) {
    val mediaImage = imageProxy.image
    if (mediaImage != null) {
        val image = InputImage.fromMediaImage(
            mediaImage,
            imageProxy.imageInfo.rotationDegrees
        )

        barcodeScanner.process(image)
            .addOnSuccessListener { barcodes ->
                for (barcode in barcodes) {
                    when (barcode.valueType) {
                        Barcode.TYPE_URL -> {
                            barcode.url?.url?.let { url ->
                                onQrCodeDetected(url)
                            }
                        }
                        Barcode.TYPE_TEXT -> {
                            barcode.rawValue?.let { text ->
                                if (isValidUrl(text)) {
                                    onQrCodeDetected(text)
                                }
                            }
                        }
                    }
                }
            }
            .addOnCompleteListener {
                imageProxy.close()
            }
    } else {
        imageProxy.close()
    }
}

private fun isValidUrl(text: String): Boolean {
    return text.startsWith("http://", ignoreCase = true) ||
           text.startsWith("https://", ignoreCase = true)
}
