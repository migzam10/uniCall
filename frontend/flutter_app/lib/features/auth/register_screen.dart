import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../models/user_role.dart';
import 'auth_controller.dart';

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _fullNameController = TextEditingController();
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  UserRole _selectedRole = UserRole.oyente;
  bool _obscurePassword = true;

  @override
  void dispose() {
    _fullNameController.dispose();
    _usernameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) return;
    ref.read(authControllerProvider.notifier).register(
          fullName: _fullNameController.text.trim(),
          username: _usernameController.text.trim(),
          email: _emailController.text.trim(),
          password: _passwordController.text,
          role: _selectedRole,
        );
  }

  @override
  Widget build(BuildContext context) {
    ref.listen<AuthState>(authControllerProvider, (previous, next) {
      if (next is AuthUnauthenticated && previous is AuthLoading) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Cuenta creada. Ahora inicia sesión.')),
        );
        context.pop();
      } else if (next is AuthError) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(next.message), backgroundColor: Theme.of(context).colorScheme.error),
        );
      }
    });

    final authState = ref.watch(authControllerProvider);
    final isLoading = authState is AuthLoading;

    return Scaffold(
      appBar: AppBar(title: const Text('Crear cuenta')),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 480),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text('¿Cómo te comunicas principalmente?', style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 12),
                    _RoleOption(
                      role: UserRole.oyente,
                      title: 'Persona oyente',
                      description: 'Hablas normalmente y quieres recibir traducción a LSC.',
                      icon: Icons.record_voice_over_outlined,
                      groupValue: _selectedRole,
                      onChanged: (role) => setState(() => _selectedRole = role),
                    ),
                    const SizedBox(height: 12),
                    _RoleOption(
                      role: UserRole.sordo,
                      title: 'Persona sorda',
                      description: 'Te comunicas en LSC y quieres que se traduzca a voz.',
                      icon: Icons.sign_language_outlined,
                      groupValue: _selectedRole,
                      onChanged: (role) => setState(() => _selectedRole = role),
                    ),
                    const SizedBox(height: 24),
                    TextFormField(
                      controller: _fullNameController,
                      decoration: const InputDecoration(labelText: 'Nombre completo'),
                      validator: (v) => (v == null || v.trim().length < 2) ? 'Ingresa tu nombre' : null,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _usernameController,
                      decoration: const InputDecoration(labelText: 'Nombre de usuario'),
                      validator: (v) {
                        if (v == null || v.trim().length < 3) return 'Mínimo 3 caracteres';
                        if (!RegExp(r'^[a-zA-Z0-9_.]+$').hasMatch(v.trim())) {
                          return 'Solo letras, números, punto y guion bajo';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _emailController,
                      keyboardType: TextInputType.emailAddress,
                      decoration: const InputDecoration(labelText: 'Correo electrónico'),
                      validator: (v) =>
                          (v == null || !v.contains('@')) ? 'Ingresa un correo válido' : null,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _passwordController,
                      obscureText: _obscurePassword,
                      decoration: InputDecoration(
                        labelText: 'Contraseña',
                        helperText: 'Mínimo 8 caracteres',
                        suffixIcon: IconButton(
                          icon: Icon(_obscurePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined),
                          onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                        ),
                      ),
                      validator: (v) => (v == null || v.length < 8) ? 'Mínimo 8 caracteres' : null,
                    ),
                    const SizedBox(height: 28),
                    ElevatedButton(
                      onPressed: isLoading ? null : _submit,
                      child: isLoading
                          ? const SizedBox(
                              height: 24,
                              width: 24,
                              child: CircularProgressIndicator(strokeWidth: 2.5, color: Colors.white),
                            )
                          : const Text('Crear cuenta'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _RoleOption extends StatelessWidget {
  const _RoleOption({
    required this.role,
    required this.title,
    required this.description,
    required this.icon,
    required this.groupValue,
    required this.onChanged,
  });

  final UserRole role;
  final String title;
  final String description;
  final IconData icon;
  final UserRole groupValue;
  final ValueChanged<UserRole> onChanged;

  @override
  Widget build(BuildContext context) {
    final selected = role == groupValue;
    final color = Theme.of(context).colorScheme.primary;

    return Semantics(
      button: true,
      selected: selected,
      label: '$title. $description',
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: () => onChanged(role),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            border: Border.all(color: selected ? color : const Color(0xFFC7CDD4), width: selected ? 2 : 1),
            borderRadius: BorderRadius.circular(14),
            color: selected ? color.withOpacity(0.06) : Colors.white,
          ),
          child: Row(
            children: [
              Icon(icon, color: selected ? color : const Color(0xFF3C4550), size: 32),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16)),
                    const SizedBox(height: 2),
                    Text(description, style: Theme.of(context).textTheme.bodyMedium),
                  ],
                ),
              ),
              Icon(
                selected ? Icons.check_circle : Icons.circle_outlined,
                color: selected ? color : const Color(0xFFC7CDD4),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
