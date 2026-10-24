import 'package:flutter/material.dart';

/// The ATLANTECH palette.
///
/// The first five come straight from the identity sheet. Everything below them
/// is derived for UI work (surfaces, text, status) and is not part of the logo
/// palette, so never use those in brand artwork.
abstract final class AtlantechColors {
  // Identity palette
  static const deepNavy = Color(0xFF083A4F); // trust, stability
  static const mutedGold = Color(0xFFA58D66); // value, progress
  static const lightTeal = Color(0xFFC0D5D6); // clarity, balance
  static const midTeal = Color(0xFF407E8C); // innovation, growth
  static const offWhite = Color(0xFFE5E1DD); // simplicity, focus

  // Light surfaces and text
  static const paper = Color(0xFFF7F5F2);
  static const ink = Color(0xFF0F2A36);
  static const inkMuted = Color(0xFF4B5F68);
  static const goldText = Color(0xFF7A6440); // gold that passes AA as text on paper

  // Dark surfaces and text
  static const abyss = Color(0xFF04222F);
  static const tideSurface = Color(0xFF0B3446);
  static const goldOnDark = Color(0xFFC2A77B);
  static const tealOnDark = Color(0xFF7FB4BF);
  static const inkMutedOnDark = Color(0xFFA9BEC3);

  // Status (functional, not identity)
  static const success = Color(0xFF2E7D5B);
  static const warning = Color(0xFF8A5C0F);
  static const danger = Color(0xFFB3412F);
  static const dangerOnDark = Color(0xFFF2A493);
}
