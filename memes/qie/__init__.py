from datetime import datetime
from pathlib import Path
from pil_utils import BuildImage
from meme_generator import add_meme
from meme_generator.exception import TextOverLength

img_dir = Path(__file__).parent / "images"

def qie(images, texts: list[str], args):
    text = texts[0] if texts else "真男人只干男人"
    frame = BuildImage.open(img_dir / "0.jpg")
    box = (183, 303, 510, 495)
    try:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            frame.draw_text(
                (box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy),
                text,
                fill=(255, 0, 0), 
                allow_wrap=True,
                max_fontsize=60,
                min_fontsize=25,
                lines_align="center",
            )
    except ValueError:
        raise TextOverLength(text)
    return frame.save_jpg()


add_meme(
    "qie",
    qie,
    min_texts=0,
    max_texts=1,
    default_texts=["真男人只干男人"],
    keywords=["企鹅举牌"],
    date_created=datetime(2025, 11, 6),
    date_modified=datetime(2025, 11, 6),
)
