package com.example.higiene.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

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
