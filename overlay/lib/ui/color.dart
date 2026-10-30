import 'dart:math';

import 'package:flutter/foundation.dart' show clampDouble;
import 'package:material_color_utilities/material_color_utilities.dart'
    show
        DynamicColor,
        DynamicScheme,
        Hct,
        MaterialDynamicColors,
        SchemeContent,
        SchemeMonochrome,
        SchemeTonalSpot,
        TonalPalette,
        Variant;
import 'package:material_ui/material_ui.dart';

import 'soviet.dart';

enum ColorStyle {
  vivid,
  tinted,
  soft,
  monochrome;

  Variant get _variant => switch (this) {
    vivid || tinted => Variant.content,
    soft => Variant.tonalSpot,
    monochrome => Variant.monochrome,
  };
}

/// `.agents/surfaces.md` explains why each role this replaces leaves
/// Material's value.
ColorScheme seededColorScheme({
  required Color seedColor,
  required Brightness brightness,
  ColorStyle style = ColorStyle.vivid,
}) {
  final dark = brightness == Brightness.dark;
  final source = Hct.fromInt(seedColor.toARGB32());
  final scheme = _dynamicScheme(source, dark, style);
  final primary = scheme.primaryPalette;
  final container = TonalPalette.of(
    primary.hue,
    min(primary.chroma, _primaryContainerChroma),
  );
  final tint = style == ColorStyle.tinted
      ? min(source.chroma / _tintDivisor, _maxTintChroma)
      : null;
  Color neutral(DynamicColor role, double maxChroma, [double? darkTone]) {
    final palette = role.palette(scheme);
    return Color(
      Hct.from(
        palette.hue,
        tint ?? min(palette.chroma, maxChroma),
        (dark ? darkTone : null) ?? role.getTone(scheme),
      ).toInt(),
    );
  }

  Color role(DynamicColor color) => Color(color.getArgb(scheme));

  final paperChroma = dark ? _surfaceChroma : _paperChroma;
  final accent = switch (style) {
    ColorStyle.vivid || ColorStyle.tinted => _accent(seedColor, source, dark),
    ColorStyle.soft || ColorStyle.monochrome => null,
  };
  final primaryColor = accent?.primary ?? role(MaterialDynamicColors.primary);
  final base = ColorScheme(
    brightness: brightness,
    primary: primaryColor,
    onPrimary: accent?.onPrimary ?? role(MaterialDynamicColors.onPrimary),
    surfaceTint: primaryColor,
    primaryContainer: Color(container.get(dark ? 30 : 90)),
    onPrimaryContainer: Color(container.get(dark ? 90 : 30)),
    primaryFixed: role(MaterialDynamicColors.primaryFixed),
    primaryFixedDim: role(MaterialDynamicColors.primaryFixedDim),
    onPrimaryFixed: role(MaterialDynamicColors.onPrimaryFixed),
    onPrimaryFixedVariant: role(MaterialDynamicColors.onPrimaryFixedVariant),
    secondary: role(MaterialDynamicColors.secondary),
    onSecondary: role(MaterialDynamicColors.onSecondary),
    secondaryContainer: role(MaterialDynamicColors.secondaryContainer),
    onSecondaryContainer: role(MaterialDynamicColors.onSecondaryContainer),
    secondaryFixed: role(MaterialDynamicColors.secondaryFixed),
    secondaryFixedDim: role(MaterialDynamicColors.secondaryFixedDim),
    onSecondaryFixed: role(MaterialDynamicColors.onSecondaryFixed),
    onSecondaryFixedVariant: role(
      MaterialDynamicColors.onSecondaryFixedVariant,
    ),
    tertiary: role(MaterialDynamicColors.tertiary),
    onTertiary: role(MaterialDynamicColors.onTertiary),
    tertiaryContainer: role(MaterialDynamicColors.tertiaryContainer),
    onTertiaryContainer: role(MaterialDynamicColors.onTertiaryContainer),
    tertiaryFixed: role(MaterialDynamicColors.tertiaryFixed),
    tertiaryFixedDim: role(MaterialDynamicColors.tertiaryFixedDim),
    onTertiaryFixed: role(MaterialDynamicColors.onTertiaryFixed),
    onTertiaryFixedVariant: role(MaterialDynamicColors.onTertiaryFixedVariant),
    error: role(MaterialDynamicColors.error),
    onError: role(MaterialDynamicColors.onError),
    errorContainer: role(MaterialDynamicColors.errorContainer),
    onErrorContainer: role(MaterialDynamicColors.onErrorContainer),
    outline: role(MaterialDynamicColors.outline),
    onSurface: dark
        ? Color(
            MaterialDynamicColors.onSurface
                .palette(scheme)
                .get(_darkOnSurfaceTone),
          )
        : role(MaterialDynamicColors.onSurface),
    onSurfaceVariant: role(MaterialDynamicColors.onSurfaceVariant),
    inverseSurface: role(MaterialDynamicColors.inverseSurface),
    onInverseSurface: role(MaterialDynamicColors.inverseOnSurface),
    inversePrimary: role(MaterialDynamicColors.inversePrimary),
    shadow: role(MaterialDynamicColors.shadow),
    scrim: role(MaterialDynamicColors.scrim),
    surface: neutral(MaterialDynamicColors.surface, paperChroma),
    surfaceBright: neutral(MaterialDynamicColors.surfaceBright, paperChroma),
    surfaceDim: neutral(MaterialDynamicColors.surfaceDim, _surfaceChroma),
    surfaceContainerLowest: neutral(
      MaterialDynamicColors.surfaceContainerLowest,
      _surfaceChroma,
    ),
    surfaceContainerLow: neutral(
      MaterialDynamicColors.surfaceContainerLow,
      _surfaceChroma,
    ),
    surfaceContainer: neutral(
      MaterialDynamicColors.surfaceContainer,
      _surfaceChroma,
      _darkCardTone,
    ),
    surfaceContainerHigh: neutral(
      MaterialDynamicColors.surfaceContainerHigh,
      _surfaceChroma,
      _darkBlockTone,
    ),
    surfaceContainerHighest: neutral(
      MaterialDynamicColors.surfaceContainerHighest,
      _surfaceChroma,
      _darkInsetTone,
    ),
    outlineVariant: neutral(MaterialDynamicColors.outlineVariant, 4),
  );
  return _sovietTint(base, source: source, dark: dark);
}

