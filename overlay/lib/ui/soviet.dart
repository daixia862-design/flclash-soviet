import 'dart:math' as math;

import 'package:material_ui/material_ui.dart';

import 'typography.dart';

/// The flag, the star and the paper of Soviet graphic design, kept apart from
/// the M3 roles so a page can reach for them directly.
abstract final class SovietPalette {
  static const Color red = Color(0xFFC1121F);
  static const Color redDeep = Color(0xFF7F0D13);
  static const Color redBright = Color(0xFFE63946);
  static const Color blood = Color(0xFF6E0A11);
  static const Color gold = Color(0xFFE8B21C);
  static const Color goldPale = Color(0xFFF7D67A);
  static const Color ink = Color(0xFF14100F);
  static const Color paper = Color(0xFFEDE3D0);
  static const Color bone = Color(0xFFF5EFE3);
  static const Color steel = Color(0xFF8A8F99);
}

/// The seed the theme boots with, and the one the picker marks as default.
const int sovietSeedArgb = 0xFFC1121F;

const Color sovietSeedColor = Color(sovietSeedArgb);

/// Where the crimson band sits in HCT hue, wide enough to catch the picker's
/// reds and reds the system reports for a dark accent.
const double sovietHueMin = 4;

const double sovietHueMax = 46;

const double sovietChromaMin = 24;

const String sovietUnion = '\u0421\u0421\u0421\u0420';

const String sovietMotto =
    '\u0421\u041B\u0410\u0412\u0410 \u0422\u0420\u0423\u0414\u0423 \u00B7 \u041F\u0420\u041E\u041B\u0415\u0422\u0410\u0420\u0418\u0418 \u0412\u0421\u0415\u0425 \u0421\u0422\u0420\u0410\u041D, \u0421\u041E\u0415\u0414\u0418\u041D\u042F\u0419\u0422\u0415\u0421\u042C!';

const String sovietGlory = '\u0421\u041B\u0410\u0412\u0410 \u0422\u0420\u0423\u0414\u0423';

/// The steel that marks a scheme as carrying the flag palette; it rides
/// on `tertiary` so a page can tell a Soviet scheme from any other red one.
const Color sovietSteel = Color(0xFF4C5561);

bool isSovietScheme(ColorScheme scheme) =>
    scheme.tertiary.toARGB32() == sovietSteel.toARGB32();

Path starPath(
  Size size, {
  double innerRatio = 0.4,
  double rotation = -math.pi / 2,
}) {
  final center = Offset(size.width / 2, size.height / 2);
  final radius = math.min(size.width, size.height) / 2;
  final path = Path();
  for (var i = 0; i < 10; i++) {
    final r = i.isEven ? radius : radius * innerRatio;
    final angle = rotation + i * math.pi / 5;
    final point = Offset(
      center.dx + r * math.cos(angle),
      center.dy + r * math.sin(angle),
    );
    if (i == 0) {
      path.moveTo(point.dx, point.dy);
    } else {
      path.lineTo(point.dx, point.dy);
    }
  }
  return path..close();
}

class SovietStarPainter extends CustomPainter {
  const SovietStarPainter({
    required this.color,
    this.innerRatio = 0.4,
    this.rimColor,
    this.rimWidth = 0,
  });

  final Color color;
  final double innerRatio;
  final Color? rimColor;
  final double rimWidth;

  @override
  void paint(Canvas canvas, Size size) {
    final path = starPath(size, innerRatio: innerRatio);
    canvas.drawPath(
      path,
      Paint()
        ..color = color
        ..isAntiAlias = true
        ..style = PaintingStyle.fill,
    );
    final rim = rimColor;
    if (rim != null && rimWidth > 0) {
      canvas.drawPath(
        path,
        Paint()
          ..color = rim
          ..isAntiAlias = true
          ..style = PaintingStyle.stroke
          ..strokeWidth = rimWidth
          ..strokeJoin = StrokeJoin.miter,
      );
    }
  }

  @override
  bool shouldRepaint(SovietStarPainter oldDelegate) =>
      oldDelegate.color != color ||
      oldDelegate.innerRatio != innerRatio ||
      oldDelegate.rimColor != rimColor ||
      oldDelegate.rimWidth != rimWidth;
}

class SovietStar extends StatelessWidget {
  const SovietStar({
    super.key,
    this.size = 16,
    this.color = SovietPalette.gold,
    this.innerRatio = 0.4,
    this.rimColor,
    this.rimWidth = 0,
  });

  final double size;
  final Color color;
  final double innerRatio;
  final Color? rimColor;
  final double rimWidth;

  @override
  Widget build(BuildContext context) {
    return SizedBox.square(
      dimension: size,
      child: CustomPaint(
        painter: SovietStarPainter(
          color: color,
          innerRatio: innerRatio,
          rimColor: rimColor,
          rimWidth: rimWidth,
        ),
      ),
    );
  }
}

