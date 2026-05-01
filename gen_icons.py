from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

def make_icon(size):
    # ── 背景：深藏青色 ──────────────────────────────────────
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    bg_top    = (0x1A, 0x1F, 0x5E)
    bg_bottom = (0x12, 0x16, 0x42)
    for y in range(size):
        t = y / size
        r = int(bg_top[0] + (bg_bottom[0] - bg_top[0]) * t)
        g = int(bg_top[1] + (bg_bottom[1] - bg_top[1]) * t)
        b = int(bg_top[2] + (bg_bottom[2] - bg_top[2]) * t)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # 圆角 mask
    radius = int(size * 0.22)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size - 1, size - 1], radius=radius, fill=255)
    img.putalpha(mask)

    # ── 渐变色板：粉→紫→青 ────────────────────────────────
    stops = [
        (0.0,  (0xFF, 0x6E, 0xC7)),   # 亮粉
        (0.45, (0x9B, 0x59, 0xFF)),   # 紫
        (1.0,  (0x3D, 0xE8, 0xD8)),   # 青绿
    ]

    def gradient_color(t):
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                f = (t - t0) / (t1 - t0)
                return tuple(int(c0[j] + (c1[j] - c0[j]) * f) for j in range(3))
        return stops[-1][1]

    grad = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    for y in range(size):
        c = gradient_color(y / size)
        ImageDraw.Draw(grad).line([(0, y), (size, y)], fill=(*c, 255))

    # ── 绘制 S 为 mask ─────────────────────────────────────
    font_size = int(size * 0.68)
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    s_mask = Image.new("L", (size, size), 0)
    sd = ImageDraw.Draw(s_mask)
    bbox = sd.textbbox((0, 0), "S", font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (size - tw) / 2 - bbox[0]
    ty = (size - th) / 2 - bbox[1] - int(size * 0.02)
    sd.text((tx, ty), "S", fill=255, font=font)

    # ── 发光层（模糊版 S）─────────────────────────────────
    glow_layer = grad.copy()
    glow_mask = s_mask.filter(ImageFilter.GaussianBlur(int(size * 0.055)))
    glow_layer.putalpha(glow_mask)

    # ── 清晰 S 层 ──────────────────────────────────────────
    sharp_layer = grad.copy()
    sharp_layer.putalpha(s_mask)

    # ── 合成 ───────────────────────────────────────────────
    result = img.copy()
    result = Image.alpha_composite(result, glow_layer)
    result = Image.alpha_composite(result, sharp_layer)

    # 重新施加圆角（合成后还原 alpha）
    final_mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(final_mask).rounded_rectangle(
        [0, 0, size - 1, size - 1], radius=radius, fill=255)
    result.putalpha(final_mask)
    return result

os.makedirs("icons", exist_ok=True)
for sz in [512, 192, 180, 152, 120]:
    icon = make_icon(sz)
    if sz in [180, 152, 120]:
        bg = Image.new("RGB", (sz, sz), (0x1A, 0x1F, 0x5E))
        bg.paste(icon, mask=icon.split()[3])
        bg.save(f"icons/icon-{sz}.png")
    else:
        icon.save(f"icons/icon-{sz}.png")

print("Done")
