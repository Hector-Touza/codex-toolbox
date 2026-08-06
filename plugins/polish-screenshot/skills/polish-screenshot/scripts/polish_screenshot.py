#!/usr/bin/env python3
"""Create publication-ready screenshot compositions without uploading images."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFilter, ImageOps
except ImportError as exc:  # pragma: no cover - exercised only without the dependency
    raise SystemExit(
        "Pillow is required. Install it with: python -m pip install 'Pillow>=10'"
    ) from exc


VERSION = "0.1.0"

PRESETS = {
    "coral-waves": "Warm coral mesh with quiet flowing lines.",
    "aurora-night": "Dark navy field with teal, violet, and rose light.",
    "cobalt-grid": "Cobalt gradient with a restrained technical grid.",
    "paper-sunrise": "Warm paper field with soft sunrise color.",
}


def parse_size(value: str) -> tuple[int, int]:
    normalized = value.lower().replace("×", "x")
    try:
        width_text, height_text = normalized.split("x", 1)
        width, height = int(width_text), int(height_text)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("Use WIDTHxHEIGHT, for example 1536x864.") from exc
    if width < 320 or height < 240:
        raise argparse.ArgumentTypeError("Canvas dimensions must be at least 320x240.")
    return width, height


def _mix(a: int, b: int, amount: float) -> int:
    return round(a + (b - a) * amount)


def _diagonal_gradient(
    size: tuple[int, int], start: str, end: str, *, resolution: int = 4
) -> Image.Image:
    width, height = size
    low_width = max(2, width // resolution)
    low_height = max(2, height // resolution)
    first = ImageColor.getrgb(start)
    second = ImageColor.getrgb(end)
    image = Image.new("RGB", (low_width, low_height))
    pixels: list[tuple[int, int, int]] = []
    denominator = max(1, low_width + low_height - 2)
    for y in range(low_height):
        for x in range(low_width):
            amount = (x + y) / denominator
            pixels.append(tuple(_mix(first[i], second[i], amount) for i in range(3)))
    image.putdata(pixels)
    return image.resize(size, Image.Resampling.BICUBIC).convert("RGBA")


def _add_blob(
    base: Image.Image,
    center: tuple[float, float],
    radius: float,
    color: str,
    opacity: int,
) -> Image.Image:
    width, height = base.size
    cx, cy = round(center[0] * width), round(center[1] * height)
    radius_px = round(radius * min(width, height))
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    rgb = ImageColor.getrgb(color)
    draw.ellipse(
        (cx - radius_px, cy - radius_px, cx + radius_px, cy + radius_px),
        fill=(*rgb, opacity),
    )
    layer = layer.filter(ImageFilter.GaussianBlur(max(8, round(radius_px * 0.5))))
    return Image.alpha_composite(base, layer)


def _add_vignette(base: Image.Image, opacity: int = 32) -> Image.Image:
    width, height = base.size
    mask = Image.new("L", base.size, opacity)
    draw = ImageDraw.Draw(mask)
    inset_x, inset_y = round(width * 0.08), round(height * 0.08)
    draw.ellipse(
        (-inset_x, -inset_y, width + inset_x, height + inset_y), fill=0
    )
    mask = mask.filter(ImageFilter.GaussianBlur(round(min(base.size) * 0.14)))
    shade = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shade.putalpha(mask)
    return Image.alpha_composite(base, shade)


def _coral_waves(size: tuple[int, int]) -> Image.Image:
    image = _diagonal_gradient(size, "#E96872", "#F7B07A")
    image = _add_blob(image, (0.17, 0.18), 0.55, "#FF5F91", 150)
    image = _add_blob(image, (0.82, 0.2), 0.5, "#FFD38B", 170)
    image = _add_blob(image, (0.68, 0.92), 0.45, "#C95386", 95)
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = size
    for index, (alpha, line_width) in enumerate(((46, 3), (28, 2), (18, 2))):
        points = []
        for x in range(-20, width + 21, max(6, width // 180)):
            phase = (x / width) * math.tau * 1.25 + index * 0.9
            y = height * (0.62 + index * 0.09) + math.sin(phase) * height * 0.095
            points.append((x, round(y)))
        draw.line(points, fill=(255, 245, 238, alpha), width=line_width)
    return Image.alpha_composite(image, overlay)


def _aurora_night(size: tuple[int, int]) -> Image.Image:
    image = _diagonal_gradient(size, "#050914", "#111C35")
    image = _add_blob(image, (0.15, 0.7), 0.72, "#00B9A4", 130)
    image = _add_blob(image, (0.58, 0.05), 0.62, "#6657FF", 135)
    image = _add_blob(image, (0.92, 0.74), 0.58, "#EA5B9E", 110)
    return _add_vignette(image, 44)


def _cobalt_grid(size: tuple[int, int]) -> Image.Image:
    image = _diagonal_gradient(size, "#09214B", "#2457C7")
    image = _add_blob(image, (0.78, 0.12), 0.55, "#31B7F3", 125)
    image = _add_blob(image, (0.08, 0.86), 0.58, "#7047EB", 95)
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = size
    spacing = max(32, round(min(width, height) * 0.075))
    for x in range(-(height // 2), width + height // 2, spacing):
        draw.line((x, 0, x - height // 3, height), fill=(201, 232, 255, 23), width=1)
    for y in range(0, height + spacing, spacing):
        draw.line((0, y, width, y), fill=(201, 232, 255, 18), width=1)
    return _add_vignette(Image.alpha_composite(image, overlay), 28)


def _paper_sunrise(size: tuple[int, int]) -> Image.Image:
    image = _diagonal_gradient(size, "#F3EFE6", "#E9DDCF")
    image = _add_blob(image, (0.7, 0.08), 0.67, "#FF9A72", 125)
    image = _add_blob(image, (0.18, 0.84), 0.58, "#E5B8FF", 78)
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = size
    center = (round(width * 0.76), round(height * 0.14))
    for index, alpha in enumerate((32, 22, 14)):
        radius = round(min(width, height) * (0.16 + index * 0.1))
        draw.ellipse(
            (
                center[0] - radius,
                center[1] - radius,
                center[0] + radius,
                center[1] + radius,
            ),
            outline=(255, 255, 255, alpha),
            width=max(1, round(min(width, height) * 0.004)),
        )
    return Image.alpha_composite(image, overlay)


BACKGROUND_BUILDERS = {
    "coral-waves": _coral_waves,
    "aurora-night": _aurora_night,
    "cobalt-grid": _cobalt_grid,
    "paper-sunrise": _paper_sunrise,
}


def render_background(preset: str, size: tuple[int, int]) -> Image.Image:
    return BACKGROUND_BUILDERS[preset](size).convert("RGB")


def _fit_background(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(ImageOps.exif_transpose(image).convert("RGB"), size, Image.Resampling.LANCZOS)


def _rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def _shadow_mask(
    canvas_size: tuple[int, int],
    card_mask: Image.Image,
    position: tuple[int, int],
    *,
    blur: int,
    offset_y: int,
    opacity: float,
) -> Image.Image:
    combined = Image.new("L", canvas_size, 0)
    for blur_factor, opacity_factor, y_factor in ((1.7, 0.32, 0.4), (1.0, 0.78, 1.0)):
        layer = Image.new("L", canvas_size, 0)
        alpha = card_mask.point(lambda value: round(value * opacity * opacity_factor))
        layer.paste(alpha, (position[0], position[1] + round(offset_y * y_factor)))
        layer = layer.filter(ImageFilter.GaussianBlur(max(1, round(blur * blur_factor))))
        combined = ImageChops.lighter(combined, layer)
    return combined


def polish(
    input_path: Path,
    output_path: Path,
    *,
    canvas_size: tuple[int, int],
    padding: int,
    radius: int,
    shadow_blur: int,
    shadow_opacity: float,
    shadow_offset_y: int,
    background_preset: str | None,
    background_image: Path | None,
    background_color: str | None,
    upscale: bool,
    trim_alpha: bool,
    quality: int,
) -> None:
    with Image.open(input_path) as source_file:
        source = ImageOps.exif_transpose(source_file).convert("RGBA")

    if trim_alpha:
        bbox = source.getchannel("A").getbbox()
        if bbox:
            source = source.crop(bbox)

    canvas_width, canvas_height = canvas_size
    if padding * 2 >= min(canvas_size):
        raise ValueError("Padding leaves no room for the screenshot.")

    if background_image:
        with Image.open(background_image) as custom_background:
            background = _fit_background(custom_background, canvas_size)
    elif background_color:
        background = Image.new("RGB", canvas_size, ImageColor.getrgb(background_color))
    else:
        background = render_background(background_preset or "coral-waves", canvas_size)

    max_width = canvas_width - padding * 2
    max_height = canvas_height - padding * 2
    scale = min(max_width / source.width, max_height / source.height)
    if not upscale:
        scale = min(1.0, scale)
    card_size = (max(1, round(source.width * scale)), max(1, round(source.height * scale)))
    source = source.resize(card_size, Image.Resampling.LANCZOS)
    radius = min(radius, card_size[0] // 2, card_size[1] // 2)
    card_mask = _rounded_mask(card_size, radius)

    card = Image.new("RGBA", card_size, (0, 0, 0, 0))
    card.paste(source, (0, 0), card_mask)
    border = Image.new("RGBA", card_size, (0, 0, 0, 0))
    ImageDraw.Draw(border).rounded_rectangle(
        (0, 0, card_size[0] - 1, card_size[1] - 1),
        radius=radius,
        outline=(255, 255, 255, 82),
        width=max(1, round(min(canvas_size) / 864)),
    )
    card = Image.alpha_composite(card, border)

    position = ((canvas_width - card_size[0]) // 2, (canvas_height - card_size[1]) // 2)
    composition = background.convert("RGBA")
    if shadow_opacity > 0 and shadow_blur > 0:
        shadow_alpha = _shadow_mask(
            canvas_size,
            card_mask,
            position,
            blur=shadow_blur,
            offset_y=shadow_offset_y,
            opacity=shadow_opacity,
        )
        shadow = Image.new("RGBA", canvas_size, (8, 12, 22, 0))
        shadow.putalpha(shadow_alpha)
        composition = Image.alpha_composite(composition, shadow)

    composition.alpha_composite(card, position)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = output_path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        composition.convert("RGB").save(output_path, quality=quality, optimize=True)
    elif suffix == ".webp":
        composition.save(output_path, quality=quality, method=6)
    else:
        composition.save(output_path, optimize=True)


def _command_polish(args: argparse.Namespace) -> int:
    try:
        polish(
            args.input,
            args.output,
            canvas_size=args.canvas,
            padding=args.padding,
            radius=args.radius,
            shadow_blur=args.shadow_blur,
            shadow_opacity=args.shadow_opacity,
            shadow_offset_y=args.shadow_offset_y,
            background_preset=args.background_preset,
            background_image=args.background_image,
            background_color=args.background_color,
            upscale=not args.no_upscale,
            trim_alpha=args.trim_alpha,
            quality=args.quality,
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(args.output.resolve())
    return 0


def _command_backgrounds(args: argparse.Namespace) -> int:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    names = args.preset or list(PRESETS)
    for name in names:
        output = args.output_dir / f"{name}.png"
        render_background(name, args.canvas).save(output, optimize=True)
        print(output.resolve())
    return 0


def _command_presets(args: argparse.Namespace) -> int:
    del args
    for name, description in PRESETS.items():
        print(f"{name:16} {description}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Polish screenshots locally with reusable compositions."
    )
    parser.add_argument("--version", action="version", version=VERSION)
    subparsers = parser.add_subparsers(dest="command", required=True)

    polish_parser = subparsers.add_parser("polish", help="Compose one screenshot.")
    polish_parser.add_argument("input", type=Path, help="Source screenshot path.")
    polish_parser.add_argument("--output", "-o", type=Path, required=True)
    polish_parser.add_argument("--canvas", type=parse_size, default=(1536, 864))
    polish_parser.add_argument("--padding", type=int, default=96)
    polish_parser.add_argument("--radius", type=int, default=22)
    polish_parser.add_argument("--shadow-blur", type=int, default=42)
    polish_parser.add_argument("--shadow-opacity", type=float, default=0.26)
    polish_parser.add_argument("--shadow-offset-y", type=int, default=24)
    background_group = polish_parser.add_mutually_exclusive_group()
    background_group.add_argument(
        "--background-preset", choices=PRESETS
    )
    background_group.add_argument("--background-image", type=Path)
    background_group.add_argument("--background-color")
    polish_parser.add_argument("--no-upscale", action="store_true")
    polish_parser.add_argument("--trim-alpha", action="store_true")
    polish_parser.add_argument("--quality", type=int, default=92)
    polish_parser.set_defaults(handler=_command_polish)

    backgrounds_parser = subparsers.add_parser(
        "backgrounds", help="Render reusable background PNGs."
    )
    backgrounds_parser.add_argument("--output-dir", type=Path, required=True)
    backgrounds_parser.add_argument("--canvas", type=parse_size, default=(1536, 864))
    backgrounds_parser.add_argument("--preset", action="append", choices=PRESETS)
    backgrounds_parser.set_defaults(handler=_command_backgrounds)

    presets_parser = subparsers.add_parser("presets", help="List built-in backgrounds.")
    presets_parser.set_defaults(handler=_command_presets)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if getattr(args, "padding", 0) < 0:
        raise SystemExit("--padding must be non-negative")
    if getattr(args, "radius", 0) < 0:
        raise SystemExit("--radius must be non-negative")
    if getattr(args, "shadow_blur", 0) < 0:
        raise SystemExit("--shadow-blur must be non-negative")
    if not 0 <= getattr(args, "shadow_opacity", 0) <= 1:
        raise SystemExit("--shadow-opacity must be between 0 and 1")
    if not 1 <= getattr(args, "quality", 92) <= 100:
        raise SystemExit("--quality must be between 1 and 100")
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
