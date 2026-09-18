import 'package:dio/dio.dart';

import '../core/api_client.dart';
import '../models/call_info.dart';

class CallRepository {
  CallRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<CallInfo> createCall() async {
    try {
      final response = await _apiClient.dio.post('/calls');
      return CallInfo.fromJson(response.data);
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<CallInfo> joinByCode(String code) async {
    try {
      final response = await _apiClient.dio.post('/calls/join', data: {'code': code.trim().toUpperCase()});
      return CallInfo.fromJson(response.data);
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<CallInfo> createDirectCall(String contactUserId) async {
    try {
      final response = await _apiClient.dio.post('/calls/direct', data: {'contact_user_id': contactUserId});
      return CallInfo.fromJson(response.data);
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<List<CallInvitation>> listPendingInvitations() async {
    try {
      final response = await _apiClient.dio.get('/calls/invitations');
      return (response.data as List).map((e) => CallInvitation.fromJson(e)).toList();
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<List<IceServerConfig>> getIceServers() async {
    try {
      final response = await _apiClient.dio.get('/calls/ice-servers');
      return (response.data['ice_servers'] as List).map((e) => IceServerConfig.fromJson(e)).toList();
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }
}
