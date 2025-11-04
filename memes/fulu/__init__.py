from datetime import datetime
from pathlib import Path
from PIL import ImageFont, ImageDraw, Image, ImageEnhance, ImageFilter
from pil_utils import BuildImage
from meme_generator import add_meme
import math

plugin_dir = Path(__file__).parent
img_dir = plugin_dir / "images"

# 字体全局变量
custom_font = None

def load_custom_font():
    """延迟加载字体，只有在使用fulu插件时才加载"""
    global custom_font
    if custom_font is None:
        font_path = plugin_dir / "fonts" / "zhylzs.ttf"
        if font_path.exists():
            try:
                custom_font = ImageFont.truetype(str(font_path), 160)
                print(f"[符箓] 成功加载字体: {font_path.name}")
            except Exception as e:
                print(f"[符箓] 字体加载失败: {e}")
        else:
            print(f"[符箓] 未找到字体文件: {font_path}")


def fulu(images, texts: list[str], args):
    global custom_font  # <-- 这里必须加

    # 延迟加载字体
    load_custom_font()

    text = texts[0] if texts else "恭喜发财"
    chars = list(text)
    n = len(chars)

    canvas_w = 1000
    canvas_h = 1536

    top_limit = 725
    bottom_limit = 1525
    usable_height = bottom_limit - top_limit

    # 动态列数
    if n <= 4:
        cols = 1
    elif n <= 8:
        cols = 2
    else:
        cols = 3

    rows_per_col = math.ceil(n / cols)
    per_char_h = usable_height / rows_per_col

    # 字体大小
    if n == 1:
        font_size = int(per_char_h * 0.8)
    elif n == 2:
        font_size = int(per_char_h * 1.2)
    elif n <= 4:
        font_size = int(per_char_h * 1.5)
    elif n <= 8:
        font_size = int(per_char_h * 1.05)
    else:
        font_size = int(per_char_h * 0.95)

    # 行距
    char_gap = int(per_char_h * 0.01) if n <= 4 else int(per_char_h * 0.05)

    if cols == 1:
        col_spacing = font_size * 1.8
    elif cols == 2:
        col_spacing = font_size * 0.7
    else:
        col_spacing = font_size * 0.6

    center_x = canvas_w // 2
    x_positions = [int(center_x + (i - (cols - 1) / 2) * col_spacing) for i in range(cols)][::-1]

    # 背景
    try:
        bg = BuildImage.open(img_dir / "0.png").convert("RGBA")
    except Exception:
        bg = BuildImage.new("RGBA", (canvas_w, canvas_h), (255, 250, 180))

    # 文字层
    text_layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)
    fill_color = (158, 44, 7)

    if custom_font is None:
        try:
            custom_font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            custom_font = ImageFont.load_default()

    total_text_height = rows_per_col * (per_char_h - char_gap)
    vertical_margin = max((usable_height - total_text_height) / 2 - 50, 0)

    if n == 1:
        vertical_shift = 250
    elif n == 2:
        vertical_shift = 80
    elif n == 3:
        vertical_shift = 20
    else:
        vertical_shift = 0

    # 绘制竖排文字
    idx = 0
    for col in range(cols):
        for row in range(rows_per_col):
            if idx >= n:
                break
            x = x_positions[col]
            y = top_limit + vertical_margin + vertical_shift + row * (per_char_h - char_gap)
            draw.text(
                (x, y),
                chars[idx],
                font=custom_font.font_variant(size=font_size),
                fill=fill_color,
                anchor="mm",
            )
            idx += 1

    combined = bg.image.copy()
    combined.alpha_composite(text_layer)

    # 朱砂滤镜
    red_overlay = Image.new("RGBA", (canvas_w, canvas_h), (255, 70, 40, 35))
    combined.alpha_composite(red_overlay)
    combined = ImageEnhance.Contrast(combined).enhance(1.03)
    combined = ImageEnhance.Color(combined).enhance(1.1)
    combined = combined.filter(ImageFilter.GaussianBlur(radius=0.8))

    return BuildImage(combined).save_jpg()


add_meme(
    "fulu",
    fulu,
    min_texts=0,
    max_texts=1,
    default_texts=["恭喜发财"],
    keywords=["符箓"],
    date_created=datetime(2025, 11, 3),
    date_modified=datetime(2025, 11, 3),
)
