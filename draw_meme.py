#!/usr/bin/env python3
"""Draw the gta6-meme-x-01 entry: Vice City / Leonida sunset postcard with the
official make.fun ghost (sunglasses on) sitting on a retro convertible's hood.
1200x1200 PNG, PIL only."""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1200, 1200
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

img = Image.new("RGB", (W, H))
d = ImageDraw.Draw(img)

# ---------- sky: vertical gradient hot pink -> orange ----------
top = (255, 46, 126)      # hot pink
mid = (255, 94, 77)
bot = (255, 138, 42)      # orange at horizon
HORIZON = 640
for y in range(HORIZON):
    t = y / HORIZON
    if t < 0.5:
        u = t / 0.5
        c = tuple(int(top[i] + (mid[i] - top[i]) * u) for i in range(3))
    else:
        u = (t - 0.5) / 0.5
        c = tuple(int(mid[i] + (bot[i] - mid[i]) * u) for i in range(3))
    d.line([(0, y), (W, y)], fill=c)

# ---------- sun disc, low on the horizon ----------
SUN_C = (600, 590)
SUN_R = 150
# soft glow
glow = Image.new("RGB", (W, H), (0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([SUN_C[0] - SUN_R - 60, SUN_C[1] - SUN_R - 60,
            SUN_C[0] + SUN_R + 60, SUN_C[1] + SUN_R + 60],
           fill=(255, 190, 90))
glow = glow.filter(ImageFilter.GaussianBlur(45))
img = Image.blend(img, Image.composite(glow, img, glow.convert("L").point(lambda v: v // 3)), 1.0)
d = ImageDraw.Draw(img)
d.ellipse([SUN_C[0] - SUN_R, SUN_C[1] - SUN_R,
           SUN_C[0] + SUN_R, SUN_C[1] + SUN_R], fill=(255, 233, 168))

# ---------- sea band ----------
SEA_TOP, SEA_BOT = HORIZON, 800
for y in range(SEA_TOP, SEA_BOT):
    t = (y - SEA_TOP) / (SEA_BOT - SEA_TOP)
    c = tuple(int(a + (b - a) * t) for a, b in zip((64, 22, 96), (24, 8, 44)))
    d.line([(0, y), (W, y)], fill=c)
# sun reflection streaks on the water
for i, (yy, half_w, alpha) in enumerate([
        (655, 150, 255), (680, 115, 230), (705, 160, 200),
        (730, 95, 180), (755, 130, 150), (780, 80, 120)]):
    d.rounded_rectangle([SUN_C[0] - half_w, yy, SUN_C[0] + half_w, yy + 10],
                        radius=5, fill=(255, 190, 110))

# ---------- ground / road band + bottom caption strip ----------
d.rectangle([0, SEA_BOT, W, 1040], fill=(60, 26, 84))
d.rectangle([0, 1040, W, H], fill=(16, 6, 30))

SIL = (18, 8, 32)   # near-black silhouette purple

# ---------- LEONIDA building silhouette + neon sign (left horizon) ----------
d.rectangle([210, 566, 380, HORIZON], fill=SIL)
d.rectangle([240, 540, 350, 566], fill=SIL)  # rooftop block
neon = ImageFont.truetype(FONT_BOLD, 40)
# neon glow: draw text several times with blur via a temp layer
sign_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(sign_layer)
sd.text((295, 496), "LEONIDA", font=neon, fill=(255, 94, 196, 255),
        anchor="mm", stroke_width=2, stroke_fill=(255, 94, 196, 255))
glow_layer = sign_layer.filter(ImageFilter.GaussianBlur(6))
img.paste(Image.alpha_composite(img.convert("RGBA"), glow_layer).convert("RGB"), (0, 0))
img.paste(Image.alpha_composite(img.convert("RGBA"), sign_layer).convert("RGB"), (0, 0))
d = ImageDraw.Draw(img)


def bezier(p0, p1, p2, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts


def draw_palm(base_x, base_y, height, lean, scale=1.0):
    """Simple palm silhouette: curved trunk + drooping fronds."""
    top_x = base_x + lean
    top_y = base_y - height
    # trunk: tapered polygon along a curve
    spine = bezier((base_x, base_y), (base_x + lean * 0.3, base_y - height * 0.55),
                   (top_x, top_y), n=20)
    w0, w1 = 16 * scale, 7 * scale
    left, right = [], []
    for i, (x, y) in enumerate(spine):
        t = i / (len(spine) - 1)
        w = w0 + (w1 - w0) * t
        # perpendicular approx: trunk mostly vertical
        left.append((x - w, y))
        right.append((x + w, y))
    d.polygon(left + right[::-1], fill=SIL)
    # fronds: 7 curved leaves fanning from the crown
    for ang_deg, length in [(-165, 150), (-135, 175), (-105, 185), (-75, 185),
                            (-45, 175), (-15, 150), (10, 120)]:
        a = math.radians(ang_deg)
        tip = (top_x + math.cos(a) * length * scale,
               top_y + math.sin(a) * length * scale * 0.55 + 55 * scale)
        ctrl = (top_x + math.cos(a) * length * 0.55 * scale,
                top_y + math.sin(a) * length * 0.55 * scale * 0.55 - 18 * scale)
        curve = bezier((top_x, top_y), ctrl, tip, n=16)
        # leaf thickness: second curve offset down
        curve2 = bezier((top_x, top_y + 10 * scale),
                        (ctrl[0], ctrl[1] + 14 * scale),
                        (tip[0], tip[1] + 8 * scale), n=16)
        d.polygon(curve + curve2[::-1], fill=SIL)
    # coconuts
    d.ellipse([top_x - 16 * scale, top_y + 2, top_x - 2 * scale, top_y + 16 * scale], fill=SIL)
    d.ellipse([top_x + 2 * scale, top_y + 4, top_x + 16 * scale, top_y + 18 * scale], fill=SIL)


draw_palm(95, 1040, 640, 55, scale=1.0)     # left palm
draw_palm(1115, 1040, 600, -50, scale=0.95)  # right palm

# ---------- retro convertible silhouette (bottom, spans the road) ----------
CAR_Y0 = 905   # top of body / windshield
CAR_Y1 = 1015  # bottom of body
car_body = [
    (95, 1000), (110, 955), (170, 945), (300, 940),          # front bumper -> hood
    (430, 938), (470, 905), (520, 900), (640, 900),          # windshield base -> open top
    (700, 900), (760, 940), (880, 945), (1060, 950),         # rear deck
    (1105, 960), (1110, 1000), (1100, 1015), (120, 1015),     # rear bumper -> underbody
]
d.polygon(car_body, fill=SIL)
# windshield (open-top frame hint)
d.polygon([(470, 905), (520, 900), (560, 900), (560, 938), (480, 938)], fill=(40, 18, 60))
# wheels
for cx in (300, 930):
    d.ellipse([cx - 52, 948, cx + 52, 1052], fill=(8, 4, 16))
    d.ellipse([cx - 24, 976, cx + 24, 1024], fill=(52, 26, 74))
# magenta rim-light along the hood / top edge
d.line([(170, 945), (430, 938)], fill=(255, 94, 150), width=3)
d.line([(760, 940), (1060, 950)], fill=(255, 94, 150), width=3)

# ---------- make.fun ghost, LARGE, sitting on the hood ----------
ghost = Image.open("ghost.png").convert("RGBA")
GH = 440                      # ~37% of image height
GW = int(GHOST_W := GH * ghost.width / ghost.height)
ghost = ghost.resize((GW, GH), Image.LANCZOS)
GX, GY = 690, 530             # bottom edge lands on the hood (~970)
img.paste(ghost, (GX, GY), ghost)
d = ImageDraw.Draw(img)
# sunglasses drawn on the ghost: two black rounded rectangles + bridge band.
# Ghost eyes sit at ~(0.42, 0.42) and ~(0.56, 0.415) of the mark.
sx = GX + 0.42 * GW
sy = GY + 0.42 * GH
rx = GX + 0.565 * GW
ry = GY + 0.415 * GH
LW, LH = 60, 48
d.rounded_rectangle([sx - LW / 2, sy - LH / 2, sx + LW / 2, sy + LH / 2],
                    radius=14, fill=(10, 6, 18))
d.rounded_rectangle([rx - LW / 2, ry - LH / 2, rx + LW / 2, ry + LH / 2],
                    radius=14, fill=(10, 6, 18))
d.rectangle([sx + LW / 2 - 4, sy - 7, rx - LW / 2 + 4, sy + 7], fill=(10, 6, 18))
# tiny shine on the lenses
d.line([(sx - LW / 2 + 12, sy + LH / 2 - 10), (sx - LW / 2 + 30, sy - LH / 2 + 10)],
       fill=(255, 255, 255), width=5)
d.line([(rx - LW / 2 + 12, ry + LH / 2 - 10), (rx - LW / 2 + 30, ry - LH / 2 + 10)],
       fill=(255, 255, 255), width=5)

# ---------- captions: bold white, thick black outline, ALL CAPS, centred ----------
def fit_font(text, start_size, max_w):
    size = start_size
    while size > 20:
        f = ImageFont.truetype(FONT_BOLD, size)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return ImageFont.truetype(FONT_BOLD, size)


def outlined_text(cx, y, text, font, fill=(255, 255, 255)):
    d.text((cx, y), text, font=font, fill=fill, anchor="ma",
           stroke_width=max(3, font.size // 14), stroke_fill=(0, 0, 0))


top_font = fit_font("WAITED 13 YEARS FOR GTA 6", 72, 1140)
outlined_text(W // 2, 34, "WAITED 13 YEARS FOR GTA 6", top_font)

bot_font = fit_font("MAKING MEMES ABOUT IT", 60, 1140)
outlined_text(W // 2, 1052, "MY AI AGENT GOT PAID", bot_font)
outlined_text(W // 2, 1122, "MAKING MEMES ABOUT IT", bot_font)

img.save("meme.png")
print("saved meme.png", img.size)
