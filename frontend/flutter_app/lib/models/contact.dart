import 'user_role.dart';

class Contact {
  const Contact({
    required this.id,
    required this.username,
    required this.fullName,
    required this.role,
    required this.contactSince,
  });

  final String id;
  final String username;
  final String fullName;
  final UserRole role;
  final DateTime contactSince;

  factory Contact.fromJson(Map<String, dynamic> json) => Contact(
        id: json['id'] as String,
        username: json['username'] as String,
        fullName: json['full_name'] as String,
        role: UserRole.fromJson(json['role'] as String),
        contactSince: DateTime.parse(json['contact_since'] as String),
      );
}

class UserSearchResult {
  const UserSearchResult({
    required this.id,
    required this.username,
    required this.fullName,
    required this.role,
  });

  final String id;
  final String username;
  final String fullName;
  final UserRole role;

  factory UserSearchResult.fromJson(Map<String, dynamic> json) => UserSearchResult(
        id: json['id'] as String,
        username: json['username'] as String,
        fullName: json['full_name'] as String,
        role: UserRole.fromJson(json['role'] as String),
      );
}

enum ContactRequestStatus {
  pending,
  accepted,
  rejected;

  static ContactRequestStatus fromJson(String value) =>
      ContactRequestStatus.values.firstWhere((v) => v.name == value, orElse: () => ContactRequestStatus.pending);
}

class ContactRequest {
  const ContactRequest({
    required this.id,
    required this.fromUserId,
    required this.toUserId,
    required this.status,
    required this.createdAt,
    required this.otherUsername,
    required this.otherFullName,
  });

  final String id;
  final String fromUserId;
  final String toUserId;
  final ContactRequestStatus status;
  final DateTime createdAt;
  final String otherUsername;
  final String otherFullName;

  factory ContactRequest.fromJson(Map<String, dynamic> json) => ContactRequest(
        id: json['id'] as String,
        fromUserId: json['from_user_id'] as String,
        toUserId: json['to_user_id'] as String,
        status: ContactRequestStatus.fromJson(json['status'] as String),
        createdAt: DateTime.parse(json['created_at'] as String),
        otherUsername: json['other_username'] as String,
        otherFullName: json['other_full_name'] as String,
      );
}
