import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/providers.dart';
import '../../models/call_info.dart';

class CreateCallScreen extends ConsumerStatefulWidget {
  const CreateCallScreen({super.key});

  @override
  ConsumerState<CreateCallScreen> createState() => _CreateCallScreenState();
}

class _CreateCallScreenState extends ConsumerState<CreateCallScreen> {
  CallInfo? _call;
  String? _error;

  @override
  void initState() {
    super.initState();
    _createCall();
  }

  Future<void> _createCall() async {
    try {
      final call = await ref.read(callRepositoryProvider).createCall();
      setState(() => _call = call);
    } catch (e) {
      setState(() => _error = 'No se pudo crear la llamada. Intenta nuevamente.');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nueva llamada')),
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: _error != null
                ? Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error))
                : _call == null
                    ? const CircularProgressIndicator()
                    : ConstrainedBox(
                        constraints: const BoxConstraints(maxWidth: 420),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.video_call, size: 56, color: Color(0xFF1755C7)),
                            const SizedBox(height: 16),
                            Text('Comparte este código', style: Theme.of(context).textTheme.titleLarge),
                            const SizedBox(height: 8),
                            Text(
                              'La otra persona debe ingresarlo en "Unirse con código"',
                              textAlign: TextAlign.center,
                              style: Theme.of(context).textTheme.bodyMedium,
                            ),
                            const SizedBox(height: 24),
                            Container(
                              padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(16),
                                border: Border.all(color: const Color(0xFF1755C7), width: 2),
                              ),
                              child: Text(
                                _call!.code,
                                style: const TextStyle(
                                  fontSize: 36,
                                  fontWeight: FontWeight.bold,
                                  letterSpacing: 4,
                                  color: Color(0xFF1755C7),
                                ),
                              ),
                            ),
                            const SizedBox(height: 16),
                            OutlinedButton.icon(
                              onPressed: () {
                                Clipboard.setData(ClipboardData(text: _call!.code));
                                ScaffoldMessenger.of(context)
                                    .showSnackBar(const SnackBar(content: Text('Código copiado')));
                              },
                              icon: const Icon(Icons.copy),
                              label: const Text('Copiar código'),
                            ),
                            const SizedBox(height: 24),
                            ElevatedButton.icon(
                              onPressed: () => context.pushReplacement('/calls/room/${_call!.id}/${_call!.code}'),
                              icon: const Icon(Icons.videocam),
                              label: const Text('Entrar a la llamada'),
                            ),
                          ],
                        ),
                      ),
          ),
        ),
      ),
    );
  }
}
