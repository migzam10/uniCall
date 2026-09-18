import 'package:dio/dio.dart';

import '../core/api_client.dart';
import '../models/app_user.dart';
import '../models/user_preferences.dart';
import '../models/user_profile.dart';

class MeData {
  const MeData({required this.user, required this.profile, required this.preferences});
  final AppUser user;
  final UserProfile profile;
  final UserPreferences preferences;
}

class UserRepository {
  UserRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<MeData> getMe() async {
    try {
      final response = await _apiClient.dio.get('/users/me');
      return MeData(
        user: AppUser.fromJson(response.data['user']),
        profile: UserProfile.fromJson(response.data['profile']),
        preferences: UserPreferences.fromJson(response.data['preferences']),
      );
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<UserProfile> updateProfile(UserProfile profile) async {
    try {
      final response = await _apiClient.dio.put('/users/me/profile', data: profile.toUpdateJson());
      return UserProfile.fromJson(response.data);
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<UserPreferences> updatePreferences(UserPreferences preferences) async {
    try {
      final response = await _apiClient.dio.put('/users/me/preferences', data: {
        'auto_translate_enabled': preferences.autoTranslateEnabled,
        'show_subtitles': preferences.showSubtitles,
        'show_avatar': preferences.showAvatar,
        'voice_output_enabled': preferences.voiceOutputEnabled,
        'voice_preference': preferences.voicePreference.toJson(),
      });
      return UserPreferences.fromJson(response.data);
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }
}
