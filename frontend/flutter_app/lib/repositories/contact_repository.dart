import 'package:dio/dio.dart';

import '../core/api_client.dart';
import '../models/contact.dart';

class ContactRepository {
  ContactRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<List<UserSearchResult>> searchUsers(String query) async {
    try {
      final response = await _apiClient.dio.get('/contacts/search', queryParameters: {'q': query});
      return (response.data as List).map((e) => UserSearchResult.fromJson(e)).toList();
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<List<Contact>> listContacts() async {
    try {
      final response = await _apiClient.dio.get('/contacts');
      return (response.data as List).map((e) => Contact.fromJson(e)).toList();
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<void> removeContact(String contactUserId) async {
    try {
      await _apiClient.dio.delete('/contacts/$contactUserId');
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<void> sendRequest(String toUsername) async {
    try {
      await _apiClient.dio.post('/contacts/requests', data: {'to_username': toUsername});
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<List<ContactRequest>> listIncomingRequests() async {
    try {
      final response = await _apiClient.dio.get('/contacts/requests/incoming');
      return (response.data as List).map((e) => ContactRequest.fromJson(e)).toList();
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<List<ContactRequest>> listOutgoingRequests() async {
    try {
      final response = await _apiClient.dio.get('/contacts/requests/outgoing');
      return (response.data as List).map((e) => ContactRequest.fromJson(e)).toList();
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<void> acceptRequest(String requestId) async {
    try {
      await _apiClient.dio.post('/contacts/requests/$requestId/accept');
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<void> rejectRequest(String requestId) async {
    try {
      await _apiClient.dio.post('/contacts/requests/$requestId/reject');
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }
}
