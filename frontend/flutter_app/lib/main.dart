import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'config/app_router.dart';
import 'config/app_theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  FlutterError.onError = (details) {
    FlutterError.presentError(details);
    debugPrint('[FlutterError] ${details.exceptionAsString()}');
  };

  PlatformDispatcher.instance.onError = (error, stack) {
    debugPrint('[UncaughtPlatformError] $error\n$stack');
    return true; // Evita que un error asíncrono no capturado cierre abruptamente la app
  };

  runApp(const ProviderScope(child: LscApp()));
}

class LscApp extends ConsumerWidget {
  const LscApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'LSC Videollamadas Accesibles',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      routerConfig: router,
      // Facilita pruebas con lectores de pantalla y permite escalar el
      // texto del sistema sin romper el layout (sección 22: accesibilidad).
      builder: (context, child) {
        final mediaQuery = MediaQuery.of(context);
        return MediaQuery(
          data: mediaQuery.copyWith(
            textScaler: mediaQuery.textScaler.clamp(minScaleFactor: 1.0, maxScaleFactor: 1.4),
          ),
          child: child!,
        );
      },
    );
  }
}
