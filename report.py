import os
import json
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
from scraper import URL_MAP, HTML_DIR

REPORT = "report.txt"
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no",
    "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our",
    "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd",
    "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that",
    "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
    "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's",
    "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom",
    "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll",
    "you're", "you've", "your", "yours", "yourself", "yourselves",
}

#helper function that TA reccomended for getting just the text content for the 50 most common words
def get_page_text(soup):
    for tag in soup.find_all(["script", "style"]):
        tag.decompose()
    return soup.get_text(separator=" ")

def tokenize_text(text):
    tokens = []
    current = []
 
    for char in text:
        try:
            if char.isalnum() and char.isascii():
                current.append(char.lower())
            elif char == "'" and current:
                # allow apostrophe in the middle of a word
                current.append(char)
            elif current:
                # remove trailing apostrophes
                while current and current[-1] == "'":
                    current.pop()
                if current:
                    token = "".join(current)
                    if len(token) > 1:
                        tokens.append(token)
                current = []
        except Exception:
            #skip unknown characters
            current = []

    while current and current[-1] == "'":
        current.pop()
    if current:
        token = "".join(current)
        if len(token) > 1:
            tokens.append(token)
    return tokens

def compute_word_frequencies(tokens):
    frequency = {}
    for word in tokens:
        if word in STOPWORDS:
            continue
        frequency[word] = frequency.get(word, 0) + 1
    return frequency

def get_top_50_words():
    combined_frequencies = {}
 
    for filename in os.listdir(HTML_DIR):
        if not filename.endswith(".html"):
            continue
        path = os.path.join(HTML_DIR, filename)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                soup = BeautifulSoup(fh.read(), "html.parser")
            tokens = tokenize_text(get_page_text(soup))
            for word, count in compute_word_frequencies(tokens).items():
                combined_frequencies[word] = combined_frequencies.get(word, 0) + count
        except Exception:
            continue
 
    sorted_words = sorted(combined_frequencies.items(), key=lambda x: x[1], reverse=True)
    return sorted_words[:50]

def get_longest_page():
    # Build a path -> url lookup from the url map
    path_to_url = {}
    with open(URL_MAP, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                path_to_url[entry["path"]] = entry["url"]
            except (json.JSONDecodeError, KeyError):
                continue
 
    longest_url = None
    longest_count = 0
 
    for filename in os.listdir(HTML_DIR):
        if not filename.endswith(".html"):
            continue
        path = os.path.join(HTML_DIR, filename)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                soup = BeautifulSoup(fh.read(), "html.parser")
            count = len(tokenize_text(get_page_text(soup)))
            if count > longest_count:
                longest_count = count
                url = path_to_url.get(path, path)
                longest_url = urldefrag(url)[0]
        except Exception:
            continue
 
    return longest_url, longest_count

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

def generate_report():
    with open(REPORT, "w") as f:
        unique_pages = get_unique_pages()
        print(f"Unique pages: {unique_pages}", file=f)

        subdomains = get_subdomains()
        print("\nSubdomains:", file=f)
        for subdomain, count in subdomains:
            print(f"{subdomain}, {count}", file=f)

        longest_url, longest_count = get_longest_page()
        print(f"\nLongest page: {longest_url} ({longest_count} words)", file=f)

        print("\nTop 50 most common words:", file=f)
        for word, count in get_top_50_words():
            print(f"  {word} -> {count}", file=f)

if __name__ == "__main__":
    generate_report()
