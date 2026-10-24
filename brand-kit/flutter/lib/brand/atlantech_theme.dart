import 'package:flutter/material.dart';

import 'atlantech_colors.dart';
import 'atlantech_tokens.dart';

/// Material 3 themes built on the ATLANTECH identity.
///
/// ```dart
/// MaterialApp(
///   theme: AtlantechTheme.light,
///   darkTheme: AtlantechTheme.dark,
/// )
/// ```
abstract final class AtlantechTheme {
  static const displayFont = 'Montserrat';
  static const bodyFont = 'Inter';

  static const _radius = 12.0;

  static final ColorScheme lightScheme = const ColorScheme(
    brightness: Brightness.light,
    primary: AtlantechColors.deepNavy,
    onPrimary: AtlantechColors.offWhite,
    primaryContainer: AtlantechColors.lightTeal,
    onPrimaryContainer: AtlantechColors.deepNavy,
    secondary: AtlantechColors.mutedGold,
    onSecondary: Color(0xFF241A0A),
    secondaryContainer: Color(0xFFEFE6D8),
    onSecondaryContainer: Color(0xFF4A3B22),
    tertiary: AtlantechColors.midTeal,
    onTertiary: Colors.white,
    tertiaryContainer: Color(0xFFD7E7EA),
    onTertiaryContainer: Color(0xFF173F49),
    error: AtlantechColors.danger,
    onError: Colors.white,
    errorContainer: Color(0xFFF7DCD6),
    onErrorContainer: Color(0xFF5C1A10),
    surface: AtlantechColors.paper,
    onSurface: AtlantechColors.ink,
    onSurfaceVariant: AtlantechColors.inkMuted,
    surfaceContainerLowest: Colors.white,
    surfaceContainerLow: Color(0xFFF2EFEB),
    surfaceContainer: Color(0xFFECE8E3),
    surfaceContainerHigh: AtlantechColors.offWhite,
    surfaceContainerHighest: Color(0xFFDDD8D2),
    outline: Color(0xFF8FA3AA),
    outlineVariant: Color(0xFFD3DEDF),
    inverseSurface: AtlantechColors.deepNavy,
    onInverseSurface: AtlantechColors.offWhite,
    inversePrimary: AtlantechColors.lightTeal,
    shadow: Colors.black,
    scrim: Colors.black,
    surfaceTint: Colors.transparent,
  );

  static final ColorScheme darkScheme = const ColorScheme(
    brightness: Brightness.dark,
    primary: AtlantechColors.lightTeal,
    onPrimary: AtlantechColors.deepNavy,
    primaryContainer: Color(0xFF1C5466),
    onPrimaryContainer: AtlantechColors.lightTeal,
    secondary: AtlantechColors.goldOnDark,
    onSecondary: Color(0xFF2B2112),
    secondaryContainer: Color(0xFF4A3B22),
    onSecondaryContainer: Color(0xFFEFE6D8),
    tertiary: AtlantechColors.tealOnDark,
    onTertiary: Color(0xFF062A36),
    tertiaryContainer: Color(0xFF235563),
    onTertiaryContainer: Color(0xFFD7E7EA),
    error: AtlantechColors.dangerOnDark,
    onError: Color(0xFF4A140B),
    errorContainer: Color(0xFF7A2A1E),
    onErrorContainer: Color(0xFFF7DCD6),
    surface: AtlantechColors.abyss,
    onSurface: AtlantechColors.offWhite,
    onSurfaceVariant: AtlantechColors.inkMutedOnDark,
    surfaceContainerLowest: Color(0xFF021A24),
    surfaceContainerLow: Color(0xFF072B3A),
    surfaceContainer: AtlantechColors.tideSurface,
    surfaceContainerHigh: Color(0xFF103D51),
    surfaceContainerHighest: Color(0xFF16475C),
    outline: Color(0xFF5F7F89),
    outlineVariant: Color(0xFF1E4A5B),
    inverseSurface: AtlantechColors.offWhite,
    onInverseSurface: AtlantechColors.deepNavy,
    inversePrimary: AtlantechColors.deepNavy,
    shadow: Colors.black,
    scrim: Colors.black,
    surfaceTint: Colors.transparent,
  );

