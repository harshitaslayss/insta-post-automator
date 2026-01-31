# poster.py
import os
import time
import requests
from generator import generate_carousel

PAGE_TOKEN = os.getenv("PAGE_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

def upload_image(image_url):
    r = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media",
        data={
            "image_url": image_url,
            "is_carousel_item": "true",
            "access_token": PAGE_TOKEN,
        },
    ).json()
    return r.get("id")

def publish_carousel(children):
    create = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media",
        data={
            "media_type": "CAROUSEL",
            "children": ",".join(children),
            "caption": "📰 Tech update • Auto-generated",
            "access_token": PAGE_TOKEN,
        },
    ).json()

    time.sleep(10)  # IMPORTANT: wait for processing

    publish = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish",
        data={
            "creation_id": create["id"],
            "access_token": PAGE_TOKEN,
        },
    ).json()

    print("PUBLISHED:", publish)

# ----------------- MAIN -----------------
slides = generate_carousel()
children = []

for slide in slides:
    raw_url = (
        "https://raw.githubusercontent.com/"
        "harshitaslayss/insta-post-automator/main/" + slide
    )
    cid = upload_image(raw_url)
    children.append(cid)
    time.sleep(5)

publish_carousel(children)
