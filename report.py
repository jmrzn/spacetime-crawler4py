import json
from urllib.parse import urldefrag
from scraper import URL_MAP

def generate_report():
    unique_pages = get_unique_pages()
    print(f"Unique pages: {unique_pages}\n")

def get_unique_pages():
    unique_pages = set()

    # Open jsonl file and extract URLs
    # Defragment URLs and append to set of unique pages
    with open(URL_MAP, "r") as f:
        for line in f:
            url = json.loads(line)["url"]
            unique_pages.add(urldefrag(url)[0])

    # Return number of unique pages
    return len(unique_pages)

if __name__ == "__main__":
    generate_report()
