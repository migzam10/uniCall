import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/api_exception.dart';
import '../../core/providers.dart';

class JoinCallScreen extends ConsumerStatefulWidget {
  const JoinCallScreen({super.key});

  @override
  ConsumerState<JoinCallScreen> createState() => _JoinCallScreenState();
}

class _JoinCallScreenState extends ConsumerState<JoinCallScreen> {
  final _controller = TextEditingController();
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _join() async {
    final code = _controller.text.trim();
    if (code.isEmpty) return;

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final call = await ref.read(callRepositoryProvider).joinByCode(code);
      if (mounted) {
        context.pushReplacement('/calls/room/${call.id}/${call.code}');
      }
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Unirse con código')),
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.link, size: 56, color: Color(0xFF1755C7)),
                  const SizedBox(height: 16),
                  Text('Ingresa el código de la llamada', style: Theme.of(context).textTheme.titleLarge),
                  const SizedBox(height: 24),
                  TextField(
                    controller: _controller,
                    textCapitalization: TextCapitalization.characters,
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 28, letterSpacing: 4, fontWeight: FontWeight.bold),
                    maxLength: 8,
                    decoration: InputDecoration(
                      counterText: '',
                      errorText: _error,
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    onSubmitted: (_) => _join(),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: _loading ? null : _join,
                    child: _loading
                        ? const SizedBox(
                            height: 24, width: 24, child: CircularProgressIndicator(strokeWidth: 2.5, color: Colors.white))
                        : const Text('Unirse a la llamada'),
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
