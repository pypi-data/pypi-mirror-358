import logging
import urllib
from collections import deque
from time import sleep

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


class Gleaner:
    """
    Gleaner object
    Has a start url
    scrape() will obtain HTML of start url, and search for hyperlinks within the
    page that point to a page on start_url. It then performs the same operations
    on all these hyperlinks creating a BFS search of the page.
    """

    def __init__(self, start_url, rate_limiter):
        self.start_url = start_url
        # strips the url: https://example.com/page/path -> https://example.com
        self.base_url = urllib.parse.urlparse(start_url).netloc
        self.de = deque([start_url])
        # Avoid gleaning same pages
        # Misleading name. Stores all urls visited, or that are present in self.de
        self.visited = {start_url}

        self.rate_limiter = rate_limiter

    def scrape(self):
        """
        Performs the BFS
        """
        pbar = tqdm(total=len(self.visited), desc="Scraping", unit=" pages ")
        failed_urls = []

        while len(self.de) > 0:
            url = self.de.pop()
            links = self.get_a_links(url)
            links = set(self.filter_and_parse_links(links, url))
            self.visited = self.visited.union(links)

            self.de.extendleft(links)

            # Update progress bar
            pbar.total = len(self.visited)
            pbar.update(1)
            pbar.refresh()
        pbar.close()

        print(f"Done! Found {len(self.visited)} pages")

        return self.visited

    def get_a_links(self, url):
        """
        Returns the hrefs of ALL a tags.
        TODO: This will miss a lot of links. Especially to images and such.
        """
        links = []
        self.rate_limiter.wait()
        # Try to request page
        try:
            response = requests.get(url)

            # If rate limited, wait a second, then try again
            if response.status_code == 429:
                logging.warning(f"Rate limited on {url}")

                sleep(1)
                response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            # For any request errors, return an empty list
            logging.error(f"Failed to analyze {url}: {e}")
            return []

        # Parse page
        soup = BeautifulSoup(response.text, "html.parser")

        # Obtain hrefs
        for a_tag in soup.find_all("a"):
            link = a_tag.get("href")
            if not link:  # Skip if a tag doesn't have href attribute
                continue
            if link.endswith(".xml"):
                continue
            links.append(link)

        return links

    def filter_and_parse_links(self, links, base):
        """
        links: list of links
        base: any url

        Removes all links that:
        - Aren't a child of self.base_url
        -
        """
        res = []
        for link in links:
            # absolute_link = base + link
            absolute_link = urllib.parse.urljoin(base, link)
            parsed_link = urllib.parse.urlparse(absolute_link)

            # Skip link if it isn't on self.base_url
            if parsed_link.netloc != self.base_url:
                continue

            # Removes fragments and returns unparsed url
            normalized_link = urllib.parse.urlunparse(
                parsed_link._replace(fragment="")
            )

            # Make sure normalized_link wasn't visited. Then process it
            if normalized_link not in self.visited:
                res.append(normalized_link)
        return res
