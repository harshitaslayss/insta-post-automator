import os
import requests
from generator import generate_next

REPO_RAW = "https://raw.githubusercontent.com/harshitaslayss/insta-post-automator/main/"


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

    image_url = REPO_RAW + img
    print("Posting image URL:", image_url)

    create = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": PAGE_TOKEN
        }
    ).json()

    print("CREATE RESPONSE:", create)

    if "id" not in create:
        raise Exception("❌ Instagram media creation failed")

    publish = requests.post(
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish",
        data={
            "creation_id": create["id"],
            "access_token": PAGE_TOKEN
        }
    ).json()

    print("PUBLISH RESPONSE:", publish)

    if "id" not in publish:
        raise Exception("❌ Instagram publish failed")

    print("✅ ACTUALLY POSTED TO INSTAGRAM")


def main():
    slide, art = generate_next()
    if not slide:
        print("No post")
        return

    git_commit([slide])

    import requests, time

    for _ in range(3):
        r = requests.get(REPO_RAW + slide)
        if r.status_code == 200:
            break
        time.sleep(5)
    # wait for GitHub raw CDN

    caption = f"{art['title']}\n\nSource: {art['source']}"
    post_instagram(slide, caption)


if __name__ == "__main__":
    main()
