import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/api_exception.dart';
import '../../core/providers.dart';
import '../../models/lsc_data.dart';
import 'lsc_admin_controller.dart';

class LscCreatePhraseScreen extends ConsumerStatefulWidget {
  const LscCreatePhraseScreen({super.key});

  @override
  ConsumerState<LscCreatePhraseScreen> createState() => _LscCreatePhraseScreenState();
}

class _LscCreatePhraseScreenState extends ConsumerState<LscCreatePhraseScreen> {
  final _textController = TextEditingController();
  final List<LscSign> _sequence = [];
  bool _saving = false;

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  Future<void> _pickSign() async {
    final allSigns = await ref.read(lscAdminRepositoryProvider).listSigns();
    if (!mounted) return;

    final selected = await showModalBottomSheet<LscSign>(
      context: context,
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.6,
        builder: (context, scrollController) => ListView.builder(
          controller: scrollController,
          padding: const EdgeInsets.all(16),
          itemCount: allSigns.length,
          itemBuilder: (context, index) {
            final sign = allSigns[index];
            return ListTile(
              title: Text(sign.word),
              subtitle: Text(sign.meaning),
              onTap: () => Navigator.pop(context, sign),
            );
          },
        ),
      ),
    );

    if (selected != null) {
      setState(() => _sequence.add(selected));
    }
  }

  Future<void> _save() async {
    if (_textController.text.trim().isEmpty || _sequence.isEmpty) return;

    setState(() => _saving = true);
    try {
      final signsPayload = [
        for (var i = 0; i < _sequence.length; i++) {'sign_id': _sequence[i].id, 'position': i},
      ];
      await ref.read(lscAdminRepositoryProvider).createPhrase(
            _textController.text.trim(),
            null,
            signsPayload,
          );
      ref.invalidate(lscPhrasesProvider);
      if (mounted) context.pop();
    } on ApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(e.message), backgroundColor: Theme.of(context).colorScheme.error));
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nueva frase')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextField(
                controller: _textController,
                decoration: const InputDecoration(labelText: 'Texto de la frase en español'),
              ),
              const SizedBox(height: 20),
              Row(
                children: [
                  Text('Secuencia de señas', style: Theme.of(context).textTheme.titleMedium),
                  const Spacer(),
                  OutlinedButton.icon(
                    onPressed: _pickSign,
                    icon: const Icon(Icons.add),
                    label: const Text('Agregar seña'),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              if (_sequence.isEmpty)
                const Text('Agrega al menos una seña, en el orden en que se realizan.')
              else
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    for (var i = 0; i < _sequence.length; i++)
                      Chip(
                        label: Text('${i + 1}. ${_sequence[i].word}'),
                        onDeleted: () => setState(() => _sequence.removeAt(i)),
                      ),
                  ],
                ),
              const Spacer(),
              ElevatedButton(
                onPressed: _saving ? null : _save,
                child: _saving
                    ? const SizedBox(
                        height: 24, width: 24, child: CircularProgressIndicator(strokeWidth: 2.5, color: Colors.white))
                    : const Text('Guardar frase'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
