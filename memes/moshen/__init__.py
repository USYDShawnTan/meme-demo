from datetime import datetime
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFont
from pil_utils import BuildImage
from meme_generator import add_meme
from meme_generator.utils import save_gif

# ---------- 路径与资源 ---------- #
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

# ---------- 文本区域参数 ---------- #
text_area_left = 770
text_area_top = 320
text_area_width = 1858
text_area_height = 480

usable_width = text_area_width - 120
char_spacing = -1
typing_speed = 75

# ---------- 基础测量功能 ---------- #
def _measure_draw():
    return ImageDraw.Draw(Image.new("RGBA", (text_area_width, text_area_height)))

def char_width(draw, s, font):
    w = 0
    for c in s:
        bbox = draw.textbbox((0, 0), c, font=font)
        w += (bbox[2] - bbox[0]) + char_spacing
    return w

def wrap_text(s, draw, font):
    lines, ln = [], ""
    for ch in s:
        if char_width(draw, ln + ch, font) > usable_width:
            lines.append(ln)
            ln = ch
        else:
            ln += ch
    if ln:
        lines.append(ln)
    return lines

# ---------- 角色名绘制（版本1 保留） ---------- #
def draw_character_name(frame, char_text, folder_name, first_color):
    target_x, target_y = 855 - 285, 215 - 75
    ratio = 0.75 if folder_name == "sherri" else 0.5
    ex = 0.25 if folder_name == "sherri" else 0

    layer = Image.new("RGBA", frame.size)
    draw = ImageDraw.Draw(layer)

    char_imgs = []
    for i, ch in enumerate(char_text):
        if i == 0:
            fs, color = 110, first_color
        elif i == 2 and folder_name == "sherri":
            fs, color = int(110 * ratio * (1 - ex * 2)), "white"
        elif i == 2:
            fs, color = 110, "white"
        else:
            fs, color = int(110 * ratio), "white"

        try:
            f = ImageFont.truetype(str(font_role_path), fs)
        except:
            f = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), ch, font=f)
        img = Image.new("RGBA", (bbox[2] - bbox[0], bbox[3] - bbox[1]))
        ImageDraw.Draw(img).text((-bbox[0], -bbox[1]), ch, font=f, fill=color)
        char_imgs.append(img)

    max_h = max(img.height for img in char_imgs)
    x = target_x - (char_imgs[0].width // 2)
    y = target_y - (max_h // 2)

    for i, img in enumerate(char_imgs):
        dy = (max_h - img.height) if (i != 0 and (i != 2 or folder_name == "sherri")) else 0
        layer.paste(img, (x, y + dy), img)
        x += img.width

    layer = layer.resize((int(layer.width * 1.5), int(layer.height * 1.5)), Image.BICUBIC)
    frame.paste(layer, (0, 0), layer)

# ---------- 确定文字排版字体（版本2 保留） ---------- #
def determine_font(full_text, max_fs=80, min_fs=32):
    draw = _measure_draw()
    font = None
    lines = None

    if not font_message_path.exists():
        f = ImageFont.load_default()
        asc, dsc = f.getmetrics()
        return f, asc + dsc, int(20 * 0.45), wrap_text(full_text, draw, f)

    for fs in range(max_fs, min_fs - 1, -1):
        f = ImageFont.truetype(str(font_message_path), fs)
        asc, dsc = f.getmetrics()
        lh = asc + dsc

        test = wrap_text(full_text, draw, f)
        if len(test) * lh + (len(test) - 1) * int(fs * 0.45) <= text_area_height - 10:
            return f, lh, int(fs * 0.45), test

    # 最小字号兜底
    f = ImageFont.truetype(str(font_message_path), min_fs)
    asc, dsc = f.getmetrics()
    return f, asc + dsc, int(min_fs * 0.45), wrap_text(full_text, draw, f)

# ---------- 文本绘制 ---------- #
def draw_message(frame, text, font, lh, ls, max_lines):
    layer = Image.new("RGBA", (text_area_width, text_area_height))
    d = ImageDraw.Draw(layer)

    # wrap
    lines, ln = [], ""
    for ch in text:
        if char_width(d, ln + ch, font) > usable_width:
            lines.append(ln)
            ln = ch
        else:
            ln += ch
    if ln:
        lines.append(ln)

    if len(lines) > max_lines:
        lines = lines[-max_lines:]

    y = 0
    for line in lines:
        x = 0
        for ch in line:
            bbox = d.textbbox((0, 0), ch, font=font)
            d.text((x, y), ch, font=font, fill="white")
            x += (bbox[2] - bbox[0]) + char_spacing
        y += lh + ls

    frame.paste(layer, (text_area_left, text_area_top), layer)

# ---------- 主函数 ---------- #
def mo_shen(images, texts, args):
    text = texts[0] if texts else "啥啊"
    is_typing = text.startswith("逐字")
    if is_typing:
        text = text[2:].strip()

    # 随机背景
    base = Image.open(random.choice(list((img_dir / "background").glob("*")))).convert("RGBA")
    w, h = base.size

    # 随机角色
    folder = random.choice(list(CHAR_TEXTS.keys()))
    char_text, first_color = CHAR_TEXTS[folder]
    icon = Image.open(random.choice(list((img_dir / folder).glob("*")))).convert("RGBA")
    icon_w, icon_h = icon.size

    # 文字排版参数
    font, lh, ls, full_lines = determine_font(text)
    max_lines = len(full_lines)

    # 静态图
    if not is_typing:
        frame = base.copy()
        frame.paste(icon, (0, h - icon_h), icon)
        draw_message(frame, text, font, lh, ls, max_lines)
        draw_character_name(frame, char_text, folder, first_color)
        return BuildImage(frame).save_jpg()

    # 逐字动画：先合成静态部分
    bg = base.copy()
    bg.paste(icon, (0, h - icon_h), icon)
    draw_character_name(bg, char_text, folder, first_color)

    frames = []
    for i in range(1, len(text) + 1):
        f = bg.copy()
        draw_message(f, text[:i], font, lh, ls, max_lines)
        frames.append(f)

    # 尾帧停顿
    frames.extend([frames[-1]] * 12 if frames else [bg])
    return save_gif(frames, duration=typing_speed / 1000)

# ---------- 注册 ---------- #
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
