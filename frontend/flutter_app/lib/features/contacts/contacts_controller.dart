import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/providers.dart';
import '../../models/contact.dart';

final contactsListProvider = FutureProvider.autoDispose<List<Contact>>((ref) async {
  return ref.watch(contactRepositoryProvider).listContacts();
});

final incomingRequestsProvider = FutureProvider.autoDispose<List<ContactRequest>>((ref) async {
  return ref.watch(contactRepositoryProvider).listIncomingRequests();
});

final outgoingRequestsProvider = FutureProvider.autoDispose<List<ContactRequest>>((ref) async {
  return ref.watch(contactRepositoryProvider).listOutgoingRequests();
});

final userSearchProvider = FutureProvider.autoDispose.family<List<UserSearchResult>, String>((ref, query) async {
  if (query.trim().length < 2) return [];
  return ref.watch(contactRepositoryProvider).searchUsers(query.trim());
});
