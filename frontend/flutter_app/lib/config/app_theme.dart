import 'package:flutter/material.dart';

/// Tema visual de la aplicación.
///
/// Decisiones de accesibilidad (sección 22 de la especificación):
/// - Contraste alto entre texto y fondo (AA/AAA de WCAG donde es posible).
/// - Áreas táctiles grandes (mínimo 48x48 lógico) para botones.
/// - Tipografía clara y tamaños base generosos.
/// - Los estados (llamando, mic activo, cámara activa) se comunican con
///   color + ícono + texto, nunca solo con color.
class AppTheme {
  AppTheme._();

  // Paleta base: azul accesible como color primario, con suficiente
  // contraste sobre blanco y negro.
  static const Color primary = Color(0xFF1755C7);
  static const Color primaryDark = Color(0xFF0E3A8A);
  static const Color secondary = Color(0xFF00897B);
  static const Color danger = Color(0xFFC62828);
  static const Color success = Color(0xFF2E7D32);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color background = Color(0xFFF5F7FA);
  static const Color textPrimary = Color(0xFF10151A);
  static const Color textSecondary = Color(0xFF3C4550);

  static ThemeData light() {
    final base = ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primary,
        primary: primary,
        secondary: secondary,
        error: danger,
        surface: surface,
        brightness: Brightness.light,
      ),
      scaffoldBackgroundColor: background,
    );

    return base.copyWith(
      textTheme: base.textTheme.apply(
        bodyColor: textPrimary,
        displayColor: textPrimary,
        fontSizeFactor: 1.05, // texto ligeramente más grande por defecto
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          minimumSize: const Size.fromHeight(56), // botones grandes
          textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: const Size.fromHeight(56),
          textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
          side: const BorderSide(color: primary, width: 2),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        ),
      ),
      iconTheme: const IconThemeData(size: 28),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surface,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 18),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFFC7CDD4)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: primary, width: 2),
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: surface,
        foregroundColor: textPrimary,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: textPrimary),
      ),
    );
  }
}

/// Colores de estado usados en la interfaz de videollamada, siempre
/// acompañados de ícono + texto (sección 22: no depender solo del color).
class StatusColors {
  StatusColors._();
  static const Color micOn = AppTheme.success;
  static const Color micOff = AppTheme.danger;
  static const Color cameraOn = AppTheme.success;
  static const Color cameraOff = AppTheme.danger;
  static const Color translationActive = AppTheme.secondary;
}
