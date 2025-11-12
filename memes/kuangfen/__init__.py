from datetime import datetime
from pathlib import Path
import random
from PIL import Image
from pil_utils import BuildImage
from meme_generator import add_meme
from meme_generator.exception import TextOverLength

img_dir = Path(__file__).parent / "images"

def gengduokuangfen(images, texts: list[str], args):
    text = texts[0] if texts else random.choice(["省略", "小谈"])

    idx = random.randint(0, 7)
    bg_path = img_dir / f"{idx}.jpg"

    base = Image.open(bg_path).convert("RGBA")
    w, h = base.size  

    # 调整区域
    box_w, box_h = 320, 165
    box_top = 20
    box_center_x = 250
    box_left = int(box_center_x - box_w / 2)

    # 文字层
    txt_layer = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    build_txt = BuildImage(txt_layer)

    try:
        build_txt.draw_text(
            (0, 0, box_w, box_h),
            text,
            fill=(255, 0, 0),
            stroke_fill=(150, 0, 0),
            stroke_ratio=0.08,
            allow_wrap=True,
            max_fontsize=80,   
            min_fontsize=20,   
            lines_align="center",
        )
    except ValueError:
        raise TextOverLength(text)

    # 倾斜（右下）
    rotated = txt_layer.rotate(-6, expand=True)

    # 位置
    box_center = (box_left + box_w // 2, box_top + box_h // 2)
    rx, ry = rotated.size
    paste_x = int(box_center[0] - rx / 2)
    paste_y = int(box_center[1] - ry / 2)

    composed = base.copy()
    composed.paste(rotated, (paste_x, paste_y), rotated)

    return BuildImage(composed).save_jpg()


add_meme(
    "gengduokuangfen",
    gengduokuangfen,
    min_texts=0,
    max_texts=1,
    default_texts=["省略","小谈"],
    keywords=["更多狂粉", "随机狂粉", "gengduokuangfen"],
    date_created=datetime(2025, 11, 7),
    date_modified=datetime(2025, 11, 7),
)
