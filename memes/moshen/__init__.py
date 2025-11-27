from datetime import datetime
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFont
from pil_utils import BuildImage
from meme_generator import add_meme
from meme_generator.utils import save_gif

# ----------
plugin_dir = Path(__file__).parent
img_dir = plugin_dir / "images"

font_role_path = plugin_dir / "fonts" / "font1.ttf"
font_message_path = plugin_dir / "fonts" / "font3.ttf"

CHAR_TEXTS = {
    'alisa': ("紫藤亚里沙", "#EA4A3A"), 'anan': ("夏目安安", "#A897FF"),
    'coco': ("泽渡可可", "#F7714C"), 'ema': ("樱羽艾玛", "#FF8DB3"),
    'hanna': ("远野汉娜", "#ACC81E"), 'hiro': ("二阶堂希罗", "#EC4348"),
    'mago': ("宝生玛格", "#A36FD4"), 'meruru': ("冰上梅露露", "#E3B4AA"),
    'miria': ("佐伯米莉亚", "#EDCB84"), 'nanoka': ("黑部奈叶香", "#858E93"),
    'noa': ("城崎诺亚", "#66E2EC"), 'reia': ("莲见蕾雅", "#FFB269"),
    'sherri': ("橘雪莉", "#7CABFF"), 'yuki': ("月代雪", "#C3D5E9"),
}

# ----------
text_area_left = 770
text_area_top = 320
text_area_width = 1858
text_area_height = 480
usable_width = text_area_width - 120

char_spacing = -1
typing_speed = 75


_measure_draw = ImageDraw.Draw(Image.new("RGBA", (text_area_width, text_area_height)))
# ----------
def char_width(text, font):
    """逐字测宽（加 char_spacing）。"""
    w = 0
    for c in text:
        bbox = _measure_draw.textbbox((0, 0), c, font=font)
        w += (bbox[2] - bbox[0]) + char_spacing
    return w

def wrap_text(text, font):
    """静态模式使用的普通 wrap。"""
    lines, ln = [], ""
    for ch in text:
        if char_width(ln + ch, font) > usable_width:
            lines.append(ln)
            ln = ch
        else:
            ln += ch
    if ln:
        lines.append(ln)
    return lines

# ----------滚动换行
def wrap_text_scroll(text, font, max_lines=4):
    lines = []
    current = ""

    for ch in text:
        if char_width(current + ch, font) > usable_width:
            lines.append(current)
            current = ch
        else:
            current += ch

        if current:
            temp = lines + [current]
            if len(temp) > max_lines:
                temp = temp[-max_lines:]
            yield temp

    final = lines + ([current] if current else [])
    if len(final) > max_lines:
        final = final[-max_lines:]
    yield final

# ----------静态文本绘制
def draw_wrapped_text(frame, text, font, line_h, line_sp, max_lines):
    layer = Image.new("RGBA", (text_area_width, text_area_height))
    draw = ImageDraw.Draw(layer)

    lines = wrap_text(text, font)
    if len(lines) > max_lines:
        lines = lines[-max_lines:]

    y = 0
    for ln in lines:
        x = 0
        for ch in ln:
            bbox = draw.textbbox((0, 0), ch, font=font)
            draw.text((x, y), ch, font=font, fill="white")
            x += (bbox[2] - bbox[0]) + char_spacing
        y += line_h + line_sp

    frame.paste(layer, (text_area_left, text_area_top), layer)

# ----------gif文本绘制
def draw_wrapped_text_scroll(frame, lines, font, line_h, line_sp):
    layer = Image.new("RGBA", (text_area_width, text_area_height))
    draw = ImageDraw.Draw(layer)

    y = 0
    for ln in lines:
        x = 0
        for ch in ln:
            bbox = draw.textbbox((0, 0), ch, font=font)
            draw.text((x, y), ch, font=font, fill="white")
            x += (bbox[2] - bbox[0]) + char_spacing
        y += line_h + line_sp

    frame.paste(layer, (text_area_left, text_area_top), layer)

