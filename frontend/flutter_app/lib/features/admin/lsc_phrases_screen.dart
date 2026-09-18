import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'lsc_admin_controller.dart';

class LscPhrasesScreen extends ConsumerWidget {
  const LscPhrasesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final phrasesAsync = ref.watch(lscPhrasesProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Frases LSC')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/admin/lsc/phrases/new'),
        icon: const Icon(Icons.add),
        label: const Text('Nueva frase'),
      ),
      body: phrasesAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(child: Text('Error: $err')),
        data: (phrases) {
          if (phrases.isEmpty) {
            return const Center(child: Text('Todavía no hay frases documentadas.'));
          }
          return ListView.separated(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
            itemCount: phrases.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              final phrase = phrases[index];
              return Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: const Color(0xFFE1E5EA)),
                ),
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(phrase.text, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
                    const SizedBox(height: 6),
                    Wrap(
                      spacing: 6,
                      runSpacing: 6,
                      children: [
                        for (var i = 0; i < phrase.signs.length; i++) ...[
                          Chip(label: Text(phrase.signs[i].word), visualDensity: VisualDensity.compact),
                          if (i < phrase.signs.length - 1)
                            const Padding(
                              padding: EdgeInsets.symmetric(horizontal: 2),
                              child: Icon(Icons.arrow_forward, size: 14, color: Color(0xFF9AA3AD)),
                            ),
                        ],
                      ],
                    ),
                  ],
                ),
              );
            },
          );
        },
      ),
    );
  }
}
