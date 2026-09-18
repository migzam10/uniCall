enum VoicePreference {
  masculina,
  femenina;

  static VoicePreference fromJson(String value) =>
      VoicePreference.values.firstWhere((v) => v.name == value, orElse: () => VoicePreference.femenina);

  String toJson() => name;
}

class UserPreferences {
  const UserPreferences({
    required this.preferredLanguage,
    required this.signLanguage,
    required this.autoTranslateEnabled,
    required this.showSubtitles,
    required this.showAvatar,
    required this.voiceOutputEnabled,
    required this.voicePreference,
  });

  final String preferredLanguage;
  final String signLanguage;
  final bool autoTranslateEnabled;
  final bool showSubtitles;
  final bool showAvatar;
  final bool voiceOutputEnabled;
  final VoicePreference voicePreference;

  factory UserPreferences.fromJson(Map<String, dynamic> json) => UserPreferences(
        preferredLanguage: json['preferred_language'] as String,
        signLanguage: json['sign_language'] as String,
        autoTranslateEnabled: json['auto_translate_enabled'] as bool,
        showSubtitles: json['show_subtitles'] as bool,
        showAvatar: json['show_avatar'] as bool,
        voiceOutputEnabled: json['voice_output_enabled'] as bool,
        voicePreference: VoicePreference.fromJson(json['voice_preference'] as String),
      );

  UserPreferences copyWith({
    bool? autoTranslateEnabled,
    bool? showSubtitles,
    bool? showAvatar,
    bool? voiceOutputEnabled,
    VoicePreference? voicePreference,
  }) =>
      UserPreferences(
        preferredLanguage: preferredLanguage,
        signLanguage: signLanguage,
        autoTranslateEnabled: autoTranslateEnabled ?? this.autoTranslateEnabled,
        showSubtitles: showSubtitles ?? this.showSubtitles,
        showAvatar: showAvatar ?? this.showAvatar,
        voiceOutputEnabled: voiceOutputEnabled ?? this.voiceOutputEnabled,
        voicePreference: voicePreference ?? this.voicePreference,
      );
}
