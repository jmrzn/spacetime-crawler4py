import re
import os
import json
from hashlib import md5
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup

MAX_SIZE = 1024 * 1024 * 5 # 5 MB, as the normal pages are below this number
HTML_DIR = "pages"
URL_MAP = "url_map.jsonl"

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    links = []

    # Check that response is valid and has content
    if not is_valid_resp(resp):
        return links

    # checks the size of the page before extracting
    size = resp.raw_response.headers.get("Content-Length")
    # print("size of file:", size)
    try: 
        if size and int(size) > MAX_SIZE:
            return []
    except ValueError:
        pass
    except TypeError:
        pass
    
    html = resp.raw_response.content
    save_html(resp.url, html)
    soup = BeautifulSoup(html, "html.parser")

    # Extract hyperlinks from the HTML <a> tags
    # Defragment and join partial URLs
    for tag in soup.find_all("a", href=True):
        try:
            href = tag.get("href")
            link, _ = urldefrag(urljoin(resp.url, href))
            links.append(link)
        except ValueError:
            continue
    
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        print(parsed.netloc.lower())

        # Only crawls in specified domains 
        if not re.match(r".*\.(ics|cs|informatics|stat)\.uci\.edu$", parsed.netloc.lower()):
            if not re.match(r"(ics|cs|informatics|stat)\.uci\.edu$", parsed.netloc.lower()):
                return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def is_valid_resp(resp):
    # Return True if the response's status is 200 and has content; return False otherwise
    return (resp.status == 200 and
            resp.raw_response and
            resp.raw_response.content and
            len(resp.raw_response.content.strip()) > 0)

def save_html(url, html):
    # Create HTML directory if it doesn't already exist
    os.makedirs(HTML_DIR, exist_ok=True)
    # Hash URL to create a unique file name
    file_name = md5(url.encode()).hexdigest()
    # Create file path
    path = os.path.join(HTML_DIR, file_name + ".html")

    # Save HTML to file
    with open(path, "w") as f:
        f.write(html.decode("utf-8", errors="ignore"))

    # Create jsonl file for URL mapping, if it doesn't already exist
    # Append URL and corresponding path
    with open(URL_MAP, "a") as m:
        m.write(json.dumps({"url": url, "path": path}) + "\n")

# if __name__ == "__main__":
#     class TestRawResponse:
#         def __init__(self, content):
#             self.content = content
    
#     class TestResponse:
#         def __init__(self, url, status, content):
#             self.url = url
#             self.status = status
#             self.raw_response = TestRawResponse(content)
    
#     response1 = TestResponse(url = "https://ics.uci.edu/", status = 200,
#         content = """<a href="/research-areas/"</a>""") # Partial url
#     response2 = TestResponse(url = "https://ics.uci.edu/", status = 200,
#         content = """<a href="#a11y-skip-link-content"</a>""") # Fragment only
#     response3 = TestResponse(url = "https://ics.uci.edu/", status = 200,
#         content = """<a href="https://ics.uci.edu/facts-figures/ics-mission-history/"</a>""") # Full url
#     response4 = TestResponse(url = "https://ics.uci.edu/", status = 400,
#         content = """<a href="https://ics.uci.edu/facts-figures/ics-mission-history/"</a>""") # Status is not 200
#     response5 = TestResponse(url = "https://ics.uci.edu/", status = 200,
#         content = "") # Status is 200, but no data

#     links = []
#     links += extract_next_links("https://ics.uci.edu/", response1) # ['https://ics.uci.edu/research-areas/']
#     links += extract_next_links("https://ics.uci.edu/", response2) # ['https://ics.uci.edu/']
#     links += extract_next_links("https://ics.uci.edu/", response3) # ['https://ics.uci.edu/facts-figures/ics-mission-history/']
#     links += extract_next_links("https://ics.uci.edu/", response4) # []
#     links += extract_next_links("https://ics.uci.edu/", response5) # []
#     print(links)

# save_html("https://ics.uci.edu/", "test 1")
# save_html("https://ics.uci.edu/facts-figures/ics-mission-history/", "test 2")

# print(is_valid("https://wics.ics.uci.edu/")) # True
# print(is_valid("https://ics.uci.edu/")) # True
# print(is_valid("https://www.instagram.com/wicsuci/")) # False
# print(is_valid("https://ics.uci.edu/event/building-worker-resilience-in-place-based-communities-amid-rapid-technological-change-april/")) #True

