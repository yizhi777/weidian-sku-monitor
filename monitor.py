import requests
import json
import os
from datetime import datetime

URL = "https://shop1211059689.v.weidian.com/item.html?itemID=7657995364"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}

DATA_DIR = "data"
LAST_FILE = f"{DATA_DIR}/last.json"
CHANGE_FILE = f"{DATA_DIR}/changes.csv"

os.makedirs(DATA_DIR, exist_ok=True)

def fetch_sku():
    resp = requests.get(URL, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    text = resp.text
    start = text.find("window.rawData=")
    end = text.find(";</script>", start)

    raw = text[start + 15:end]
    data = json.loads(raw)

    skus = data["item"]["sku"]
    result = {}

    for sku_id, sku in skus.items():
        result[sku_id] = {
            "title": sku["title"],
            "stock": sku["stock"]
        }

    return result

def load_last():
    if not os.path.exists(LAST_FILE):
        return {}
    with open(LAST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_last(data):
    with open(LAST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def record_change(changes):
    header = not os.path.exists(CHANGE_FILE)
    with open(CHANGE_FILE, "a", encoding="utf-8") as f:
        if header:
            f.write("time,sku_id,title,old_stock,new_stock,delta\n")
        for c in changes:
            f.write(",".join(map(str, c)) + "\n")

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    current = fetch_sku()
    last = load_last()

    changes = []

    for sku_id, info in current.items():
        old = last.get(sku_id, {}).get("stock")
        new = info["stock"]

        if old is not None and old != new:
            changes.append([
                now,
                sku_id,
                info["title"],
                old,
                new,
                new - old
            ])

    if changes:
        record_change(changes)

    save_last(current)

if __name__ == "__main__":
    main()