  static ThemeData get light => _build(lightScheme);
  static ThemeData get dark => _build(darkScheme);

  static TextTheme _textTheme(Color ink) {
    TextStyle d(double size, FontWeight w, double height, [double ls = 0]) => TextStyle(
        fontFamily: displayFont, fontSize: size, fontWeight: w, height: height / size, letterSpacing: ls);
    TextStyle b(double size, FontWeight w, double height, [double ls = 0]) => TextStyle(
        fontFamily: bodyFont, fontSize: size, fontWeight: w, height: height / size, letterSpacing: ls);

    return TextTheme(
      displayLarge: d(57, FontWeight.w700, 64, -0.25),
      displayMedium: d(45, FontWeight.w700, 52),
      displaySmall: d(36, FontWeight.w600, 44),
      headlineLarge: d(32, FontWeight.w600, 40),
      headlineMedium: d(28, FontWeight.w600, 36),
      headlineSmall: d(24, FontWeight.w600, 32),
      titleLarge: d(22, FontWeight.w600, 28),
      titleMedium: b(16, FontWeight.w600, 24, 0.1),
      titleSmall: b(14, FontWeight.w600, 20, 0.1),
      bodyLarge: b(16, FontWeight.w400, 24, 0.15),
      bodyMedium: b(14, FontWeight.w400, 20, 0.25),
      bodySmall: b(12, FontWeight.w400, 16, 0.4),
      labelLarge: b(14, FontWeight.w600, 20, 0.1),
      labelMedium: b(12, FontWeight.w500, 16, 0.5),
      labelSmall: b(11, FontWeight.w500, 16, 0.5),
    ).apply(bodyColor: ink, displayColor: ink);
  }

  static ThemeData _build(ColorScheme s) {
    final light = s.brightness == Brightness.light;
    final t = light ? AtlantechTokens.light : AtlantechTokens.dark;
    final shape = RoundedRectangleBorder(borderRadius: BorderRadius.circular(_radius));

    return ThemeData(
      useMaterial3: true,
      colorScheme: s,
      fontFamily: bodyFont,
      textTheme: _textTheme(s.onSurface),
      extensions: [t],
      scaffoldBackgroundColor: t.bg,
      appBarTheme: AppBarTheme(
        backgroundColor: t.headerBg,
        foregroundColor: t.headerText,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: const TextStyle(
          fontFamily: displayFont,
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: AtlantechColors.offWhite,
        ),
      ),
      cardTheme: CardThemeData(
        color: t.surface,
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(_radius + 4),
          side: BorderSide(color: t.border),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          shape: shape,
          minimumSize: const Size(64, 48),
          padding: const EdgeInsets.symmetric(horizontal: 24),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          shape: shape,
          minimumSize: const Size(64, 48),
          side: BorderSide(color: s.outline),
        ),
      ),
      textButtonTheme: TextButtonThemeData(style: TextButton.styleFrom(shape: shape)),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: t.surface,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(_radius)),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(_radius),
          borderSide: BorderSide(color: s.outline),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(_radius),
          borderSide: BorderSide(color: light ? s.primary : s.tertiary, width: 2),
        ),
      ),
      chipTheme: ChipThemeData(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        side: BorderSide(color: s.outlineVariant),
      ),
      dividerTheme: DividerThemeData(color: s.outlineVariant, thickness: 1, space: 1),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: s.surfaceContainer,
        indicatorColor: light ? AtlantechColors.lightTeal : s.primaryContainer,
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: s.inverseSurface,
        contentTextStyle: TextStyle(fontFamily: bodyFont, color: s.onInverseSurface),
        shape: shape,
      ),
      progressIndicatorTheme: ProgressIndicatorThemeData(color: light ? s.tertiary : s.primary),
    );
  }
}
