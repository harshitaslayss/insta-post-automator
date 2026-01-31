import os
import time
import requests
from generator import generate_next

REPO_RAW = "https://raw.githubusercontent.com/harshitaslayss/insta-post-automator/main/"

PAGE_TOKEN = os.environ["PAGE_TOKEN"]
IG_USER_ID = os.environ["IG_USER_ID"]


def git_commit(files):
    os.system('git config --global user.email "bot@github.com"')
    os.system('git config --global user.name "ig-bot"')

    for f in files + ["queue_db.json"]:
        os.system(f"git add {f}")

    os.system('git commit -m "auto post" || echo "no changes"')
    os.system("git push")


def publish_with_retry(creation_id, max_tries=10, wait=6):
    """
    Instagram media is ASYNC.
    This WILL retry until IG is ready.
    """
    for attempt in range(1, max_tries + 1):
        time.sleep(wait)

        res = requests.post(
            f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish",
            data={
                "creation_id": creation_id,
                "access_token": PAGE_TOKEN
            }
        ).json()

        print(f"📡 Publish attempt {attempt}:", res)

        if "id" in res:
            print("✅ INSTAGRAM POST LIVE")
            return

    raise Exception("❌ Media never became ready after retries")


def post_instagram(image_file, caption):
    image_url = REPO_RAW + image_file
    print("📤 IMAGE URL:", image_url)

    create = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": PAGE_TOKEN
        }
    ).json()

    print("🧱 CREATE RESPONSE:", create)

    if "id" not in create:
        raise Exception(f"❌ Create failed: {create}")

    # VERY IMPORTANT:
    # GitHub raw + IG processing delay
    print("⏳ Waiting before publish...")
    time.sleep(20)

    publish_with_retry(create["id"])


def main():
    slide, article = generate_next()

    if not slide:
        print("😴 Nothing to post")
        return

    print("🖼 Generated:", slide)

    git_commit([slide])

    # Give GitHub raw CDN time
    print("⏳ Waiting for GitHub CDN...")
    time.sleep(20)

    caption = f"{article['title']}\n\nSource: {article['source']}"
    post_instagram(slide, caption)


if __name__ == "__main__":
    main()
