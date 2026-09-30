class LscCategory {
  const LscCategory({
    required this.id,
    required this.name,
    required this.slug,
    this.description,
    required this.isActive,
  });

  final String id;
  final String name;
  final String slug;
  final String? description;
  final bool isActive;

  factory LscCategory.fromJson(Map<String, dynamic> json) => LscCategory(
        id: json['id'] as String,
        name: json['name'] as String,
        slug: json['slug'] as String,
        description: json['description'] as String?,
        isActive: json['is_active'] as bool,
      );
}

enum LscSignStatus {
  draft,
  published,
  archived;

  static LscSignStatus fromJson(String value) =>
      LscSignStatus.values.firstWhere((v) => v.name == value, orElse: () => LscSignStatus.draft);

  String get label => switch (this) {
        LscSignStatus.draft => 'Borrador',
        LscSignStatus.published => 'Publicada',
        LscSignStatus.archived => 'Archivada',
      };
}

class LscSign {
  const LscSign({
    required this.id,
    required this.categoryId,
    required this.word,
    required this.meaning,
    this.description,
    this.tags,
    required this.status,
    required this.version,
    required this.isActive,
  });

  final String id;
  final String categoryId;
  final String word;
  final String meaning;
  final String? description;
  final String? tags;
  final LscSignStatus status;
  final int version;
  final bool isActive;

  factory LscSign.fromJson(Map<String, dynamic> json) => LscSign(
        id: json['id'] as String,
        categoryId: json['category_id'] as String,
        word: json['word'] as String,
        meaning: json['meaning'] as String,
        description: json['description'] as String?,
        tags: json['tags'] as String?,
        status: LscSignStatus.fromJson(json['status'] as String),
        version: json['version'] as int,
        isActive: json['is_active'] as bool,
      );
}

class LscVideo {
  const LscVideo({
    required this.id,
    required this.signId,
    required this.url,
    required this.originalFilename,
    required this.sizeBytes,
    required this.isActive,
  });

  final String id;
  final String signId;
  final String url;
  final String originalFilename;
  final int sizeBytes;
  final bool isActive;

  factory LscVideo.fromJson(Map<String, dynamic> json) => LscVideo(
        id: json['id'] as String,
        signId: json['sign_id'] as String,
        url: json['url'] as String,
        originalFilename: json['original_filename'] as String,
        sizeBytes: json['size_bytes'] as int,
        isActive: json['is_active'] as bool,
      );
}

class LscAnimation {
  const LscAnimation({
    required this.id,
    required this.signId,
    required this.url,
    required this.originalFilename,
    required this.sizeBytes,
    required this.isActive,
  });

  final String id;
  final String signId;
  final String url;
  final String originalFilename;
  final int sizeBytes;
  final bool isActive;

  factory LscAnimation.fromJson(Map<String, dynamic> json) => LscAnimation(
        id: json['id'] as String,
        signId: json['sign_id'] as String,
        url: json['url'] as String,
        originalFilename: json['original_filename'] as String,
        sizeBytes: json['size_bytes'] as int,
        isActive: json['is_active'] as bool,
      );
}

class LscSignWithVideos extends LscSign {
  const LscSignWithVideos({
    required super.id,
    required super.categoryId,
    required super.word,
    required super.meaning,
    super.description,
    super.tags,
    required super.status,
    required super.version,
    required super.isActive,
    required this.videos,
    required this.animations,
  });

  final List<LscVideo> videos;
  final List<LscAnimation> animations;

  factory LscSignWithVideos.fromJson(Map<String, dynamic> json) => LscSignWithVideos(
        id: json['id'] as String,
        categoryId: json['category_id'] as String,
        word: json['word'] as String,
        meaning: json['meaning'] as String,
        description: json['description'] as String?,
        tags: json['tags'] as String?,
        status: LscSignStatus.fromJson(json['status'] as String),
        version: json['version'] as int,
        isActive: json['is_active'] as bool,
        videos: (json['videos'] as List).map((e) => LscVideo.fromJson(e)).toList(),
        animations: (json['animations'] as List).map((e) => LscAnimation.fromJson(e)).toList(),
      );
}

class LscPhraseSignRef {
  const LscPhraseSignRef({required this.signId, required this.word, required this.position});
  final String signId;
  final String word;
  final int position;

  factory LscPhraseSignRef.fromJson(Map<String, dynamic> json) => LscPhraseSignRef(
        signId: json['sign_id'] as String,
        word: json['word'] as String,
        position: json['position'] as int,
      );
}

class LscPhrase {
  const LscPhrase({
    required this.id,
    required this.text,
    this.description,
    required this.isActive,
    required this.signs,
  });

  final String id;
  final String text;
  final String? description;
  final bool isActive;
  final List<LscPhraseSignRef> signs;

  factory LscPhrase.fromJson(Map<String, dynamic> json) => LscPhrase(
        id: json['id'] as String,
        text: json['text'] as String,
        description: json['description'] as String?,
        isActive: json['is_active'] as bool,
        signs: (json['signs'] as List).map((e) => LscPhraseSignRef.fromJson(e)).toList(),
      );
}
