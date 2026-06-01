"""Generate a 16:9 cover image for the Mantle Alpha Trading Agent hackathon submission.

Style: dark tech / AI trading / audit log / on-chain verification.
Output: cover_16x9.png (1920x1080)
"""

from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1920, 1080
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover_16x9.png")


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    h = hex_str.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Try common monospace/system fonts."""
    candidates = [
        "CascadiaCode.ttf",
        "CascadiaMono.ttf",
        "JetBrainsMono-Regular.ttf",
        "FiraCode-Regular.ttf",
        "consola.ttf",
        "cour.ttf",
        "arial.ttf",
        "segoeui.ttf",
    ]
    bold_candidates = [
        "CascadiaCode-Bold.ttf",
        "CascadiaMono-Bold.ttf",
        "JetBrainsMono-Bold.ttf",
        "FiraCode-Bold.ttf",
        "consolab.ttf",
        "courbd.ttf",
        "arialbd.ttf",
        "segoeuib.ttf",
    ]
    names = bold_candidates if bold else candidates
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    # Fallback
    try:
        return ImageFont.truetype("arial.ttf", size)
    except (OSError, IOError):
        return ImageFont.load_default()


def draw_text(
    draw: ImageDraw.Draw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    anchor: str = "lt",
):
    draw.text(xy, text, fill=fill, font=font, anchor=anchor)


def main():
    # Colors
    bg = hex_to_rgb("#0a0e17")         # dark navy-black
    accent = hex_to_rgb("#00d4aa")     # Mantle green
    accent2 = hex_to_rgb("#6366f1")    # indigo/purple
    text_white = hex_to_rgb("#e2e8f0")
    text_dim = hex_to_rgb("#64748b")
    line_color = hex_to_rgb("#1e293b")

    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    font_title = get_font(64, bold=True)
    font_sub = get_font(28, bold=False)
    font_body = get_font(22, bold=False)
    font_mono = get_font(18, bold=False)
    font_small = get_font(16, bold=False)

    # ---- Background grid lines (subtle) ----
    for x in range(0, W, 80):
        draw.line([(x, 0), (x, H)], fill=line_color, width=1)
    for y in range(0, H, 80):
        draw.line([(0, y), (W, y)], fill=line_color, width=1)

    # ---- Left accent bar ----
    draw.rectangle([(0, 0), (6, H)], fill=accent)

    # ---- Top-right decor ----
    draw.rectangle([(W - 400, 0), (W, 4)], fill=accent2)

    # ---- Title ----
    draw_text(draw, (80, 180), "MANTLE ALPHA", font_title, text_white)
    draw_text(draw, (80, 260), "TRADING AGENT", font_title, accent)

    # ---- Subtitle ----
    draw_text(draw, (86, 340), "Mantle Turing Test Hackathon 2026  |  AI Trading Strategy", font_sub, text_dim)

    # ---- Separator ----
    draw.line([(80, 400), (W - 80, 400)], fill=accent, width=2)

    # ---- Left column: Architecture ----
    y = 450
    draw_text(draw, (80, y), "ARCHITECTURE", font_sub, accent)
    y += 50
    arch_lines = [
        "mock market data",
        "       |",
        "       v",
        "  signal engine  (momentum + mean reversion + vol breakout)",
        "       |",
        "       v",
        "  risk policy     (edge / confidence / exposure / Kelly)",
        "       |",
        "       v",
        "  dry-run trader  (paper trading only)",
        "       |",
        "       v",
        "  audit logger    (JSONL decision trail)",
        "       |",
        "       v",
        "  terminal dashboard",
    ]
    for line in arch_lines:
        draw_text(draw, (80, y), line, font_mono, text_dim)
        y += 28

    # ---- Right column: Key Metrics ----
    ry = 450
    draw_text(draw, (W // 2 + 80, ry), "KEY METRICS", font_sub, accent2)
    ry += 55
    metrics = [
        ("Tests", "37 / 37  passing"),
        ("Signals", "momentum  |  mean reversion  |  vol breakout"),
        ("Risk Checks", "6-layer policy  |  quarter-Kelly sizing"),
        ("Execution", "DRY RUN  only  (zero real funds)"),
        ("Audit", "JSONL  logs  (ready for on-chain anchoring)"),
        ("Dependencies", "zero  (fully offline demo)"),
    ]
    for label, value in metrics:
        draw_text(draw, (W // 2 + 80, ry), f"[{label}]", font_body, accent)
        draw_text(draw, (W // 2 + 220, ry), value, font_mono, text_dim)
        ry += 40

    # ---- Bottom: Mantle roadmap ----
    ry += 40
    draw.line([(80, ry), (W - 80, ry)], fill=line_color, width=1)
    ry += 30
    draw_text(draw, (80, ry), "MANTLE ON-CHAIN ROADMAP", font_sub, accent)
    ry += 45
    phases = [
        "Phase 1: Identity      — Sign agent decisions with Mantle wallet",
        "Phase 2: Anchoring     — Merkle root of decisions on-chain",
        "Phase 3: Reputation    — Verifiable performance history",
        "Phase 4: Marketplace   — Decentralized strategy composability",
    ]
    for phase in phases:
        draw_text(draw, (80, ry), phase, font_mono, text_white)
        ry += 30

    # ---- Bottom bar ----
    draw.rectangle([(0, H - 50), (W, H)], fill=hex_to_rgb("#060a10"))
    draw_text(draw, (80, H - 35), "github.com/YYYCCCV/mantle-turing-trading-agent", font_small, text_dim)
    draw_text(draw, (W - 280, H - 35), "Mantle Turing Test  |  DoraHacks 2026", font_small, text_dim)

    # ---- Bottom right decor ----
    draw.rectangle([(W - 4, H - 200), (W, H - 50)], fill=accent)

    img.save(OUTPUT, "PNG")
    print(f"[Cover] Saved: {OUTPUT}")
    print(f"[Cover] Size: {W}x{H}")


if __name__ == "__main__":
    main()
