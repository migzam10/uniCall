class UserProfile {
  const UserProfile({this.avatarUrl, this.bio, this.phoneNumber, this.location});

  final String? avatarUrl;
  final String? bio;
  final String? phoneNumber;
  final String? location;

  factory UserProfile.fromJson(Map<String, dynamic> json) => UserProfile(
        avatarUrl: json['avatar_url'] as String?,
        bio: json['bio'] as String?,
        phoneNumber: json['phone_number'] as String?,
        location: json['location'] as String?,
      );

  Map<String, dynamic> toUpdateJson() => {
        if (avatarUrl != null) 'avatar_url': avatarUrl,
        if (bio != null) 'bio': bio,
        if (phoneNumber != null) 'phone_number': phoneNumber,
        if (location != null) 'location': location,
      };

  UserProfile copyWith({String? avatarUrl, String? bio, String? phoneNumber, String? location}) => UserProfile(
        avatarUrl: avatarUrl ?? this.avatarUrl,
        bio: bio ?? this.bio,
        phoneNumber: phoneNumber ?? this.phoneNumber,
        location: location ?? this.location,
      );
}
