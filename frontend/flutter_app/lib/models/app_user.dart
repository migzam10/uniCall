import 'user_role.dart';

class AppUser {
  const AppUser({
    required this.id,
    required this.username,
    required this.email,
    required this.fullName,
    required this.role,
    required this.isActive,
    required this.isVerified,
  });

  final String id;
  final String username;
  final String email;
  final String fullName;
  final UserRole role;
  final bool isActive;
  final bool isVerified;

  factory AppUser.fromJson(Map<String, dynamic> json) => AppUser(
        id: json['id'] as String,
        username: json['username'] as String,
        email: json['email'] as String,
        fullName: json['full_name'] as String,
        role: UserRole.fromJson(json['role'] as String),
        isActive: json['is_active'] as bool,
        isVerified: json['is_verified'] as bool,
      );
}
