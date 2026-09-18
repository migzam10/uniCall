import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/api_exception.dart';
import '../../core/providers.dart';
import '../../models/contact.dart';
import 'contacts_controller.dart';

class ContactsScreen extends ConsumerStatefulWidget {
  const ContactsScreen({super.key});

  @override
  ConsumerState<ContactsScreen> createState() => _ContactsScreenState();
}

class _ContactsScreenState extends ConsumerState<ContactsScreen> with SingleTickerProviderStateMixin {
  late final TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Contactos'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Mis contactos'),
            Tab(text: 'Solicitudes'),
            Tab(text: 'Buscar'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: const [
          _MyContactsTab(),
          _RequestsTab(),
          _SearchTab(),
        ],
      ),
    );
  }
}

class _MyContactsTab extends ConsumerWidget {
  const _MyContactsTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final contactsAsync = ref.watch(contactsListProvider);

    return contactsAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, _) => Center(child: Text('No se pudieron cargar los contactos: $err')),
      data: (contacts) {
        if (contacts.isEmpty) {
          return const _EmptyState(
            icon: Icons.people_outline,
            message: 'Todavía no tienes contactos.\nBúscalos en la pestaña "Buscar".',
          );
        }
        return ListView.separated(
          padding: const EdgeInsets.all(16),
          itemCount: contacts.length,
          separatorBuilder: (_, __) => const SizedBox(height: 8),
          itemBuilder: (context, index) {
            final contact = contacts[index];
            return _ContactTile(contact: contact);
          },
        );
      },
    );
  }
}