/// A seed only counts as a red flag once it carries enough colour to read as
/// cloth, and its hue has to land where CAM16 puts red rather than orange.
bool _isSovietSeed(Hct seed) =>
    seed.hue >= sovietHueMin &&
    seed.hue <= sovietHueMax &&
    seed.chroma >= sovietChromaMin;

/// Red seeds are printed rather than generated: crimson plates, gold and steel
/// ornament, and printed paper for the ground. Every other seed keeps the
/// scheme DynamicColor derived, so a green or blue theme is left alone.
ColorScheme _sovietTint(
  ColorScheme base, {
  required Hct source,
  required bool dark,
}) {
  if (!_isSovietSeed(source)) {
    return base;
  }
  if (dark) {
    return base.copyWith(
      primary: const Color(0xFFD01A28),
      onPrimary: const Color(0xFFFFF3E0),
      primaryContainer: const Color(0xFF7E0A12),
      onPrimaryContainer: const Color(0xFFF7D67A),
      primaryFixed: const Color(0xFFF0434E),
      primaryFixedDim: const Color(0xFFC1121F),
      onPrimaryFixed: const Color(0xFF2A0609),
      onPrimaryFixedVariant: const Color(0xFFF7D67A),
      secondary: const Color(0xFFE8B21C),
      onSecondary: const Color(0xFF241A00),
      secondaryContainer: const Color(0xFF4A3700),
      onSecondaryContainer: const Color(0xFFF7D67A),
      secondaryFixed: const Color(0xFFE8B21C),
      secondaryFixedDim: const Color(0xFFB98A00),
      onSecondaryFixed: const Color(0xFF241A00),
      onSecondaryFixedVariant: const Color(0xFF3A2A00),
      tertiary: const Color(0xFF4C5561),
      onTertiary: const Color(0xFFFFF3E0),
      tertiaryContainer: const Color(0xFF333B45),
      onTertiaryContainer: const Color(0xFFDCE3EC),
      error: const Color(0xFFFFA000),
      onError: const Color(0xFF291A00),
      errorContainer: const Color(0xFF6B3F00),
      onErrorContainer: const Color(0xFFFFE0A6),
      outline: const Color(0xFF8E7A6A),
      outlineVariant: const Color(0xFF3E2C24),
      onSurface: const Color(0xFFF2E7D8),
      onSurfaceVariant: const Color(0xFFC4B6A4),
      inverseSurface: const Color(0xFFF2E7D8),
      onInverseSurface: const Color(0xFF14100F),
      inversePrimary: const Color(0xFFB00D1C),
      surface: const Color(0xFF170A0B),
      surfaceBright: const Color(0xFF48201F),
      surfaceDim: const Color(0xFF0F0405),
      surfaceContainerLowest: const Color(0xFF110607),
      surfaceContainerLow: const Color(0xFF1E0C0D),
      surfaceContainer: const Color(0xFF261110),
      surfaceContainerHigh: const Color(0xFF301716),
      surfaceContainerHighest: const Color(0xFF3C1E1C),
    );
  }
  return base.copyWith(
    primary: const Color(0xFF8E1116),
    onPrimary: const Color(0xFFFFF3E0),
    primaryContainer: const Color(0xFFA31419),
    onPrimaryContainer: const Color(0xFFFFF3E0),
    primaryFixed: const Color(0xFFC1121F),
    primaryFixedDim: const Color(0xFF8E1116),
    onPrimaryFixed: const Color(0xFFFFF3E0),
    onPrimaryFixedVariant: const Color(0xFF6B0A0F),
    secondary: const Color(0xFFB98A00),
    onSecondary: const Color(0xFFFFF3E0),
    secondaryContainer: const Color(0xFFF3E2B8),
    onSecondaryContainer: const Color(0xFF3A2A00),
    secondaryFixed: const Color(0xFFE8B21C),
    secondaryFixedDim: const Color(0xFFB98A00),
    onSecondaryFixed: const Color(0xFF3A2A00),
    onSecondaryFixedVariant: const Color(0xFF5A4400),
    tertiary: const Color(0xFF4C5561),
    onTertiary: const Color(0xFFFFF3E0),
    tertiaryContainer: const Color(0xFFD7DEE7),
    onTertiaryContainer: const Color(0xFF1A2128),
    error: const Color(0xFFA5291B),
    onError: const Color(0xFFFFF3E0),
    errorContainer: const Color(0xFFF7D2C8),
    onErrorContainer: const Color(0xFF3A0D07),
    outline: const Color(0xFFB0705F),
    outlineVariant: const Color(0xFFDCC0AE),
    onSurface: const Color(0xFF3B1712),
    onSurfaceVariant: const Color(0xFF6E4A3E),
    inverseSurface: const Color(0xFF3B1712),
    onInverseSurface: const Color(0xFFF4EADA),
    inversePrimary: const Color(0xFFF0434E),
    surface: const Color(0xFFF4EADA),
    surfaceBright: const Color(0xFFFFFCF3),
    surfaceDim: const Color(0xFFE3D3B8),
    surfaceContainerLowest: const Color(0xFFFFF9EC),
    surfaceContainerLow: const Color(0xFFFBF3E4),
    surfaceContainer: const Color(0xFFF7EDDC),
    surfaceContainerHigh: const Color(0xFFEFE2CD),
    surfaceContainerHighest: const Color(0xFFE7D7BE),
  );
}

