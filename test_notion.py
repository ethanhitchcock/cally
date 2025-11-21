import os
import json
import requests
from dotenv import load_dotenv
from cally.loaders_live import NotionTaskLoader

# 1. Load Environment Variables
load_dotenv()

TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

print(f"DEBUG: Token loaded: {'Yes' if TOKEN else 'No'}")
print(f"DEBUG: Database ID loaded: {'Yes' if DATABASE_ID else 'No'}")

if not TOKEN or not DATABASE_ID:
    print("\nERROR: Missing environment variables.")
    print("Please ensure .env file exists and contains NOTION_TOKEN and NOTION_DATABASE_ID")
    exit(1)

# 2. Test Raw API Connection (Verbose Debugging)
print("\n--- Testing Raw Notion API ---")
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

try:
    response = requests.post(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    data = response.json()
    # Print first result structure to help with property mapping
    if "results" in data and data["results"]:
        print("\nSuccessfully connected! Found", len(data["results"]), "items.")
        print("\nStructure of first item (use this to debug property names in loaders_live.py):")
        print(json.dumps(data["results"][0]["properties"], indent=2))
    elif "results" in data:
        print("\nConnected, but database is empty.")
    else:
        print("\nAPI Error Response:")
        print(json.dumps(data, indent=2))

except Exception as e:
    print(f"Connection failed: {e}")

# 3. Test Loader Class Integration
print("\n--- Testing NotionTaskLoader Integration ---")
class MockConfig:
    pass

try:
    loader = NotionTaskLoader(MockConfig())
    tasks = loader.load()
    print(f"Loader returned {len(tasks)} tasks.")
    for t in tasks:
        print(f"- [ID: {t.item_id}] {t.name} (Status: {t.status})")
except Exception as e:
    print(f"Loader failed: {e}")

