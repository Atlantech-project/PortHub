import 'package:atlantech/brand/brand.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

Widget app(ThemeData theme, Widget child) => MaterialApp(theme: theme, home: Scaffold(body: child));

void main() {
  testWidgets('every logo asset resolves', (tester) async {
    for (final shape in AtlantechLogoShape.values) {
      for (final tone in AtlantechLogoTone.values) {
        final data = await rootBundle.load(AtlantechLogo.assetPath(shape, tone));
        expect(data.lengthInBytes, greaterThan(0));
      }
    }
  });

  testWidgets('primary logo stays primary: plain on light, on a paper card on dark', (tester) async {
    await tester.pumpWidget(app(AtlantechTheme.light, const AtlantechLogo(height: 80)));
    expect(find.byType(DecoratedBox), findsNothing);
    expect((tester.widget<Image>(find.byType(Image)).image as AssetImage).assetName, 'assets/brand/lockup_color.png');

    await tester.pumpWidget(app(AtlantechTheme.dark, const AtlantechLogo(height: 80)));
    await tester.pumpAndSettle(); // MaterialApp animates the theme change
    expect((tester.widget<Image>(find.byType(Image)).image as AssetImage).assetName, 'assets/brand/lockup_color.png');
    final box = tester.widget<DecoratedBox>(find.descendant(of: find.byType(AtlantechLogo), matching: find.byType(DecoratedBox)));
    expect((box.decoration as BoxDecoration).color, AtlantechColors.paper);
  });

  testWidgets('auto still offers the reversed variation on dark', (tester) async {
    await tester.pumpWidget(app(AtlantechTheme.dark, const AtlantechLogo(tone: AtlantechLogoTone.auto, height: 80)));
    expect((tester.widget<Image>(find.byType(Image)).image as AssetImage).assetName, 'assets/brand/lockup_reversed.png');
  });

  testWidgets('designer token names are on the theme and drive cards', (tester) async {
    late AtlantechTokens light, dark;
    await tester.pumpWidget(app(AtlantechTheme.light, Builder(builder: (c) { light = c.atl; return const SizedBox(); })));
    await tester.pumpWidget(app(AtlantechTheme.dark, Builder(builder: (c) { dark = c.atl; return const SizedBox(); })));
    await tester.pumpAndSettle();
    expect(light.surface, const Color(0xFFFFFFFF));
    expect(dark.surface, const Color(0xFF072B3A));
    expect(AtlantechTheme.light.cardTheme.color, AtlantechTokens.light.surface);
    expect(AtlantechTheme.dark.scaffoldBackgroundColor, AtlantechTokens.dark.bg);
  });
}