const _surfaceChroma = 3.0;

const _paperChroma = 1.5;

const _tintDivisor = 6.0;

const _maxTintChroma = 10.0;

const _primaryContainerChroma = 48.0;

const _darkOnSurfaceTone = 97;

const _darkCardTone = 15.0;

const _darkBlockTone = 21.0;

const _darkInsetTone = 27.0;

const _minAccentTone = 35.0;

const _maxAccentTone = 60.0;

const _darkAccentLift = 3.0;

const _minDarkAccentTone = 50.0;

const _maxDarkAccentTone = 75.0;

({Color primary, Color onPrimary}) _accent(
  Color seedColor,
  Hct seed,
  bool dark,
) {
  final tone = dark
      ? clampDouble(
          seed.tone + _darkAccentLift,
          _minDarkAccentTone,
          _maxDarkAccentTone,
        )
      : clampDouble(seed.tone, _minAccentTone, _maxAccentTone);
  return (
    primary: tone == seed.tone
        ? seedColor
        : Color(Hct.from(seed.hue, seed.chroma, tone).toInt()),
    onPrimary: tone <= _maxAccentTone
        ? Colors.white
        : Color(TonalPalette.of(seed.hue, seed.chroma).get(10)),
  );
}

DynamicScheme? _lastScheme;

