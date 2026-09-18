import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class AdminHomeScreen extends StatelessWidget {
  const AdminHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Panel administrativo')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text('Datos de Lengua de Señas Colombiana', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 4),
              Text(
                'Gestiona el material documentado que alimentará el reconocimiento de LSC.',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 20),
              _AdminTile(
                icon: Icons.category_outlined,
                title: 'Categorías',
                subtitle: 'Saludos, personas, lugares, acciones...',
                onTap: () => context.push('/admin/lsc/categories'),
              ),
              const SizedBox(height: 12),
              _AdminTile(
                icon: Icons.front_hand_outlined,
                title: 'Señas',
                subtitle: 'Palabras, significados, videos de referencia',
                onTap: () => context.push('/admin/lsc/signs'),
              ),
              const SizedBox(height: 12),
              _AdminTile(
                icon: Icons.short_text_outlined,
                title: 'Frases',
                subtitle: 'Secuencias de señas que forman una frase',
                onTap: () => context.push('/admin/lsc/phrases'),
              ),
              const SizedBox(height: 12),
              const _AdminTile(
                icon: Icons.people_alt_outlined,
                title: 'Usuarios',
                subtitle: 'Próximamente: administrar cuentas y roles',
                enabled: false,
              ),
              const SizedBox(height: 12),
              const _AdminTile(
                icon: Icons.model_training_outlined,
                title: 'Modelos de IA',
                subtitle: 'Próximamente: datasets, versiones, métricas',
                enabled: false,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _AdminTile extends StatelessWidget {
  const _AdminTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    this.onTap,
    this.enabled = true,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback? onTap;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    final color = enabled ? Theme.of(context).colorScheme.primary : const Color(0xFF9AA3AD);

    return Opacity(
      opacity: enabled ? 1 : 0.55,
      child: Material(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        child: InkWell(
          borderRadius: BorderRadius.circular(14),
          onTap: enabled ? onTap : null,
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(borderRadius: BorderRadius.circular(14), border: Border.all(color: const Color(0xFFE1E5EA))),
            child: Row(
              children: [
                Icon(icon, color: color, size: 32),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(title, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16)),
                      const SizedBox(height: 2),
                      Text(subtitle, style: Theme.of(context).textTheme.bodySmall),
                    ],
                  ),
                ),
                if (enabled) const Icon(Icons.chevron_right, color: Color(0xFF9AA3AD)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
