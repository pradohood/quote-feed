import requests
import os

# Ensure you have DOT_API_KEY and DOT_DEVICE_ID set in your env
headers = {"Authorization": f"Bearer {os.environ.get('DOT_API_KEY')}"}
device_id = os.environ.get('DOT_DEVICE_ID')

url = f"https://dot.mindreset.tech/api/authV2/open/device/{device_id}/loop/list"

print("Fetching device mapping...")
res = requests.get(url, headers=headers)
data = res.json()

if data.get("code") == 200:
    tasks = data.get("result", [])
    print(f"\nFound {len(tasks)} items in your loop:")
    for task in tasks:
        # 'key' is what we need for your Python scripts
        # 'title' or 'alias' helps you identify which is which
        print(f"---")
        print(f"Task Key: {task.get('key')}")
        print(f"Type: {task.get('type')}")
        print(f"Current Title: {task.get('title')}")
else:
    print(f"Error: {data}")
