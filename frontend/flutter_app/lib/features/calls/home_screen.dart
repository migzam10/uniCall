import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../models/user_role.dart';
import '../profile/profile_controller.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final meAsync = ref.watch(meProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Inicio'),
        actions: [
          if (meAsync.valueOrNull?.user.role == UserRole.administrador)
            IconButton(
              tooltip: 'Panel administrativo',
              icon: const Icon(Icons.admin_panel_settings_outlined),
              onPressed: () => context.push('/admin'),
            ),
          IconButton(
            tooltip: 'Configuración',
            icon: const Icon(Icons.settings_outlined),
            onPressed: () => context.push('/settings'),
          ),
          IconButton(
            tooltip: 'Mi perfil',
            icon: const Icon(Icons.person_outline),
            onPressed: () => context.push('/profile'),
          ),
        ],
      ),
      body: SafeArea(
        child: meAsync.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (err, _) => Center(child: Text('No se pudo cargar tu información: $err')),
          data: (me) => Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Hola, ${me.user.fullName.split(' ').first}',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text(me.user.role.label, style: Theme.of(context).textTheme.bodyLarge),
                const SizedBox(height: 32),
                Expanded(
                  child: GridView.count(
                    crossAxisCount: 2,
                    mainAxisSpacing: 16,
                    crossAxisSpacing: 16,
                    children: [
                      _HomeTile(
                        icon: Icons.contacts_outlined,
                        label: 'Contactos',
                        onTap: () => context.push('/contacts'),
                      ),
                      _HomeTile(
                        icon: Icons.video_call_outlined,
                        label: 'Nueva llamada',
                        onTap: () => context.push('/calls/new'),
                      ),
                      _HomeTile(
                        icon: Icons.link,
                        label: 'Unirse con código',
                        onTap: () => context.push('/calls/join'),
                      ),
                      _HomeTile(
                        icon: Icons.history,
                        label: 'Historial',
                        enabled: false,
                        onTap: () {},
                      ),
                    ],
                  ),
                ),
                Text(
                  'El historial de llamadas se habilita en una fase posterior.',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(color: const Color(0xFF3C4550)),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _HomeTile extends StatelessWidget {
  const _HomeTile({required this.icon, required this.label, required this.onTap, this.enabled = true});

  final IconData icon;
  final String label;
  final VoidCallback onTap;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    final color = enabled ? Theme.of(context).colorScheme.primary : const Color(0xFF9AA3AD);

    return Semantics(
      button: true,
      enabled: enabled,
      label: label,
      child: Opacity(
        opacity: enabled ? 1 : 0.55,
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: enabled ? onTap : null,
          child: Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE1E5EA)),
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(icon, size: 40, color: color),
                const SizedBox(height: 12),
                Text(label, style: TextStyle(fontWeight: FontWeight.w600, color: color)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
