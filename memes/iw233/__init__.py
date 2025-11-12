from datetime import datetime
import io
import requests
from pil_utils import BuildImage
from meme_generator import add_meme


def iw233(images, texts, args):
    
    url = "https://t.alcy.cc/xhl"
#    url = "https://t.alcy.cc/moez"
#    print("正在获取随机动漫图片...")
    res = requests.get(url)
    res.raise_for_status()

    img_bytes = io.BytesIO(res.content)
    frame = BuildImage.open(img_bytes)
    print("图片获取完成！")

    return frame.save_jpg()


add_meme(
    "iw233",
    iw233,
    keywords=["随机狐狸", "iw233"],
    date_created=datetime(2025, 11, 6),
    date_modified=datetime(2025, 11, 6),
)
