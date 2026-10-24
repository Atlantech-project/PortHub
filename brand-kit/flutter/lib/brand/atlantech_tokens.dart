import 'package:flutter/material.dart';

/// The design tokens under the same names the designer uses in Figma and the
/// web uses in CSS (`surface-2` here is `surface2`, `--atl-surface-2` on the web).
///
/// ```dart
/// Container(color: context.atl.surface2)
/// Text('Delay risk', style: TextStyle(color: context.atl.warning))
/// ```
///
/// Values must match design/tokens/atlantech.tokens.json; tools/check_tokens.py verifies it.
@immutable
class AtlantechTokens extends ThemeExtension<AtlantechTokens> {
  const AtlantechTokens({
    required this.bg,
    required this.surface,
    required this.surface2,
    required this.surface3,
    required this.text,
    required this.textMuted,
    required this.border,
    required this.borderStrong,
    required this.primary,
    required this.onPrimary,
    required this.primarySoft,
    required this.accent,
    required this.accentText,
    required this.link,
    required this.focus,
    required this.headerBg,
    required this.headerText,
    required this.success,
    required this.warning,
    required this.danger,
    required this.logoCard,
  });

  final Color bg;
  final Color surface;
  final Color surface2;
  final Color surface3;
  final Color text;
  final Color textMuted;
  final Color border;
  final Color borderStrong;
  final Color primary;
  final Color onPrimary;
  final Color primarySoft;
  final Color accent;
  final Color accentText;
  final Color link;
  final Color focus;
  final Color headerBg;
  final Color headerText;
  final Color success;
  final Color warning;
  final Color danger;
  final Color logoCard;

  static const light = AtlantechTokens(
    bg: Color(0xFFF7F5F2),
    surface: Color(0xFFFFFFFF),
    surface2: Color(0xFFF2EFEB),
    surface3: Color(0xFFE5E1DD),
    text: Color(0xFF0F2A36),
    textMuted: Color(0xFF4B5F68),
    border: Color(0xFFD3DEDF),
    borderStrong: Color(0xFF8FA3AA),
    primary: Color(0xFF083A4F),
    onPrimary: Color(0xFFE5E1DD),
    primarySoft: Color(0xFFC0D5D6),
    accent: Color(0xFFA58D66),
    accentText: Color(0xFF7A6440),
    link: Color(0xFF407E8C),
    focus: Color(0xFF407E8C),
    headerBg: Color(0xFF083A4F),
    headerText: Color(0xFFE5E1DD),
    success: Color(0xFF2E7D5B),
    warning: Color(0xFF8A5C0F),
    danger: Color(0xFFB3412F),
    logoCard: Color(0x00000000),
  );

  static const dark = AtlantechTokens(
    bg: Color(0xFF04222F),
    surface: Color(0xFF072B3A),
    surface2: Color(0xFF0B3446),
    surface3: Color(0xFF103D51),
    text: Color(0xFFE5E1DD),
    textMuted: Color(0xFFA9BEC3),
    border: Color(0xFF1E4A5B),
    borderStrong: Color(0xFF5F7F89),
    primary: Color(0xFFC0D5D6),
    onPrimary: Color(0xFF083A4F),
    primarySoft: Color(0xFF1C5466),
    accent: Color(0xFFC2A77B),
    accentText: Color(0xFFC2A77B),
    link: Color(0xFF7FB4BF),
    focus: Color(0xFF7FB4BF),
    headerBg: Color(0xFF0B3446),
    headerText: Color(0xFFE5E1DD),
    success: Color(0xFF7CC9A4),
    warning: Color(0xFFE3B766),
    danger: Color(0xFFF2A493),
    logoCard: Color(0xFFF7F5F2),
  );

  @override
  AtlantechTokens copyWith({
    Color? bg,
    Color? surface,
    Color? surface2,
    Color? surface3,
    Color? text,
    Color? textMuted,
    Color? border,
    Color? borderStrong,
    Color? primary,
    Color? onPrimary,
    Color? primarySoft,
    Color? accent,
    Color? accentText,
    Color? link,
    Color? focus,
    Color? headerBg,
    Color? headerText,
    Color? success,
    Color? warning,
    Color? danger,
    Color? logoCard,
  }) {
    return AtlantechTokens(
      bg: bg ?? this.bg,
      surface: surface ?? this.surface,
      surface2: surface2 ?? this.surface2,
      surface3: surface3 ?? this.surface3,
      text: text ?? this.text,
      textMuted: textMuted ?? this.textMuted,
      border: border ?? this.border,
      borderStrong: borderStrong ?? this.borderStrong,
      primary: primary ?? this.primary,
      onPrimary: onPrimary ?? this.onPrimary,
      primarySoft: primarySoft ?? this.primarySoft,
      accent: accent ?? this.accent,
      accentText: accentText ?? this.accentText,
      link: link ?? this.link,
      focus: focus ?? this.focus,
      headerBg: headerBg ?? this.headerBg,
      headerText: headerText ?? this.headerText,
      success: success ?? this.success,
      warning: warning ?? this.warning,
      danger: danger ?? this.danger,
      logoCard: logoCard ?? this.logoCard,
    );
  }

  @override
  AtlantechTokens lerp(ThemeExtension<AtlantechTokens>? other, double t) {
    if (other is! AtlantechTokens) return this;
    Color l(Color a, Color b) => Color.lerp(a, b, t)!;
    return AtlantechTokens(
      bg: l(bg, other.bg),
      surface: l(surface, other.surface),
      surface2: l(surface2, other.surface2),
      surface3: l(surface3, other.surface3),
      text: l(text, other.text),
      textMuted: l(textMuted, other.textMuted),
      border: l(border, other.border),
      borderStrong: l(borderStrong, other.borderStrong),
      primary: l(primary, other.primary),
      onPrimary: l(onPrimary, other.onPrimary),
      primarySoft: l(primarySoft, other.primarySoft),
      accent: l(accent, other.accent),
      accentText: l(accentText, other.accentText),
      link: l(link, other.link),
      focus: l(focus, other.focus),
      headerBg: l(headerBg, other.headerBg),
      headerText: l(headerText, other.headerText),
      success: l(success, other.success),
      warning: l(warning, other.warning),
      danger: l(danger, other.danger),
      logoCard: l(logoCard, other.logoCard),
    );
  }
}

extension AtlantechTokensContext on BuildContext {
  /// The ATLANTECH tokens for the current theme.
  AtlantechTokens get atl =>
      Theme.of(this).extension<AtlantechTokens>() ??
      (Theme.of(this).brightness == Brightness.dark ? AtlantechTokens.dark : AtlantechTokens.light);
}
