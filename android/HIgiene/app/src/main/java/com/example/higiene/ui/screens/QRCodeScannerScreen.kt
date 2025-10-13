package com.example.higiene.ui.screens

import android.content.Context
import android.util.Log
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import com.example.higiene.ui.theme.BlueTheme
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.common.InputImage
import com.example.higiene.ui.screens.SettingsScreen
import com.example.higiene.ui.screens.WebViewScreen
import java.util.concurrent.Executors

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun QRCodeScannerApp() {
    val context = LocalContext.current
    val prefs = remember { context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE) }

    var currentUrl by remember { mutableStateOf<String?>(null) }
    var lastScannedUrl by remember { mutableStateOf<String?>(null) }
    var showSettings by remember { mutableStateOf(false) }

    var deviceId by remember { mutableStateOf(prefs.getString("device_id", "") ?: "") }
    var manualUrl by remember { mutableStateOf(prefs.getString("manual_url", "http://172.19.0.80:8000/salas") ?: "http://172.19.0.80:8000/salas") }
    var returnUrl by remember { mutableStateOf(prefs.getString("return_url", "http://172.19.0.80:8000/sucesso") ?: "http://172.19.0.80:8000/sucesso") }
    var returnDelay by remember { mutableStateOf(prefs.getInt("return_delay", 5)) }
    var showPasswordDialog by remember { mutableStateOf(false) }
    var showDeviceIdAlert by remember { mutableStateOf(false) }

    val openSettings: () -> Unit = { showPasswordDialog = true }
    val openManual: () -> Unit = {
        if (deviceId.isBlank()) {
            showDeviceIdAlert = true
        } else {
            currentUrl = manualUrl
        }
    }
    val refreshScanner: () -> Unit = {
        lastScannedUrl = null
    }

    val goToScanner: () -> Unit = {
        currentUrl = null
        lastScannedUrl = null
    }

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
                    deviceId = deviceId,
                    manualUrl = manualUrl,
                    returnUrl = returnUrl,
                    returnDelay = returnDelay,
                    onDeviceIdChange = { deviceId = it },
                    onManualUrlChange = { manualUrl = it },
                    onReturnUrlChange = { returnUrl = it },
                    onReturnDelayChange = { returnDelay = it },
                    onSave = {
                        val sanitizedDeviceId = deviceId.trim()
                        val sanitizedManualUrl = manualUrl.trim().ifEmpty { "http://172.19.0.80/" }
                        val sanitizedReturnUrl = returnUrl.trim()

                        prefs.edit().apply {
                            putString("device_id", sanitizedDeviceId)
                            putString("manual_url", sanitizedManualUrl)
                            putString("return_url", sanitizedReturnUrl)
                            putInt("return_delay", returnDelay)
                            apply()
                        }
                        deviceId = sanitizedDeviceId
                        manualUrl = sanitizedManualUrl
                        returnUrl = sanitizedReturnUrl
                        showSettings = false
                    },
                    onBack = { showSettings = false }
                )
            }
            showDeviceIdAlert -> {
                DeviceIdDialog(
                    onGoToSettings = {
                        showDeviceIdAlert = false
                        showPasswordDialog = true
                    },
                    onDismiss = { showDeviceIdAlert = false }
                )
            }
            currentUrl != null -> {
                WebViewScreen(
                    url = currentUrl!!,
                    deviceId = deviceId,
                    returnUrl = returnUrl,
                    returnDelay = returnDelay,
                    onBack = {
                        currentUrl = null
                        lastScannedUrl = null
                    },
                    onHomeClick = { goToScanner() },
                    onOpenSettings = { openSettings() }
                )
            }
            else -> {
                Scaffold(
                    topBar = {
                        TopAppBar(
                            title = {
                                TopBarButtons(
                                    onHomeClick = { goToScanner() },
                                    onHomeLongClick = { openSettings() },
                                    onRefreshClick = { refreshScanner() }
                                )
                            },
                            actions = {
                                IconButton(onClick = { openSettings() }) {
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
                                if (deviceId.isBlank()) {
                                    showDeviceIdAlert = true
                                    return@CameraPreview
                                }
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

                            if (deviceId.isBlank()) {
                                Text(
                                    text = "ID do dispositivo n~~ao configurado",
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = MaterialTheme.colorScheme.error
                                )
                            }

                            Button(
                                onClick = { openManual() },
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

@Composable
fun TopBarButtons(
    onHomeClick: () -> Unit,
    onHomeLongClick: () -> Unit,
    onRefreshClick: () -> Unit
) {
    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        Button(
            onClick = onHomeClick,
            modifier = Modifier.pointerInput(Unit) {
                detectTapGestures(
                    onLongPress = { onHomeLongClick() }
                )
            },
            colors = ButtonDefaults.buttonColors(
                containerColor = MaterialTheme.colorScheme.primary,
                contentColor = MaterialTheme.colorScheme.onPrimary
            ),
            shape = MaterialTheme.shapes.small
        ) {
            Text("HOME")
        }
        Button(
            onClick = onRefreshClick,
            colors = ButtonDefaults.buttonColors(
                containerColor = MaterialTheme.colorScheme.secondary,
                contentColor = MaterialTheme.colorScheme.onSecondary
            ),
            shape = MaterialTheme.shapes.small
        ) {
            Text("Atualizar")
        }
    }
}

@Composable
fun DeviceIdDialog(
    onGoToSettings: () -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Configurar device_ID") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    text = "Defina um ID exclusivo para este aparelho nas configurações. "
                )
            }
        },
        confirmButton = {
            Button(onClick = onGoToSettings) {
                Text("Configurações")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("voltar")
            }
        }
    )
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
