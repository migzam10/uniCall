import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';

import '../core/api_client.dart';
import '../models/user_preferences.dart';

class SpeechRepository {
  SpeechRepository(this._apiClient);

  final ApiClient _apiClient;

  /// Envía audio grabado (WAV) y devuelve el texto transcrito.
  Future<String> transcribe(String audioFilePath) async {
    try {
      final formData = FormData.fromMap({
        'audio': await MultipartFile.fromFile(audioFilePath, filename: 'audio.wav'),
      });
      final response = await _apiClient.dio.post('/speech/transcribe', data: formData);
      return response.data['text'] as String;
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  /// Sintetiza texto a voz y devuelve los bytes de audio WAV listos para
  /// reproducir.
  Future<Uint8List> synthesize(String text, VoicePreference voice) async {
    try {
      final response = await _apiClient.dio.post('/speech/synthesize', data: {
        'text': text,
        'voice': voice.toJson(),
      });
      final base64Audio = response.data['audio_base64'] as String;
      return base64Decode(base64Audio);
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }
}
