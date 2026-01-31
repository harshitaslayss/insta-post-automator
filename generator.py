from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import spacy
from collections import Counter
import json
from datetime import datetime, timedelta
import os
import time

# ---------- CONFIG ----------
DB_FILE = "queue_db.json"
QUERY = "technology india"
WIDTH, HEIGHT = 1080, 1080

newsapi_key = os.getenv("NEWSAPI_KEY")
gnews_key = os.getenv("GNEWS_KEY")
mstack_key = os.getenv("MEDIASTACK_KEY")

nlp = spacy.load("en_core_web_sm")

# ---------- DB ----------
def load_db():
    if not os.path.exists(DB_FILE):
        return {"queue": [], "posted": [], "recent_topics": {}}
    return json.load(open(DB_FILE))

def save_db(db):
    json.dump(db, open(DB_FILE, "w"), indent=2)

# ---------- NEWS ----------
def score_article(a):
    score = 0
    if a.get("image"): score += 2
    if len(a.get("desc", "")) > 120: score += 1
    if any(w in a["title"].lower() for w in ["breaking","launch","wins"]): score += 2
    return score

def fetch_news():
    arts, seen = [], set()

    urls = [
        f"https://newsapi.org/v2/top-headlines?q={QUERY}&apiKey={newsapi_key}",
        f"https://gnews.io/api/v4/top-headlines?q={QUERY}&token={gnews_key}&lang=en",
        f"http://api.mediastack.com/v1/news?access_key={mstack_key}&keywords={QUERY}"
    ]

    for url in urls:
        try:
            data = requests.get(url, timeout=10).json()
            for a in data.get("articles", []) + data.get("data", []):
                u = a.get("url")
                if not u or u in seen: continue
                seen.add(u)
                arts.append({
                    "title": a.get("title",""),
                    "desc": a.get("description",""),
                    "url": u,
                    "image": a.get("image") or a.get("urlToImage"),
                    "source": (a.get("source") or {}).get("name","News")
                })
        except:
            pass
    return arts

# ---------- TREND ----------
def detect_trends(articles):
    counter, bucket = Counter(), {}
    for a in articles:
        doc = nlp(f"{a['title']} {a['desc']}")
        ents = {e.text.title() for e in doc.ents if e.label_ in ["ORG","PERSON","GPE"]}
        for e in ents:
            counter[e] += 1
            bucket.setdefault(e, []).append(a)

    trends = []
    for t,_ in counter.most_common(3):
        best = max(bucket[t], key=score_article)
        trends.append((t, best))
    return trends

# ---------- IMAGE ----------
def get_font(size):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except:
        return ImageFont.load_default()

def generate_slide(article, topic):
    img = Image.new("RGB",(WIDTH,HEIGHT),(18,18,18))
    d = ImageDraw.Draw(img)
    font_t = get_font(60)
    font_b = get_font(36)

    d.text((60,300), topic.upper(), fill="#FFD700", font=font_b)
    d.text((60,380), article["title"], fill="white", font=font_t)

    name = f"slide_{int(time.time())}.jpg"
    img = img.convert("RGB")  # safety
    img.save(
        name,
        "JPEG",
        quality=95,
        subsampling=0,
        optimize=True
    )
    return name


# ---------- MAIN ----------
def generate_next():
    db = load_db()
    news = fetch_news()
    trends = detect_trends(news)

    for topic, art in trends:
        # if topic in db["recent_topics"]:
        #     last = datetime.fromisoformat(db["recent_topics"][topic])
        #     if datetime.now() - last < timedelta(hours=6):
        #         continue

        slide = generate_slide(art, topic)
        db["recent_topics"][topic] = datetime.now().isoformat()
        save_db(db)
        return slide, art

    save_db(db)
    return None, None
