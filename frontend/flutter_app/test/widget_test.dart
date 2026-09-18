import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:lsc_videollamadas/main.dart';

void main() {
  testWidgets('La app arranca y muestra la pantalla de splash', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: LscApp()));
    await tester.pump();

    expect(find.text('LSC Videollamadas'), findsOneWidget);
  });
}
