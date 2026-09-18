enum CallStatus {
  waiting,
  active,
  ended,
  expired;

  static CallStatus fromJson(String value) =>
      CallStatus.values.firstWhere((v) => v.name == value, orElse: () => CallStatus.waiting);
}

class CallInfo {
  const CallInfo({
    required this.id,
    required this.code,
    required this.status,
    required this.createdById,
    required this.createdAt,
    required this.expiresAt,
  });

  final String id;
  final String code;
  final CallStatus status;
  final String createdById;
  final DateTime createdAt;
  final DateTime expiresAt;

  factory CallInfo.fromJson(Map<String, dynamic> json) => CallInfo(
        id: json['id'] as String,
        code: json['code'] as String,
        status: CallStatus.fromJson(json['status'] as String),
        createdById: json['created_by_id'] as String,
        createdAt: DateTime.parse(json['created_at'] as String),
        expiresAt: DateTime.parse(json['expires_at'] as String),
      );
}

class CallInvitation {
  const CallInvitation({
    required this.id,
    required this.callId,
    required this.callCode,
    required this.fromUsername,
    required this.fromFullName,
  });

  final String id;
  final String callId;
  final String callCode;
  final String fromUsername;
  final String fromFullName;

  factory CallInvitation.fromJson(Map<String, dynamic> json) => CallInvitation(
        id: json['id'] as String,
        callId: json['call_id'] as String,
        callCode: json['call_code'] as String,
        fromUsername: json['from_username'] as String,
        fromFullName: json['from_full_name'] as String,
      );
}

class IceServerConfig {
  const IceServerConfig({required this.urls, this.username, this.credential});

  final String urls;
  final String? username;
  final String? credential;

  factory IceServerConfig.fromJson(Map<String, dynamic> json) => IceServerConfig(
        urls: json['urls'] as String,
        username: json['username'] as String?,
        credential: json['credential'] as String?,
      );

  Map<String, dynamic> toWebRTCConfig() => {
        'urls': urls,
        if (username != null) 'username': username,
        if (credential != null) 'credential': credential,
      };
}
