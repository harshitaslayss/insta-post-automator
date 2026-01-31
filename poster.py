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


def publish_with_retry(creation_id, retries=6, delay=5):
    for i in range(retries):
        publish = requests.post(
            f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish",
            data={
                "creation_id": creation_id,
                "access_token": PAGE_TOKEN
            }
        ).json()

        if "id" in publish:
            print("✅ PUBLISHED:", publish)
            return

        print(f"⏳ Media not ready, retry {i+1}/{retries}")
        time.sleep(delay)

    raise Exception("❌ Media never became ready")


def post_instagram(image_file, caption):
    image_url = REPO_RAW + image_file
    print("📤 Posting:", image_url)

    create = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": PAGE_TOKEN
        }
    ).json()

    print("CREATE:", create)

    if "id" not in create:
        raise Exception(f"❌ Create failed: {create}")

    time.sleep(8)  # IMPORTANT wait before publish
    publish_with_retry(create["id"])


def main():
    slide, article = generate_next()

    if not slide:
        print("😴 No post to publish")
        return

    # commit image + db
    git_commit([slide])

    # wait for GitHub raw CDN
    time.sleep(12)

    caption = f"{article['title']}\n\nSource: {article['source']}"
    post_instagram(slide, caption)


if __name__ == "__main__":
    main()
