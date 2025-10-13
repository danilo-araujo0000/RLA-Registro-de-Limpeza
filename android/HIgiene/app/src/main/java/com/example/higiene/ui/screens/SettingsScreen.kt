package com.example.higiene.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    deviceId: String,
    manualUrl: String,
    returnUrl: String,
    returnDelay: Int,
    onDeviceIdChange: (String) -> Unit,
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
                value = deviceId,
                onValueChange = onDeviceIdChange,
                label = { Text("ID do Dispositivo") },
                placeholder = { Text("Ex: tablet-DML-1") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
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
                label = { Text("URL de Retorno (quando detectada, voltará ao scanner)") },
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
                label = { Text("Delay de Retorno (segundos max 60)") },
                placeholder = { Text("5") },
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
