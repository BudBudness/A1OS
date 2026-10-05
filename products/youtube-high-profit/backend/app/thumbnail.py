from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def make_thumbnail(text: str, output: str):
    path=Path(output); path.parent.mkdir(parents=True,exist_ok=True)
    img=Image.new("RGB",(1280,720),(18,18,18))
    draw=ImageDraw.Draw(img)
    font=ImageFont.load_default(size=64)
    draw.text((70,280),text[:48],font=font,fill=(255,255,255),stroke_width=2,stroke_fill=(0,0,0))
    img.save(path,"PNG")
    return str(path)
