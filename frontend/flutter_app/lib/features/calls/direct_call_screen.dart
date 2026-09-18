import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/api_exception.dart';
import '../../core/providers.dart';

class DirectCallScreen extends ConsumerStatefulWidget {
  const DirectCallScreen({super.key, required this.contactUserId, required this.contactName});

  final String contactUserId;
  final String contactName;

  @override
  ConsumerState<DirectCallScreen> createState() => _DirectCallScreenState();
}

class _DirectCallScreenState extends ConsumerState<DirectCallScreen> {
  String? _error;

  @override
  void initState() {
    super.initState();
    _start();
  }

  Future<void> _start() async {
    try {
      final call = await ref.read(callRepositoryProvider).createDirectCall(widget.contactUserId);
      if (mounted) {
        context.pushReplacement('/calls/room/${call.id}/${call.code}');
      }
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Center(
        child: _error != null
            ? Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.error_outline, color: Colors.white, size: 48),
                    const SizedBox(height: 16),
                    Text(_error!, style: const TextStyle(color: Colors.white), textAlign: TextAlign.center),
                    const SizedBox(height: 24),
                    ElevatedButton(onPressed: () => context.pop(), child: const Text('Volver')),
                  ],
                ),
              )
            : Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const CircularProgressIndicator(color: Colors.white),
                  const SizedBox(height: 16),
                  Text('Llamando a ${widget.contactName}...', style: const TextStyle(color: Colors.white)),
                ],
              ),
      ),
    );
  }
}
