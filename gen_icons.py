from PIL import Image, ImageDraw, ImageFont
import os

def make_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Blue gradient background
    r1, g1, b1 = 0x3B, 0x82, 0xF6
    r2, g2, b2 = 0x1D, 0x4E, 0xD8
    for y in range(size):
        t = y / size
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # Rounded corners
    radius = size // 5
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    img.putalpha(mask)

    # Draw "S" on separate layer then shear for motion feel
    s_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(s_layer)

    font_size = int(size * 0.62)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    bbox = s_draw.textbbox((0, 0), "S", font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (size - tw) / 2 - bbox[0]
    ty = (size - th) / 2 - bbox[1] - size * 0.04
    s_draw.text((tx, ty), "S", fill=(255, 255, 255, 255), font=font)

    # Shear right for italic/speed feel
    shear = 0.22
    s_layer = s_layer.transform(
        (size, size), Image.AFFINE,
        (1, shear, -shear * size * 0.5, 0, 1, 0),
        Image.BICUBIC
    )

    # Speed swoosh: two short arcs below-right of S
    sd = ImageDraw.Draw(s_layer)
    lw = max(2, int(size * 0.028))
    cx = int(size * 0.54)
    cy = int(size * 0.76)
    for i, (w, alpha) in enumerate([(0.38, 200), (0.24, 120)]):
        sw = int(size * w)
        sx = cx - sw // 2 + i * int(size * 0.06)
        sd.arc([sx, cy - lw * 2, sx + sw, cy + lw * 2],
               start=0, end=180,
               fill=(255, 255, 255, alpha), width=lw)

    img = Image.alpha_composite(img, s_layer)
    return img

os.makedirs("icons", exist_ok=True)
for sz in [512, 192, 180, 152, 120]:
    icon = make_icon(sz)
    if sz in [180, 152, 120]:
        bg = Image.new("RGB", (sz, sz), (0x3B, 0x82, 0xF6))
        bg.paste(icon, mask=icon.split()[3])
        bg.save(f"icons/icon-{sz}.png")
    else:
        icon.save(f"icons/icon-{sz}.png")

print("Done")