// Palettes do not depend on brightness, and a seed's light and dark schemes
// are built one after the other, so the second takes the first one's rather
// than running the content variant's temperature analysis again.
DynamicScheme _dynamicScheme(Hct source, bool dark, ColorStyle style) {
  final last = _lastScheme;
  final scheme =
      last != null &&
          last.sourceColorArgb == source.toInt() &&
          last.variant == style._variant
      ? DynamicScheme(
          sourceColorHct: source,
          variant: last.variant,
          isDark: dark,
          primaryPalette: last.primaryPalette,
          secondaryPalette: last.secondaryPalette,
          tertiaryPalette: last.tertiaryPalette,
          neutralPalette: last.neutralPalette,
          neutralVariantPalette: last.neutralVariantPalette,
        )
      : switch (style) {
          ColorStyle.vivid || ColorStyle.tinted => SchemeContent(
            sourceColorHct: source,
            isDark: dark,
            contrastLevel: 0,
          ),
          ColorStyle.soft => SchemeTonalSpot(
            sourceColorHct: source,
            isDark: dark,
            contrastLevel: 0,
          ),
          ColorStyle.monochrome => SchemeMonochrome(
            sourceColorHct: source,
            isDark: dark,
            contrastLevel: 0,
          ),
        };
  return _lastScheme = scheme;
}

final _successPalette = TonalPalette.fromHct(
  Hct.from(48, 64, 46),
);

final _warningPalette = TonalPalette.fromHct(
  Hct.from(26, 82, 50),
);

extension ColorExtension on Color {
  Color get opacity80 {
    return withValues(alpha: 0.8);
  }

  Color get opacity60 {
    return withValues(alpha: 0.6);
  }

  Color get opacity50 {
    return withValues(alpha: 0.5);
  }

  Color get opacity38 {
    return withValues(alpha: 0.38);
  }

  Color get opacity30 {
    return withValues(alpha: 0.3);
  }

  Color get opacity12 {
    return withValues(alpha: 0.12);
  }

  Color get opacity15 {
    return withValues(alpha: 0.15);
  }

  Color get opacity10 {
    return withValues(alpha: 0.1);
  }

  Color get opacity0 {
    return withValues(alpha: 0);
  }

  double get tone => Hct.fromInt(toARGB32()).tone;

  Color shiftTone(double delta) {
    final hct = Hct.fromInt(toARGB32());
    return Color(
      Hct.from(
        hct.hue,
        hct.chroma,
        clampDouble(hct.tone + delta, 0, 100),
      ).toInt(),
    );
  }

  String get hex {
    final value = toARGB32();
    final red = (value >> 16) & 0xFF;
    final green = (value >> 8) & 0xFF;
    final blue = value & 0xFF;
    return '#${red.toRadixString(16).padLeft(2, '0')}'
            '${green.toRadixString(16).padLeft(2, '0')}'
            '${blue.toRadixString(16).padLeft(2, '0')}'
        .toUpperCase();
  }
}

extension ColorSchemeExtension on ColorScheme {
  ColorScheme toPureBlack(bool isPureBlack) {
    if (!isPureBlack || brightness != Brightness.dark) {
      return this;
    }
    final shift = surface.tone;
    Color lower(Color color) => color.shiftTone(-shift);

    return copyWith(
      surface: Colors.black,
      surfaceDim: Colors.black,
      surfaceContainerLowest: Colors.black,
      surfaceContainerLow: lower(surfaceContainerLow),
      surfaceContainer: lower(surfaceContainer),
      surfaceContainerHigh: lower(surfaceContainerHigh),
      surfaceContainerHighest: lower(surfaceContainerHighest),
      surfaceBright: lower(surfaceBright),
    );
  }

  Color get modalScrim => scrim.withValues(alpha: 0.32);

  /// How far iOS 27 dims behind an alert.
  Color get alertScrim =>
      scrim.withValues(alpha: brightness == Brightness.dark ? 0.48 : 0.2);

  /// iOS 27's systemRed, which an alert's destructive action takes.
  Color get destructive =>
      Color(brightness == Brightness.dark ? 0xFFFF4245 : 0xFFFF383C);

  Color _toneOf(TonalPalette palette, int light, int dark) =>
      Color(palette.get(brightness == Brightness.dark ? dark : light));

  Color get success => _toneOf(_successPalette, 40, 80);

  Color get successContainer => _toneOf(_successPalette, 90, 30);

  Color get onSuccessContainer => _toneOf(_successPalette, 30, 90);

  Color get warning => _toneOf(_warningPalette, 40, 80);

  Color get warningContainer => _toneOf(_warningPalette, 90, 30);

  Color get onWarningContainer => _toneOf(_warningPalette, 30, 90);

  Color? delayColor(int? delay) {
    if (delay == null) return null;
    if (delay < 0) return error;
    if (delay < 600) return success;
    return warning;
  }
}
