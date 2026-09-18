import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/admin/admin_home_screen.dart';
import '../features/admin/lsc_categories_screen.dart';
import '../features/admin/lsc_create_phrase_screen.dart';
import '../features/admin/lsc_phrases_screen.dart';
import '../features/admin/lsc_sign_detail_screen.dart';
import '../features/admin/lsc_signs_screen.dart';
import '../features/auth/auth_controller.dart';
import '../features/auth/forgot_password_screen.dart';
import '../features/auth/login_screen.dart';
import '../features/auth/register_screen.dart';
import '../features/auth/splash_screen.dart';
import '../features/calls/create_call_screen.dart';
import '../features/calls/call_screen.dart';
import '../features/calls/direct_call_screen.dart';
import '../features/calls/home_screen.dart';
import '../features/calls/join_call_screen.dart';
import '../features/contacts/contacts_screen.dart';
import '../features/profile/profile_screen.dart';
import '../features/settings/settings_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authControllerProvider);

  return GoRouter(
    initialLocation: '/',
    redirect: (context, state) {
      final loggingRoutes = {'/login', '/register', '/forgot-password'};
      final atLoginArea = loggingRoutes.contains(state.matchedLocation);

      if (authState is AuthInitial || authState is AuthLoading) {
        return state.matchedLocation == '/' ? null : null;
      }
      if (authState is AuthAuthenticated) {
        if (state.matchedLocation == '/' || atLoginArea) return '/home';
        return null;
      }
      if (authState is AuthUnauthenticated || authState is AuthError) {
        if (!atLoginArea) return '/login';
        return null;
      }
      return null;
    },
    routes: [
      GoRoute(path: '/', builder: (context, state) => const SplashScreen()),
      GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
      GoRoute(path: '/register', builder: (context, state) => const RegisterScreen()),
      GoRoute(path: '/forgot-password', builder: (context, state) => const ForgotPasswordScreen()),
      GoRoute(path: '/home', builder: (context, state) => const HomeScreen()),
      GoRoute(path: '/profile', builder: (context, state) => const ProfileScreen()),
      GoRoute(path: '/settings', builder: (context, state) => const SettingsScreen()),
      GoRoute(path: '/contacts', builder: (context, state) => const ContactsScreen()),
      GoRoute(path: '/calls/new', builder: (context, state) => const CreateCallScreen()),
      GoRoute(path: '/calls/join', builder: (context, state) => const JoinCallScreen()),
      GoRoute(
        path: '/calls/direct/:contactId/:contactName',
        builder: (context, state) => DirectCallScreen(
          contactUserId: state.pathParameters['contactId']!,
          contactName: Uri.decodeComponent(state.pathParameters['contactName']!),
        ),
      ),
      GoRoute(
        path: '/calls/room/:callId/:callCode',
        builder: (context, state) => CallScreen(
          callId: state.pathParameters['callId']!,
          callCode: state.pathParameters['callCode']!,
        ),
      ),
      GoRoute(path: '/admin', builder: (context, state) => const AdminHomeScreen()),
      GoRoute(path: '/admin/lsc/categories', builder: (context, state) => const LscCategoriesScreen()),
      GoRoute(path: '/admin/lsc/signs', builder: (context, state) => const LscSignsScreen()),
      GoRoute(
        path: '/admin/lsc/signs/:signId',
        builder: (context, state) => LscSignDetailScreen(signId: state.pathParameters['signId']!),
      ),
      GoRoute(path: '/admin/lsc/phrases', builder: (context, state) => const LscPhrasesScreen()),
      GoRoute(path: '/admin/lsc/phrases/new', builder: (context, state) => const LscCreatePhraseScreen()),
    ],
  );
});
