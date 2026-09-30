import 'package:dio/dio.dart';

import '../core/api_client.dart';
import '../models/lsc_translation.dart';

class LscTranslationRepository {
  LscTranslationRepository(this._apiClient);

  final ApiClient _apiClient;

  /// Traduce texto en español a la secuencia de señas/animaciones LSC
  /// correspondiente (Fase 6). El motor NLP resuelve las palabras; el
  /// backend enriquece la respuesta con disponibilidad de animación 3D.
  Future<LscTranslationResult> translate(String text) async {
    try {
      final response = await _apiClient.dio.post('/lsc/translate', data: {'text': text});
      return LscTranslationResult.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }
}
