import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/providers.dart';
import '../../models/user_preferences.dart';
import '../profile/profile_controller.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  Future<void> _update(WidgetRef ref, UserPreferences updated) async {
    await ref.read(userRepositoryProvider).updatePreferences(updated);
    ref.invalidate(meProvider);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final meAsync = ref.watch(meProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Configuración')),
      body: meAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(child: Text('No se pudo cargar la configuración: $err')),
        data: (me) {
          final prefs = me.preferences;
          return ListView(
            padding: const EdgeInsets.symmetric(vertical: 16),
            children: [
              const _SectionHeader('Traducción automática'),
              SwitchListTile(
                title: const Text('Activar traducción automáticamente'),
                subtitle: const Text('Se inicia sola al entrar a una videollamada'),
                value: prefs.autoTranslateEnabled,
                onChanged: (v) => _update(ref, prefs.copyWith(autoTranslateEnabled: v)),
              ),
              SwitchListTile(
                title: const Text('Mostrar texto de apoyo'),
                subtitle: const Text('Subtítulos de lo que se está traduciendo'),
                value: prefs.showSubtitles,
                onChanged: (v) => _update(ref, prefs.copyWith(showSubtitles: v)),
              ),
              SwitchListTile(
                title: const Text('Mostrar avatar 3D'),
                subtitle: const Text('Representación en LSC de lo que dice la persona oyente'),
                value: prefs.showAvatar,
                onChanged: (v) => _update(ref, prefs.copyWith(showAvatar: v)),
              ),
              const Divider(height: 32),
              const _SectionHeader('Voz de traducción'),
              SwitchListTile(
                title: const Text('Convertir LSC a voz'),
                subtitle: const Text('Cuando la persona sorda hace señas, se reproduce en voz'),
                value: prefs.voiceOutputEnabled,
                onChanged: (v) => _update(ref, prefs.copyWith(voiceOutputEnabled: v)),
              ),
              RadioListTile<VoicePreference>(
                title: const Text('Voz femenina'),
                value: VoicePreference.femenina,
                groupValue: prefs.voicePreference,
                onChanged: (v) => _update(ref, prefs.copyWith(voicePreference: v)),
              ),
              RadioListTile<VoicePreference>(
                title: const Text('Voz masculina'),
                value: VoicePreference.masculina,
                groupValue: prefs.voicePreference,
                onChanged: (v) => _update(ref, prefs.copyWith(voicePreference: v)),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader(this.title);
  final String title;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
      child: Text(
        title,
        style: Theme.of(context)
            .textTheme
            .titleSmall
            ?.copyWith(color: Theme.of(context).colorScheme.primary, fontWeight: FontWeight.w700),
      ),
    );
  }
}