/// The hammer and sickle plate the icon set is drawn from.
class SovietEmblem extends StatelessWidget {
  const SovietEmblem({super.key, this.size = 40, this.opacity = 1});

  final double size;
  final double opacity;

  @override
  Widget build(BuildContext context) {
    return Opacity(
      opacity: opacity,
      child: Image.asset(
        'assets/images/soviet/emblem.png',
        width: size,
        height: size,
        filterQuality: FilterQuality.medium,
      ),
    );
  }
}

/// A banner whose ends are cut on the slant, the way a printed slogan is.
class SovietRibbon extends StatelessWidget {
  const SovietRibbon({
    super.key,
    required this.text,
    this.height = 34,
    this.color = SovietPalette.red,
    this.foregroundColor = SovietPalette.goldPale,
    this.glyph,
  });

  final String text;
  final double height;
  final Color color;
  final Color foregroundColor;
  final Widget? glyph;

  @override
  Widget build(BuildContext context) {
    final style = AppTextStyle.caption1
        .of(context, emphasized: true)
        .copyWith(
          color: foregroundColor,
          letterSpacing: 1.4,
          height: 1,
        );
    return SizedBox(
      height: height,
      child: CustomPaint(
        painter: _RibbonPainter(color: color),
        child: Padding(
          padding: EdgeInsets.symmetric(horizontal: height * 0.52),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            mainAxisSize: MainAxisSize.min,
            children: [
              if (glyph != null) ...[glyph!, const SizedBox(width: 8)],
              Flexible(
                child: Text(
                  text,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: style,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _RibbonPainter extends CustomPainter {
  const _RibbonPainter({required this.color});

  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final slant = size.height * 0.42;
    final path = Path()
      ..moveTo(slant, 0)
      ..lineTo(size.width - slant, 0)
      ..lineTo(size.width, size.height)
      ..lineTo(0, size.height)
      ..close();
    canvas.drawPath(path, Paint()..color = color);
    final edge = Paint()
      ..color = SovietPalette.gold
      ..strokeWidth = 1.6
      ..style = PaintingStyle.stroke;
    canvas.drawLine(
      Offset(slant, 0.8),
      Offset(size.width - slant, 0.8),
      edge,
    );
    canvas.drawLine(
      Offset(0, size.height - 0.8),
      Offset(size.width, size.height - 0.8),
      edge,
    );
  }

  @override
  bool shouldRepaint(_RibbonPainter oldDelegate) => oldDelegate.color != color;
}

/// A two-tone rule that reads as a flag flown across the page.
class SovietFlagStrip extends StatelessWidget {
  const SovietFlagStrip({super.key, this.height = 3, this.width});

  final double height;
  final double? width;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: height,
      width: width,
      child: const Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Expanded(flex: 3, child: ColoredBox(color: SovietPalette.red)),
          Expanded(flex: 2, child: ColoredBox(color: SovietPalette.gold)),
          Expanded(flex: 3, child: ColoredBox(color: SovietPalette.ink)),
        ],
      ),
    );
  }
}

/// Gold brackets around whatever sits inside, as on a bronze plaque.
class SovietFrame extends StatelessWidget {
  const SovietFrame({
    super.key,
    required this.child,
    this.color = SovietPalette.gold,
    this.length = 14,
    this.strokeWidth = 1.6,
    this.padding = const EdgeInsets.all(14),
  });

  final Widget child;
  final Color color;
  final double length;
  final double strokeWidth;
  final EdgeInsets padding;

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: _FramePainter(
        color: color,
        length: length,
        strokeWidth: strokeWidth,
      ),
      child: Padding(padding: padding, child: child),
    );
  }
}

class _FramePainter extends CustomPainter {
  const _FramePainter({
    required this.color,
    required this.length,
    required this.strokeWidth,
  });

  final Color color;
  final double length;
  final double strokeWidth;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.square
      ..style = PaintingStyle.stroke;
    final w = size.width;
    final h = size.height;
    final l = math.min(length, math.min(w, h) / 2.5);
    final corners = <Offset>[
      Offset.zero,
      Offset(w, 0),
      Offset(0, h),
      Offset(w, h),
    ];
    for (final corner in corners) {
      final dx = corner.dx == 0 ? l : -l;
      final dy = corner.dy == 0 ? l : -l;
      canvas.drawLine(corner, Offset(corner.dx + dx, corner.dy), paint);
      canvas.drawLine(corner, Offset(corner.dx, corner.dy + dy), paint);
    }
  }

  @override
  bool shouldRepaint(_FramePainter oldDelegate) =>
      oldDelegate.color != color ||
      oldDelegate.length != length ||
      oldDelegate.strokeWidth != strokeWidth;
}

extension SovietColorScheme on ColorScheme {
  Color get sovietGold => SovietPalette.gold;
}
