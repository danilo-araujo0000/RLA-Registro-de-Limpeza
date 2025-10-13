package com.example.higiene.ui.screens

import android.net.Uri
import android.os.Handler
import android.os.Looper
import android.webkit.CookieManager
import android.webkit.WebView
import android.webkit.WebViewClient
import android.webkit.WebResourceRequest
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView
import com.example.higiene.ui.screens.TopBarButtons

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WebViewScreen(
    url: String,
    deviceId: String,
    returnUrl: String,
    returnDelay: Int,
    onBack: () -> Unit,
    onHomeClick: () -> Unit,
    onOpenSettings: () -> Unit
) {
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
                title = {
                    TopBarButtons(
                        onHomeClick = {
                            webView?.stopLoading()
                            onHomeClick()
                        },
                        onHomeLongClick = { onOpenSettings() },
                        onRefreshClick = { webView?.reload() }
                    )
                },
                actions = {
                    IconButton(onClick = { onOpenSettings() }) {
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
        AndroidView(
            factory = { context ->
                WebView(context).apply {
                    val sanitizedDeviceId = deviceId.trim()
                    val headers = if (sanitizedDeviceId.isNotEmpty()) {
                        mapOf("X-Device-Id" to sanitizedDeviceId)
                    } else {
                        emptyMap()
                    }
                    val cookieManager = CookieManager.getInstance()
                    cookieManager.setAcceptCookie(true)

                    fun setDeviceCookie(targetUrl: String?) {
                        if (sanitizedDeviceId.isEmpty() || targetUrl.isNullOrBlank()) return
                        val parsed = runCatching { Uri.parse(targetUrl) }.getOrNull() ?: return
                        val host = parsed.host ?: return
                        val scheme = parsed.scheme ?: "http"
                        val portSuffix = if (parsed.port != -1) ":${parsed.port}" else ""
                        val baseUrl = "$scheme://$host$portSuffix"
                        cookieManager.setCookie(baseUrl, "device_id=$sanitizedDeviceId")
                        cookieManager.flush()
                    }

                    setDeviceCookie(url)

                    webViewClient = object : WebViewClient() {
                        override fun shouldOverrideUrlLoading(
                            view: WebView?,
                            request: WebResourceRequest?
                        ): Boolean {
                            val targetUrl = request?.url?.toString()
                            setDeviceCookie(targetUrl)
                            return false
                        }

                        override fun onPageFinished(view: WebView?, url: String?) {
                            super.onPageFinished(view, url)
                            setDeviceCookie(url)
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
                    if (headers.isEmpty()) {
                        loadUrl(url)
                    } else {
                        loadUrl(url, headers)
                    }
                    webView = this
                }
            },
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        )
    }
}
