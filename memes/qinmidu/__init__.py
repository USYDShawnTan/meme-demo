from datetime import datetime
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from pil_utils import BuildImage, Text2Image
from meme_generator import MemeArgsModel, MemeArgsType, ParserOption, add_meme
import random, re, io


class Model(MemeArgsModel):
    """占位"""
    pass


args_type = MemeArgsType(
    args_model=Model,
    parser_options=[
        ParserOption(names=["--上升"], args=[], help_text="甜蜜粉"),
        ParserOption(names=["--下降"], args=[], help_text="伤心蓝"),
        ParserOption(names=["无", "默认"], args=[], help_text="随机"),
    ],
)


def qinmidu(images, texts: list[str], args: Model):
    text = texts[0] if texts else "亲密度"
    text = str(text).strip()
    text = re.sub(r"^(上升){2,}", "上升", text)
    text = re.sub(r"^(下降){2,}", "下降", text)

    if text.startswith("上升"):
        text = text.replace("上升", "", 1).strip()
        arrow = "↑"
    elif text.startswith("下降"):
        text = text.replace("下降", "", 1).strip()
        arrow = "↓"
    else:
        arrow = random.choice(["↑", "↓"])

    text = (text + " " + arrow) if text else ("亲密度 " + arrow)
    is_up = arrow == "↑"

    font_size = 200
    padding = 120
    inner_fill = (255, 255, 255)
    inner_stroke_width = int(6 * 1.5 * 1.5)
    outline_thickness = 40

    if is_up:
        inner_stroke_color = (220, 50, 120)
        outline_color = (255, 216, 240, 255)
    else:
        inner_stroke_color = (50, 80, 140)
        outline_color = (156, 195, 252, 255)

    # 直接用 Text2Image（像 5000choyen）
    t2i = Text2Image.from_text(
        text,
        font_size,
        font_families=["Noto Sans SC", "Source Han Sans SC", "Arial Unicode MS"],
        fill=inner_fill,
        stroke_width=inner_stroke_width,
        stroke_fill=inner_stroke_color,
    )
    text_img = t2i.to_image(padding=(padding, padding))
    text_mask = text_img.getchannel("A")

    edge_mask = text_mask.filter(ImageFilter.MaxFilter(outline_thickness * 2 + 1))
    edge_mask = edge_mask.filter(ImageFilter.GaussianBlur(radius=max(4, outline_thickness // 2)))
    outline_layer = Image.new("RGBA", text_img.size, outline_color)
    outline_layer.putalpha(edge_mask)

    result = Image.new("RGBA", text_img.size, (255, 255, 255, 255))
    result = Image.alpha_composite(result, outline_layer)
    result = Image.alpha_composite(result, text_img)

    # 像素化 + 模糊 + 色彩减淡
    downscale_factor = 0.15
    w, h = result.size
    small = result.resize((int(w * downscale_factor), int(h * downscale_factor)), Image.BILINEAR)
    pixelated = small.resize((w, h), Image.NEAREST)

    buf = io.BytesIO()
    pixelated.convert("RGB").save(buf, format="JPEG", quality=50)
    buf.seek(0)
    final_img = Image.open(buf)

    final_img = final_img.filter(ImageFilter.GaussianBlur(radius=2.0))
    final_img = ImageEnhance.Color(final_img).enhance(0.97)

    return BuildImage(final_img).save_jpg()


add_meme(
    "qinmidu",
    qinmidu,
    min_texts=0,
    max_texts=1,
    args_type=args_type,
    keywords=["亲密度"],
    date_created=datetime(2025, 11, 4),
    date_modified=datetime(2025, 11, 4),
)
