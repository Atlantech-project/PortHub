import 'package:flutter/material.dart';

import 'atlantech_colors.dart';

enum AtlantechLogoShape { lockup, symbol, wordmark }

enum AtlantechLogoTone {
  /// The primary, full-colour logo. On dark themes it sits on a paper card.
  color,

  /// Follow the theme: full colour on light, reversed on dark.
  auto,

  /// Variation with light inks, only for logos placed directly on navy or dark surfaces.
  reversed,

  /// Single colour Deep Navy.
  monoNavy,

  /// Single colour white, for photos and strong colour fields.
  monoWhite,
}

/// The ATLANTECH logo, picked from the resolution-aware PNGs in `assets/brand/`.
///
/// ```dart
/// const AtlantechLogo(height: 120)                                  // primary logo, card on dark
/// const AtlantechLogo(shape: AtlantechLogoShape.symbol, height: 32)
/// const AtlantechLogo(shape: AtlantechLogoShape.wordmark, tone: AtlantechLogoTone.reversed, height: 28) // app bar
/// ```
class AtlantechLogo extends StatelessWidget {
  const AtlantechLogo({
    super.key,
    this.shape = AtlantechLogoShape.lockup,
    this.tone = AtlantechLogoTone.color,
    this.width,
    this.height,
    this.cardOnDark = true,
    this.semanticLabel = 'ATLANTECH',
  });

  final AtlantechLogoShape shape;
  final AtlantechLogoTone tone;
  final double? width;
  final double? height;

  /// Put the full-colour logo on a paper card when the theme is dark, so the
  /// primary logo stays readable instead of being swapped for a variation.
  final bool cardOnDark;
  final String semanticLabel;

  static String assetPath(AtlantechLogoShape shape, AtlantechLogoTone tone) {
    final file = switch (tone) {
      AtlantechLogoTone.auto || AtlantechLogoTone.color => 'color',
      AtlantechLogoTone.reversed => 'reversed',
      AtlantechLogoTone.monoNavy => 'mono_navy',
      AtlantechLogoTone.monoWhite => 'mono_white',
    };
    return 'assets/brand/${shape.name}_$file.png';
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final resolved = tone == AtlantechLogoTone.auto && dark ? AtlantechLogoTone.reversed : tone;

    final image = Image.asset(
      assetPath(shape, resolved),
      width: width,
      height: height,
      fit: BoxFit.contain,
      filterQuality: FilterQuality.medium,
      semanticLabel: semanticLabel,
    );

    if (!(dark && cardOnDark && resolved == AtlantechLogoTone.color)) return image;

    final pad = (height ?? width ?? 48) * 0.14;
    return DecoratedBox(
      decoration: BoxDecoration(
        color: AtlantechColors.paper,
        borderRadius: BorderRadius.circular(pad * 1.2),
      ),
      child: Padding(padding: EdgeInsets.all(pad), child: image),
    );
  }
}
