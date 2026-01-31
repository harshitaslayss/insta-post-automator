# generator.py
import os
import json
import time
import requests
import spacy
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sklearn.feature_extraction.text import TfidfVectorizer

WIDTH, HEIGHT = 1080, 1080
QUERY = "technology india"

NEWS_API_KEY = os.getenv("NEWSAPI_KEY")

nlp = spacy.load("en_core_web_sm")

# ----------------- FONT -----------------
def font(size):
    try:
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size
        )
    except:
        return ImageFont.load_default()

# ----------------- FETCH NEWS -----------------
def fetch_news():
    url = f"https://newsapi.org/v2/everything?q={QUERY}&language=en&apiKey={NEWS_API_KEY}"
    data = requests.get(url, timeout=10).json()
    return [
        {
            "title": a["title"],
            "desc": a["description"] or "",
            "content": a["content"] or "",
            "source": a["source"]["name"],
        }
        for a in data.get("articles", [])[:15]
    ]

# ----------------- TF-IDF -----------------
def select_best_article(articles):
    corpus = [
        f"{a['title']} {a['desc']} {a['content']}" for a in articles
    ]
    tfidf = TfidfVectorizer(stop_words="english")
    scores = tfidf.fit_transform(corpus).toarray().sum(axis=1)
    return articles[int(np.argmax(scores))]

# ----------------- SLIDE MAKER -----------------
def make_slide(text_lines, highlight=None):
    img = Image.new("RGB", (WIDTH, HEIGHT), (15, 15, 15))
    d = ImageDraw.Draw(img)

    y = 260
    if highlight:
        d.text((80, y - 80), highlight.upper(), fill="#FFD700", font=font(42))

    for line in text_lines:
        d.text((80, y), line, fill="white", font=font(64))
        y += 90

    name = f"slide_{int(time.time()*1000)}.jpg"
    img.save(name, "JPEG", quality=95)
    return name

# ----------------- MAIN -----------------
def generate_carousel():
    news = fetch_news()
    article = select_best_article(news)

    # Slide 1 – Headline
    s1 = make_slide(
        [article["title"][:60] + "..."],
        highlight="Trending Tech",
    )

    # Slide 2 – Summary
    summary = article["desc"] or article["content"]
    bullets = summary.split(".")[:3]
    s2 = make_slide([f"• {b.strip()}" for b in bullets if b.strip()])

    # Slide 3 – Source
    s3 = make_slide(
        [article["source"]],
        highlight="Source",
    )

    return [s1, s2, s3]
