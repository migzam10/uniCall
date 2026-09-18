import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/api_exception.dart';
import '../../core/providers.dart';
import '../../models/lsc_data.dart';
import 'lsc_admin_controller.dart';

class LscSignsScreen extends ConsumerStatefulWidget {
  const LscSignsScreen({super.key});

  @override
  ConsumerState<LscSignsScreen> createState() => _LscSignsScreenState();
}

class _LscSignsScreenState extends ConsumerState<LscSignsScreen> {
  String? _categoryFilter;

  Future<void> _showCreateDialog() async {
    final categories = await ref.read(lscAdminRepositoryProvider).listCategories();
    if (categories.isEmpty) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(const SnackBar(content: Text('Primero crea al menos una categoría.')));
      }
      return;
    }

    final wordController = TextEditingController();
    final meaningController = TextEditingController();
    final tagsController = TextEditingController();
    String selectedCategoryId = categories.first.id;

    final created = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (dialogContext, setDialogState) => AlertDialog(
          title: const Text('Nueva seña'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<String>(
                  initialValue: selectedCategoryId,
                  decoration: const InputDecoration(labelText: 'Categoría'),
                  items: categories.map((c) => DropdownMenuItem(value: c.id, child: Text(c.name))).toList(),
                  onChanged: (value) => setDialogState(() => selectedCategoryId = value!),
                ),
                const SizedBox(height: 12),
                TextField(controller: wordController, decoration: const InputDecoration(labelText: 'Palabra')),
                const SizedBox(height: 12),
                TextField(
                  controller: meaningController,
                  decoration: const InputDecoration(labelText: 'Significado'),
                  maxLines: 2,
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: tagsController,
                  decoration: const InputDecoration(labelText: 'Etiquetas (separadas por coma)'),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(dialogContext, false), child: const Text('Cancelar')),
            FilledButton(onPressed: () => Navigator.pop(dialogContext, true), child: const Text('Crear')),
          ],
        ),
      ),
    );

    if (created != true || wordController.text.trim().isEmpty || meaningController.text.trim().isEmpty) return;

    try {
      await ref.read(lscAdminRepositoryProvider).createSign(
            categoryId: selectedCategoryId,
            word: wordController.text.trim(),
            meaning: meaningController.text.trim(),
            tags: tagsController.text.trim().isEmpty ? null : tagsController.text.trim(),
          );
      ref.invalidate(lscSignsProvider(_categoryFilter));
    } on ApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(e.message), backgroundColor: Theme.of(context).colorScheme.error));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final categoriesAsync = ref.watch(lscCategoriesProvider);
    final signsAsync = ref.watch(lscSignsProvider(_categoryFilter));

    return Scaffold(
      appBar: AppBar(title: const Text('Señas LSC')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showCreateDialog,
        icon: const Icon(Icons.add),
        label: const Text('Nueva seña'),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: categoriesAsync.when(
              loading: () => const SizedBox.shrink(),
              error: (_, __) => const SizedBox.shrink(),
              data: (categories) => SizedBox(
                height: 40,
                child: ListView(
                  scrollDirection: Axis.horizontal,
                  children: [
                    _FilterChip(label: 'Todas', selected: _categoryFilter == null, onTap: () => setState(() => _categoryFilter = null)),
                    ...categories.map(
                      (c) => _FilterChip(
                        label: c.name,
                        selected: _categoryFilter == c.id,
                        onTap: () => setState(() => _categoryFilter = c.id),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          Expanded(
            child: signsAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (err, _) => Center(child: Text('Error: $err')),
              data: (signs) {
                if (signs.isEmpty) {
                  return const Center(child: Text('Todavía no hay señas en esta categoría.'));
                }
                return ListView.separated(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 96),
                  itemCount: signs.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (context, index) {
                    final sign = signs[index];
                    return Container(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: const Color(0xFFE1E5EA)),
                      ),
                      child: ListTile(
                        title: Text(sign.word, style: const TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Text('${sign.meaning} · v${sign.version}'),
                        trailing: _StatusBadge(status: sign.status),
                        onTap: () => context.push('/admin/lsc/signs/${sign.id}'),
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  const _FilterChip({required this.label, required this.selected, required this.onTap});
  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: ChoiceChip(label: Text(label), selected: selected, onSelected: (_) => onTap()),
    );
  }
}

class _StatusBadge extends StatelessWidget {
  const _StatusBadge({required this.status});
  final LscSignStatus status;

  @override
  Widget build(BuildContext context) {
    final color = switch (status) {
      LscSignStatus.draft => const Color(0xFF9AA3AD),
      LscSignStatus.published => const Color(0xFF2E7D32),
      LscSignStatus.archived => const Color(0xFFC62828),
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: color.withOpacity(0.12), borderRadius: BorderRadius.circular(20)),
      child: Text(status.label, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.w600)),
    );
  }
}