class _ContactTile extends ConsumerWidget {
  const _ContactTile({required this.contact});
  final Contact contact;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE1E5EA)),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: CircleAvatar(
          backgroundColor: Theme.of(context).colorScheme.primary,
          child: Text(contact.fullName.isNotEmpty ? contact.fullName[0].toUpperCase() : '?',
              style: const TextStyle(color: Colors.white)),
        ),
        title: Text(contact.fullName, style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Text('@${contact.username} · ${contact.role.label}'),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              tooltip: 'Llamar',
              icon: const Icon(Icons.video_call, color: Color(0xFF1755C7)),
              onPressed: () => context.push('/calls/direct/${contact.id}/${Uri.encodeComponent(contact.fullName)}'),
            ),
            IconButton(
              tooltip: 'Eliminar contacto',
              icon: const Icon(Icons.person_remove_outlined, color: Color(0xFFC62828)),
              onPressed: () async {
                final confirmed = await showDialog<bool>(
                  context: context,
                  builder: (context) => AlertDialog(
                    title: const Text('Eliminar contacto'),
                    content: Text('¿Quitar a ${contact.fullName} de tus contactos?'),
                    actions: [
                      TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancelar')),
                      TextButton(onPressed: () => Navigator.pop(context, true), child: const Text('Eliminar')),
                    ],
                  ),
                );
                if (confirmed == true) {
                  await ref.read(contactRepositoryProvider).removeContact(contact.id);
                  ref.invalidate(contactsListProvider);
                }
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _RequestsTab extends ConsumerWidget {
  const _RequestsTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final incomingAsync = ref.watch(incomingRequestsProvider);
    final outgoingAsync = ref.watch(outgoingRequestsProvider);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text('Recibidas', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        incomingAsync.when(
          loading: () => const Padding(padding: EdgeInsets.all(16), child: CircularProgressIndicator()),
          error: (err, _) => Text('Error: $err'),
          data: (requests) => requests.isEmpty
              ? const Padding(padding: EdgeInsets.symmetric(vertical: 8), child: Text('Sin solicitudes recibidas.'))
              : Column(children: requests.map((r) => _IncomingRequestTile(request: r)).toList()),
        ),
        const SizedBox(height: 24),
        Text('Enviadas', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        outgoingAsync.when(
          loading: () => const Padding(padding: EdgeInsets.all(16), child: CircularProgressIndicator()),
          error: (err, _) => Text('Error: $err'),
          data: (requests) => requests.isEmpty
              ? const Padding(padding: EdgeInsets.symmetric(vertical: 8), child: Text('Sin solicitudes enviadas.'))
              : Column(
                  children: requests
                      .map((r) => ListTile(
                            leading: const Icon(Icons.hourglass_top_outlined),
                            title: Text(r.otherFullName),
                            subtitle: Text('@${r.otherUsername} · pendiente'),
                          ))
                      .toList(),
                ),
        ),
      ],
    );
  }
}

class _IncomingRequestTile extends ConsumerWidget {
  const _IncomingRequestTile({required this.request});
  final ContactRequest request;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE1E5EA)),
      ),
      child: ListTile(
        title: Text(request.otherFullName, style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Text('@${request.otherUsername}'),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              tooltip: 'Aceptar',
              icon: const Icon(Icons.check_circle, color: Color(0xFF2E7D32)),
              onPressed: () async {
                await ref.read(contactRepositoryProvider).acceptRequest(request.id);
                ref.invalidate(incomingRequestsProvider);
                ref.invalidate(contactsListProvider);
              },
            ),
            IconButton(
              tooltip: 'Rechazar',
              icon: const Icon(Icons.cancel, color: Color(0xFFC62828)),
              onPressed: () async {
                await ref.read(contactRepositoryProvider).rejectRequest(request.id);
                ref.invalidate(incomingRequestsProvider);
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _SearchTab extends ConsumerStatefulWidget {
  const _SearchTab();

  @override
  ConsumerState<_SearchTab> createState() => _SearchTabState();
}

class _SearchTabState extends ConsumerState<_SearchTab> {
  final _controller = TextEditingController();
  String _query = '';

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final resultsAsync = ref.watch(userSearchProvider(_query));

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextField(
            controller: _controller,
            decoration: const InputDecoration(
              labelText: 'Buscar por nombre o usuario',
              prefixIcon: Icon(Icons.search),
            ),
            onChanged: (value) => setState(() => _query = value),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: resultsAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (err, _) => Center(child: Text('Error: $err')),
              data: (results) {
                if (_query.trim().length < 2) {
                  return const _EmptyState(icon: Icons.search, message: 'Escribe al menos 2 caracteres.');
                }
                if (results.isEmpty) {
                  return const _EmptyState(icon: Icons.person_search_outlined, message: 'No se encontraron usuarios.');
                }
                return ListView.separated(
                  itemCount: results.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (context, index) {
                    final user = results[index];
                    return Container(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: const Color(0xFFE1E5EA)),
                      ),
                      child: ListTile(
                        title: Text(user.fullName, style: const TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Text('@${user.username} · ${user.role.label}'),
                        trailing: IconButton(
                          tooltip: 'Agregar contacto',
                          icon: const Icon(Icons.person_add_alt_1, color: Color(0xFF1755C7)),
                          onPressed: () async {
                            try {
                              await ref.read(contactRepositoryProvider).sendRequest(user.username);
                              if (context.mounted) {
                                ScaffoldMessenger.of(context)
                                    .showSnackBar(SnackBar(content: Text('Solicitud enviada a ${user.fullName}')));
                              }
                              ref.invalidate(outgoingRequestsProvider);
                            } on ApiException catch (e) {
                              if (context.mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(content: Text(e.message), backgroundColor: Theme.of(context).colorScheme.error),
                                );
                              }
                            }
                          },
                        ),
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

class _EmptyState extends StatelessWidget {
  const _EmptyState({required this.icon, required this.message});
  final IconData icon;
  final String message;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 48, color: const Color(0xFF9AA3AD)),
            const SizedBox(height: 12),
            Text(message, textAlign: TextAlign.center, style: const TextStyle(color: Color(0xFF3C4550))),
          ],
        ),
      ),
    );
  }
}
