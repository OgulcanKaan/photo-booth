from PIL import Image, ImageDraw, ImageFont
import os

# ── Sabitler ─────────────────────────────────────────────────
DPI = 300
def cm(val): return int(val * DPI / 2.54)

W = cm(10)      # 1181 px
H = cm(15)      # 1772 px

CARD_RED   = (196, 55, 40, 255)
DARK       = (40, 40, 40, 255)
WHITE      = (255, 255, 255, 255)
TRANS      = (255, 255, 255, 0)

# Ölçüler (cm → px)
LOGO_Y1    = cm(0.5)
LOGO_Y2    = cm(3.8)
LOGO_W     = cm(3.5)
LOGO_X     = (W - LOGO_W) // 2

PHOTO_Y1   = cm(4.0)
PHOTO_Y2   = cm(12.0)
PHOTO_X1   = cm(0.8)
PHOTO_X2   = W - cm(0.8)

SLOGAN_Y1  = cm(12.4)
SLOGAN_Y2  = cm(13.0)

LOVE_Y1    = cm(13.1)
LOVE_Y2    = cm(14.8)

BASE       = r"c:\Users\ogulc\Desktop\foto"

# ── Yazı tiplerini bul ────────────────────────────────────────
def find_font(names, size):
    """İlk bulunan fontu döndürür."""
    dirs = [r"C:\Windows\Fonts"]
    for name in names:
        for d in dirs:
            p = os.path.join(d, name)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)

slogan_sz = int((SLOGAN_Y2 - SLOGAN_Y1) * 0.65)
love_sz   = int((LOVE_Y2  - LOVE_Y1)  * 0.72)

font_slogan = find_font(["ariali.ttf", "arial.ttf", "calibrii.ttf"], slogan_sz)
font_love   = find_font(["MTCORSVA.TTF", "segoesc.ttf", "SEGOEPR.TTF", "Gabriola.ttf", "arial.ttf"], love_sz)

# ── Logo yükle (beyaz arka planı şeffaf yap) ─────────────────
logo_raw = Image.open(os.path.join(BASE, "logo.png")).convert("RGBA")
logo_h   = LOGO_Y2 - LOGO_Y1
logo_r   = logo_raw.resize((LOGO_W, logo_h), Image.LANCZOS)

# Beyaz pikselleri şeffaf yap
px = logo_r.load()
for y in range(logo_r.height):
    for x in range(logo_r.width):
        r, g, b, a = px[x, y]
        if r > 240 and g > 240 and b > 240:
            px[x, y] = (r, g, b, 0)

# ── 1) PREVIEW (gri foto alanı) ───────────────────────────────
preview = Image.new("RGBA", (W, H), WHITE)
draw_p  = ImageDraw.Draw(preview)

# Fotoğraf alanı placeholder
draw_p.rectangle([PHOTO_X1, PHOTO_Y1, PHOTO_X2, PHOTO_Y2],
                 fill=(220, 220, 220, 255), outline=(180, 180, 180, 255), width=3)

# Logo
preview.paste(logo_r, (LOGO_X, LOGO_Y1), logo_r)

# Slogan
slogan_cx = W // 2
slogan_cy = (SLOGAN_Y1 + SLOGAN_Y2) // 2
draw_p.text((slogan_cx, slogan_cy), "Coffee & Memories, Together!",
            fill=DARK, font=font_slogan, anchor="mm")

# Sticker zone - left blank, drawn dynamically by web app
love_cx = W // 2
love_cy = (LOVE_Y1 + LOVE_Y2) // 2
# Draw dashed placeholder in preview only
for i in range(0, int(cm(4.8)), 20):
    draw_p.line([love_cx - cm(2.4) + i, love_cy, love_cx - cm(2.4) + i + 10, love_cy],
                fill=(200, 200, 200, 255), width=2)

preview.save(os.path.join(BASE, "frame_preview.png"), dpi=(DPI, DPI))
print("OK: frame_preview.png saved")

# ── 2) OVERLAY (saydam PNG — foto alani delik) ───────────────
overlay = Image.new("RGBA", (W, H), TRANS)
draw_o  = ImageDraw.Draw(overlay)

# Ust bolge (logo + bosluk)
draw_o.rectangle([0, 0, W, PHOTO_Y1], fill=WHITE)
# Sol kenarlik
draw_o.rectangle([0, PHOTO_Y1, PHOTO_X1, PHOTO_Y2], fill=WHITE)
# Sag kenarlik
draw_o.rectangle([PHOTO_X2, PHOTO_Y1, W, PHOTO_Y2], fill=WHITE)
# Alt bolge
draw_o.rectangle([0, PHOTO_Y2, W, H], fill=WHITE)

# Logo
overlay.paste(logo_r, (LOGO_X, LOGO_Y1), logo_r)

# Slogan
draw_o2 = ImageDraw.Draw(overlay)
draw_o2.text((slogan_cx, slogan_cy), "Coffee & Memories, Together!",
             fill=DARK, font=font_slogan, anchor="mm")
# Sticker zone left transparent - web app draws sticker dynamically

overlay.save(os.path.join(BASE, "frame_overlay.png"), dpi=(DPI, DPI))
print("OK: frame_overlay.png saved (transparent PNG)")
print(f"Card: {W} x {H} px @ {DPI} DPI")
print(f"Logo : y={LOGO_Y1}-{LOGO_Y2}  x={LOGO_X}-{LOGO_X+LOGO_W}")
print(f"Photo: y={PHOTO_Y1}-{PHOTO_Y2}  x={PHOTO_X1}-{PHOTO_X2}")
print(f"Slogan cy={slogan_cy}  Love cy={love_cy}")
