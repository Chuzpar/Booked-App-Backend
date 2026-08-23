import requests
import time

BACKEND_URL = "http://127.0.0.1:5000/api/books"
OPEN_LIBRARY_SEARCH = "https://openlibrary.org/search.json"


def fetch_book_info(title, author):
    """Search Open Library for a cover image and description."""
    params = {"title": title, "author": author, "limit": 1}
    response = requests.get(OPEN_LIBRARY_SEARCH, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if not data.get("docs"):
        return None, None

    doc = data["docs"][0]
    cover_id = doc.get("cover_i")
    cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else None

    # description often lives on the "work" record, fetch it separately
    synopsis = None
    key = doc.get("key")  # e.g. "/works/OL27448W"
    if key:
        work_resp = requests.get(f"https://openlibrary.org{key}.json", timeout=10)
        if work_resp.ok:
            work_data = work_resp.json()
            desc = work_data.get("description")
            if isinstance(desc, dict):
                synopsis = desc.get("value")
            elif isinstance(desc, str):
                synopsis = desc

    return cover_url, synopsis


def main():
    books = requests.get(BACKEND_URL).json()["books"]
    print(f"Found {len(books)} books to enrich.")

    for book in books:
        title, author, book_id = book["title"], book["author"], book["id"]
        print(f"Looking up: {title} by {author}...")

        try:
            cover_url, synopsis = fetch_book_info(title, author)
        except Exception as e:
            print(f"  Failed to fetch info: {e}")
            continue

        if not cover_url and not synopsis:
            print("  No data found, skipping.")
            continue

        update_payload = {}
        if cover_url:
            update_payload["cover_image_url"] = cover_url
        if synopsis:
            update_payload["synopsis"] = synopsis[:500]  # keep it reasonably short

        put_resp = requests.put(f"{BACKEND_URL}/{book_id}", json=update_payload)
        if put_resp.ok:
            print(f"  Updated with cover={bool(cover_url)}, synopsis={bool(synopsis)}")
        else:
            print(f"  Update failed: {put_resp.status_code} {put_resp.text}")

        time.sleep(1)  # be polite to Open Library's free API


if __name__ == "__main__":
    main()