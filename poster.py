import os
import requests
from generator import generate_next

REPO_RAW = "https://raw.githubusercontent.com/harshitaslayss/insta-bot/main/"

def git_commit(files):
    os.system('git config --global user.email "bot@github.com"')
    os.system('git config --global user.name "ig-bot"')
    for f in files + ["queue_db.json"]:
        os.system(f"git add {f}")
    os.system('git commit -m "auto post" || echo "no changes"')
    os.system("git push")

def post_instagram(img, caption):
    PAGE_TOKEN = os.environ["PAGE_TOKEN"]
    IG_USER_ID = os.environ["IG_USER_ID"]

    create = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media",
        data={
            "image_url": REPO_RAW + img,
            "caption": caption,
            "access_token": PAGE_TOKEN
        }
    ).json()

    if "id" not in create:
        print("Create failed", create)
        return

    publish = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish",
        data={
            "creation_id": create["id"],
            "access_token": PAGE_TOKEN
        }
    ).json()

    print("Published:", publish)

def main():
    slide, art = generate_next()
    if not slide:
        print("No post")
        return

    git_commit([slide])
    caption = f"{art['title']}\n\nSource: {art['source']}"
    post_instagram(slide, caption)

if __name__ == "__main__":
    main()