# ----------字体
def determine_font(text, max_fs=80, min_fs=32):
    if not font_message_path.exists():
        f = ImageFont.load_default()
        a, d = f.getmetrics()
        return f, a + d, int(20 * 0.45), wrap_text(text, f)

    for fs in range(max_fs, min_fs - 1, -1):
        f = ImageFont.truetype(str(font_message_path), fs)
        a, d = f.getmetrics()
        lh = a + d
        ls = int(fs * 0.45)

        lines = wrap_text(text, f)
        total_h = lh * len(lines) + ls * (len(lines) - 1)

        if total_h <= text_area_height - 10:
            return f, lh, ls, lines

    f = ImageFont.truetype(str(font_message_path), min_fs)
    a, d = f.getmetrics()
    return f, a + d, int(min_fs * 0.45), wrap_text(text, f)

# ----------角色名文本绘制
def draw_character_name(frame, char_text, folder_name, first_color):
    target_x, target_y = 855 - 285, 215 - 75
    ratio = 0.75 if folder_name == "sherri" else 0.5
    ex = 0.25 if folder_name == "sherri" else 0

    layer = Image.new("RGBA", frame.size)
    d = ImageDraw.Draw(layer)

    char_imgs = []
    for i, ch in enumerate(char_text):
        if i == 0:
            fs, color = 110, first_color
        elif i == 2 and folder_name == "sherri":
            fs = int(110 * ratio * (1 - ex * 2))
            color = "white"
        elif i == 2:
            fs = 110
            color = "white"
        else:
            fs = int(110 * ratio)
            color = "white"

        try:
            f = ImageFont.truetype(str(font_role_path), fs)
        except:
            f = ImageFont.load_default()

        bbox = d.textbbox((0, 0), ch, font=f)
        img = Image.new("RGBA", (bbox[2] - bbox[0], bbox[3] - bbox[1]))
        ImageDraw.Draw(img).text((-bbox[0], -bbox[1]), ch, font=f, fill=color)
        char_imgs.append(img)

    max_h = max(im.height for im in char_imgs)
    x = target_x - (char_imgs[0].width // 2)
    y = target_y - (max_h // 2)

    for i, img in enumerate(char_imgs):
        dy = (max_h - img.height) if (i != 0 and (i != 2 or folder_name == "sherri")) else 0
        layer.paste(img, (x, y + dy), img)
        x += img.width

    layer = layer.resize((int(layer.width * 1.5), int(layer.height * 1.5)), Image.BICUBIC)
    frame.paste(layer, (0, 0), layer)

# ----------主
def mo_shen(images, texts, args):
    text = texts[0] if texts else "啥啊"

    is_typing = text.startswith("逐字")
    if is_typing:
        text = text[2:].strip()

    base = Image.open(random.choice(list((img_dir / "background").glob("*")))).convert("RGBA")
    w, h = base.size

    folder = random.choice(list(CHAR_TEXTS.keys()))
    char_text, first_color = CHAR_TEXTS[folder]
    icon = Image.open(random.choice(list((img_dir / folder).glob("*")))).convert("RGBA")
    icon_w, icon_h = icon.size

    font, lh, ls, full_lines = determine_font(text)
    max_lines = len(full_lines)

    # ----------静态
    if not is_typing:
        frame = base.copy()
        frame.paste(icon, (0, h - icon_h), icon)
        draw_wrapped_text(frame, text, font, lh, ls, max_lines)
        draw_character_name(frame, char_text, folder, first_color)
        return BuildImage(frame).save_jpg()

    # ----------逐字
    typing_font_size = 80
    typing_font = ImageFont.truetype(str(font_message_path), typing_font_size)

    a, d = typing_font.getmetrics()
    typing_lh = a + d
    typing_ls = 18

    static_bg = base.copy()
    static_bg.paste(icon, (0, h - icon_h), icon)
    draw_character_name(static_bg, char_text, folder, first_color)

    frames = []
    scroller = wrap_text_scroll(text, typing_font, max_lines=4)

    for lines in scroller:
        f = static_bg.copy()
        draw_wrapped_text_scroll(f, lines, typing_font, typing_lh, typing_ls)
        frames.append(f)

    frames.extend([frames[-1]] * 12)

    return save_gif(frames, duration=typing_speed / 1000)

add_meme(
    "moshen",
    mo_shen,
    min_texts=0,
    max_texts=1,
    default_texts=["啥啊"],
    keywords=["魔审", "moshen"],
    date_created=datetime(2025, 11, 25),
    date_modified=datetime(2025, 11, 27),
)
