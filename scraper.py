import re
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup

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

    if resp.status != 200:
        return links

    html = resp.raw_response.content
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all("a", href=True):
        href = tag.get("href")
        link, _ = urldefrag(urljoin(resp.url, href))
        links.append(link)

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

#     links = []
#     links += extract_next_links("https://ics.uci.edu/", response1) # ['https://ics.uci.edu/research-areas/']
#     links += extract_next_links("https://ics.uci.edu/", response2) # ['https://ics.uci.edu/']
#     links += extract_next_links("https://ics.uci.edu/", response3) # ['https://ics.uci.edu/facts-figures/ics-mission-history/']
#     links += extract_next_links("https://ics.uci.edu/", response4) # []
#     print(links)
# print(is_valid("https://wics.ics.uci.edu/")) # True
# print(is_valid("https://ics.uci.edu/")) # True
# print(is_valid("https://www.instagram.com/wicsuci/")) # False
# print(is_valid("https://ics.uci.edu/event/building-worker-resilience-in-place-based-communities-amid-rapid-technological-change-april/")) #True

