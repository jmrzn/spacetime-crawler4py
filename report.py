import json
from urllib.parse import urlparse, urldefrag
from scraper import URL_MAP

def generate_report():
    unique_pages = get_unique_pages()
    print(f"Unique pages: {unique_pages}\n")

    subdomains = get_subdomains()
    print("Subdomains:")
    for subdomain, count in subdomains:
        print(f"{subdomain}, {count}")

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

def get_subdomains():
    subdomains = {}

    # Open jsonl file and extract URLs
    # Defragment and parse URLs
    with open(URL_MAP, "r") as f:
        for line in f:
            url = json.loads(line)["url"]
            parsed = urlparse(urldefrag(url)[0])
            host = parsed.netloc

            # Increment counter for the parsed subdomain
            if "uci.edu" in host:
                subdomains[host] = subdomains.get(host, 0) + 1
    
    return sorted(subdomains.items())

if __name__ == "__main__":
    generate_report()
