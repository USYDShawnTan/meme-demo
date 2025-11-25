from datetime import datetime
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFont
from pil_utils import BuildImage
from meme_generator import add_meme
from meme_generator.exception import TextOverLength
from meme_generator.utils import save_gif

plugin_dir = Path(__file__).parent
img_dir = plugin_dir / "images"


font_name = None       # 角色名
font_message = None    # 消息

def load_fonts():
    global font_name, font_message
    if font_name is None:
        path = plugin_dir / "fonts" / "font2.ttf"
        if path.exists():
            font_name = ImageFont.truetype(str(path), 160)
    if font_message is None:
        path = plugin_dir / "fonts" / "font3.ttf"
        if path.exists():
            font_message = ImageFont.truetype(str(path), 60)


CHAR_TEXTS = {
    'alisa': ("紫藤亚里沙", "#EA4A3A"),
    'anan': ("夏目安安", "#A897FF"),
    'coco': ("泽渡可可", "#F7714C"),
    'ema': ("樱羽艾玛", "#FF8DB3"),
    'hanna': ("远野汉娜", "#ACC81E"),
    'hiro': ("二阶堂希罗", "#EC4348"),
    'mago': ("宝生玛格", "#A36FD4"),
    'meruru': ("冰上梅露露", "#E3B4AA"),
    'miria': ("佐伯米莉亚", "#EDCB84"),
    'nanoka': ("黑部奈叶香", "#858E93"),
    'noa': ("城崎诺亚", "#66E2EC"),
    'reia': ("莲见蕾雅", "#FFB269"),
    'sherri': ("橘雪莉", "#7CABFF"),
    'yuki': ("月代雪", "#C3D5E9"),
}

def mo_shen(images, texts: list[str], args):
    load_fonts()
    text = texts[0] if texts else "啥啊"

    is_typing = False
    if text.startswith("逐字"):
        is_typing = True
        text = text[2:].strip()

    #背景
    bg_folder = img_dir / "background"
    bg_path = random.choice(list(bg_folder.glob("*")))
    base = Image.open(bg_path).convert("RGBA")
    w, h = base.size

    #角色
    folder_name = random.choice(list(CHAR_TEXTS.keys()))
    choice_folder = img_dir / folder_name
    icon_path = random.choice(list(choice_folder.glob("*")))
    icon = Image.open(icon_path).convert("RGBA")
    icon_w, icon_h = icon.size

    #文本区域
    raw_width, raw_height = 1858, 523
    padding = 55
    text_width = raw_width - padding * 2
    text_height = raw_height - padding * 2
    text_area_left = icon_w + padding
    text_area_top = h - raw_height

    char_text, first_color = CHAR_TEXTS[folder_name]
    ratio = 0.75 if folder_name == "sherri" else 0.5
    extra_shrink = 0.25 if folder_name == "sherri" else 0

    target_center_x, target_center_y = 855-285, 215-75  # 调整偏移

    def draw_character_name(frame, text_slice=None):
        text_slice = text_slice or char_text
        draw_layer = Image.new("RGBA", frame.size, (0,0,0,0))
        draw = ImageDraw.Draw(draw_layer)

        char_imgs = []
        heights = []

        for idx, ch in enumerate(text_slice):
            if idx == 0:
                fs = 110
                color = first_color
            elif idx == 2 and folder_name != "sherri":
                fs = 110
                color = "white"
            elif idx == 2 and folder_name == "sherri":
                fs = int(110 * ratio * (1 - extra_shrink*2)) 
                color = "white"
            else:
                fs = int(110 * ratio)
                color = "white"
            font = ImageFont.truetype(str(plugin_dir / "fonts" / "font1.ttf"), fs)

            bbox = draw.textbbox((0,0), ch, font=font)
            char_img = Image.new("RGBA", (bbox[2]-bbox[0], bbox[3]-bbox[1]), (0,0,0,0))
            draw_tmp = ImageDraw.Draw(char_img)
            draw_tmp.text((-bbox[0], -bbox[1]), ch, font=font, fill=color)
            char_imgs.append(char_img)
            heights.append(char_img.height)

        max_height = max(heights)
        x = target_center_x - char_imgs[0].width // 2
        y = target_center_y - max_height // 2
        for idx, img in enumerate(char_imgs):
            dy = max_height - img.height if idx !=0 and (idx !=2 or folder_name=="sherri") else 0
            draw_layer.paste(img, (x, y + dy), img)
            x += img.width

        draw_layer = draw_layer.resize((int(draw_layer.width*1.5), int(draw_layer.height*1.5)), Image.BICUBIC)
        frame.paste(draw_layer, (0,0), draw_layer)

    #消息文本（动态行距）
    def draw_message_text(frame, message_text):
        txt_layer = Image.new("RGBA", (text_width, text_height), (0,0,0,0))
        draw = ImageDraw.Draw(txt_layer)
        max_fontsize = 100
        font = ImageFont.truetype(str(plugin_dir / "fonts" / "font3.ttf"), max_fontsize)

        #换行
        lines=[]
        line=""
        for ch in message_text:
            line_candidate = line + ch
            bbox = draw.textbbox((0,0), line_candidate, font=font)
            w = bbox[2]-bbox[0]
            if w>text_width:
                lines.append(line)
                line=ch
                if len(lines)>=3:
                    break
            else:
                line=line_candidate
        if line and len(lines)<3:
            lines.append(line)

        #行距计算
        bbox_sample = draw.textbbox((0,0), "我", font=font)
        line_height = bbox_sample[3]-bbox_sample[1]
        if len(lines)>1:
            line_spacing = int((text_height - line_height*len(lines)) / (len(lines)-1) * 0.85)  # 85%缩小
        else:
            line_spacing = 0

        #绘制
        y=0
        for l in lines:
            draw.text((0,y), l, font=font, fill="white")
            y += line_height + line_spacing

        frame.paste(txt_layer, (text_area_left, text_area_top), txt_layer)

    #静态
    if not is_typing:
        frame = base.copy()
        frame.paste(icon, (0,h-icon_h), icon)
        draw_message_text(frame, text)
        draw_character_name(frame)
        return BuildImage(frame).save_jpg()

    #逐字
    frames=[]
    typing_speed = 75
    for i in range(1,len(text)+1):
        frame = base.copy()
        frame.paste(icon, (0,h-icon_h), icon)
        draw_message_text(frame, text[:i])
        draw_character_name(frame, char_text) 
        frames.append(frame)

    for _ in range(12):
        frames.append(frames[-1])

    return save_gif(frames, duration=typing_speed/1000)


add_meme(
    "moshen",
    mo_shen,
    min_texts=0,
    max_texts=1,
    default_texts=["啥啊"],
    keywords=["魔审","moshen"],
    date_created=datetime(2025,11,25),
    date_modified=datetime(2025,11,25),
)
