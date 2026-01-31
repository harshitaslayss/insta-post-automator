from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import time

WIDTH, HEIGHT = 1080, 1080

def get_font(size):
    try:
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            size
        )
    except:
        return ImageFont.load_default()

def generate_slide(article, topic):
    img = Image.new("RGB", (WIDTH, HEIGHT), (18, 18, 18))
    draw = ImageDraw.Draw(img)

    title_font = get_font(64)
    topic_font = get_font(36)

    draw.text((60, 300), topic.upper(), fill="#FFD700", font=topic_font)
    draw.text((60, 380), article["title"], fill="white", font=title_font)

    filename = f"slide_{int(time.time())}.jpg"
    img.save(
        filename,
        "JPEG",
        quality=95,
        subsampling=0,
        optimize=True
    )
    return filename

def generate_next():
    article = {
        "title": "TEST POST — GitHub Actions",
        "source": "Automation Test"
    }

    slide = generate_slide(article, "TEST")
    return slide, article
