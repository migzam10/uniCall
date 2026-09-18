/// Tipos de cuenta soportados (sección 3 de la especificación).
enum UserRole {
  oyente,
  sordo,
  administrador;

  static UserRole fromJson(String value) => UserRole.values.firstWhere(
        (r) => r.name == value,
        orElse: () => UserRole.oyente,
      );

  String toJson() => name;

  String get label => switch (this) {
        UserRole.oyente => 'Persona oyente',
        UserRole.sordo => 'Persona sorda',
        UserRole.administrador => 'Administrador',
      };
}
