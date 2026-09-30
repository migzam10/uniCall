class LscTranslationItem {
  const LscTranslationItem({
    required this.word,
    this.signId,
    required this.foundInDb,
    required this.hasAnimation,
    this.animationUrl,
  });

  final String word;
  final String? signId;
  final bool foundInDb;
  final bool hasAnimation;
  final String? animationUrl;

  factory LscTranslationItem.fromJson(Map<String, dynamic> json) => LscTranslationItem(
        word: json['word'] as String,
        signId: json['sign_id'] as String?,
        foundInDb: json['found_in_db'] as bool,
        hasAnimation: json['has_animation'] as bool,
        animationUrl: json['animation_url'] as String?,
      );
}

class LscTranslationResult {
  const LscTranslationResult({
    required this.originalText,
    required this.sequence,
    required this.complete,
  });

  final String originalText;
  final List<LscTranslationItem> sequence;
  // False si alguna palabra no tiene seña documentada o animación cargada
  // (sección 29, "nunca inventar"): la UI debe avisar que la traducción es
  // incompleta en vez de simular que todo se tradujo.
  final bool complete;

  factory LscTranslationResult.fromJson(Map<String, dynamic> json) => LscTranslationResult(
        originalText: json['original_text'] as String,
        sequence: (json['sequence'] as List).map((e) => LscTranslationItem.fromJson(e)).toList(),
        complete: json['complete'] as bool,
      );
}
