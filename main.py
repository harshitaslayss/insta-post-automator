import os
import requests
import sys

PAGE_TOKEN = os.environ["PAGE_TOKEN"]
IG_USER_ID = os.environ["IG_USER_ID"]

IMAGE_URL = "https://raw.githubusercontent.com/harshitaslayss/test-images/main/Your%20paragraph%20text%20(1).png"
CAPTION = "Render test post"

# STEP 1: create media
create = requests.post(
    f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media",
    data={
        "image_url": IMAGE_URL,
        "caption": CAPTION,
        "access_token": PAGE_TOKEN
    }
).json()

print("CREATE:", create)

if "id" not in create:
    print("Media creation failed")
    print(create)
    sys.exit(1)

# STEP 2: publish
publish = requests.post(
    f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish",
    data={
        "creation_id": create["id"],
        "access_token": PAGE_TOKEN
    }
).json()

print("PUBLISH:", publish)
print("POSTING SUCCESS")


