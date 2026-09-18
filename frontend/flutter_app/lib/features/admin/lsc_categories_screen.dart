import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/api_exception.dart';
import '../../core/providers.dart';
import 'lsc_admin_controller.dart';

class LscCategoriesScreen extends ConsumerWidget {
  const LscCategoriesScreen({super.key});

  Future<void> _showCreateDialog(BuildContext context, WidgetRef ref) async {
    final nameController = TextEditingController();
    final descController = TextEditingController();

    final created = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Nueva categoría'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(controller: nameController, decoration: const InputDecoration(labelText: 'Nombre')),
            const SizedBox(height: 12),
            TextField(
              controller: descController,
              decoration: const InputDecoration(labelText: 'Descripción (opcional)'),
              maxLines: 2,
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Crear')),
        ],
      ),
    );

    if (created != true || nameController.text.trim().isEmpty) return;

    try {
      await ref
          .read(lscAdminRepositoryProvider)
          .createCategory(nameController.text.trim(), descController.text.trim().isEmpty ? null : descController.text.trim());
      ref.invalidate(lscCategoriesProvider);
    } on ApiException catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(e.message), backgroundColor: Theme.of(context).colorScheme.error));
      }
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final categoriesAsync = ref.watch(lscCategoriesProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Categorías LSC')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showCreateDialog(context, ref),
        icon: const Icon(Icons.add),
        label: const Text('Nueva categoría'),
      ),
      body: categoriesAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(child: Text('Error: $err')),
        data: (categories) {
          if (categories.isEmpty) {
            return const Center(child: Text('Todavía no hay categorías.'));
          }
          return ListView.separated(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
            itemCount: categories.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              final category = categories[index];
              return Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: const Color(0xFFE1E5EA)),
                ),
                child: ListTile(
                  title: Text(category.name, style: const TextStyle(fontWeight: FontWeight.w600)),
                  subtitle: Text(category.description ?? category.slug),
                  trailing: Switch(
                    value: category.isActive,
                    onChanged: (value) async {
                      await ref.read(lscAdminRepositoryProvider).setCategoryActive(category.id, value);
                      ref.invalidate(lscCategoriesProvider);
                    },
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
