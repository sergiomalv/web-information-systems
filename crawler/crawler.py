#-------------------------------------------------------------------------------
# Name:        Creation of a basic crawler
# Purpose:     A crawler is a program that automatically and recursively scans
#              the Web, usually for the purpose of feeding the index of a web
#              search engine, but also for the creation of a mirror (a replica
#              of a given website).
#
# Author:      Sergio Murillo
#
# Created:     06/10/2022
#-------------------------------------------------------------------------------

from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib.request, urllib.error, urllib.parse, urllib.robotparser
import requests
import time
from collections import deque

# Change for a different maximum number of downloads
max_downloads = 10
# Change according to the file containing the seeds
file = "base.txt"
# Change according to the desired wait between GET requests
pause_seconds = 10
# Change according to the search you want: True will be deep search, False will
# be width search
deep_search = False
# Auxiliary list where to save the visited links
visited = set()
# Auxiliary queue for width search
q = deque()

class FullDownloadsExceptcion(Exception):
    """
    Exception that stops the crawler in case of reaching the maximum number of
    downloads
    """
    pass

def crawl_deep(url, seconds):
    """
    Runs the crawler with a deep search
    """
    global max_downloads, visited
    if max_downloads == 0:
        raise FullDownloadsExceptcion()
    time.sleep(seconds)
    html = requests.get(url)
    max_downloads -= 1
    save_to_file(url, html)
    soup = BeautifulSoup(html.content, 'html.parser')
    links = soup.find_all('a')
    for l in links:
        if (l.get('href') != None):
            l = normalize_link(url, l.get('href'))
            if l not in visited:
                try:
                    r = requests.head(l)
                    if "text/html" in r.headers["content-type"]:
                        visited.add(l)
                        crawl_deep(l, seconds)
                except Exception:
                    return

def crawl_width(url, seconds):
    """
    Runs the crawler with a width search
    """
    global max_downloads
    global visited, newLinks
    global q
    if max_downloads == 0:
        raise FullDownloadsExceptcion()
    time.sleep(seconds)
    html = requests.get(url)
    max_downloads -= 1
    save_to_file(url, html)
    soup = BeautifulSoup(html.content, 'html.parser')
    links = soup.find_all('a')
    for l in links:
        if (l.get('href') != None):
            l = normalize_link(url, l.get('href'))
            if l not in visited:
                try:
                    r = requests.head(l)
                    if "text/html" in r.headers["content-type"]:
                        visited.add(l)
                        q.append(l)
                except Exception:
                    pass

def save_to_file(url, html):
    """
    Save an .html file
    """
    toSave = get_title(url) + ".html"
    with open(toSave, 'wb+') as f:
        f.write(html.content)
        f.close()
        print(toSave, "successfully downloaded")

def normalize_link(url, link):
    """
    Normalizes a link with its given url if needed
    """
    if link.startswith("/") or link.startswith("#"):
        result = urljoin(url, link) # urlparse
        return result
    return link

def get_title(url):
    """
    Converts a url to a string that can be used as the name of a document
    """
    result = ''
    for char in url:
        if (str(char) not in ('/:.')):
            result += str(char)
        else :
            result += '-'

    # Delete the last character in case it is '/'.
    if (result[len(result)-1] == '/'):
        result = result[:-1]
    # Delete https-www from the string
    result = result[11:]

    # Delete the first character in case it is '-'
    if (result[0] == '-'):
        result = result[1:]

    return result

def get_seconds_wait_robots(url):
    """
    Check if there is any time restriction inside /robots.txt when using a
    crawler
    """
    rp = urllib.robotparser.RobotFileParser()
    print("Checking: " + url + "/robots.txt")
    rp.set_url(url + "/robots.txt")
    rp.read()

    # We check that we can use the crawler on the website
    if (rp.can_fetch("*", url)):
        # Change the timeout in case robots.txt tells us to do
        if(rp.crawl_delay("*") != None):
            pause_seconds = rp.crawl_delay("*")
            print(url + "/robots.txt has a delay of", pause_seconds, "for crawlers")
    else:
        return False
    return True


def main():
    """
    Open the file containing the seeds and run the crawler recursively until the
    maximum number of downloads is reached
    """
    global visited
    global q
    seeds =open(file, mode='r')

    if (deep_search):
        try:
            for seed in seeds:
                visited.add(seed.rstrip('\n'))
                response = get_seconds_wait_robots(seed.rstrip('\n'))
                if(response):
                    crawl_deep(seed.rstrip('\n'), pause_seconds)
                else:
                    print("Can't crawler", seed)
        except FullDownloadsExceptcion:
            print("The maximum number of downloads has been reached")
    else:
        try:
            for seed in seeds:
                visited.add(seed.rstrip('\n'))
                response = get_seconds_wait_robots(seed.rstrip('\n'))
                if (response):
                    q.append(seed.rstrip('\n'))
                else:
                    print("Can't crawler", seed)
            while q:
                crawl_width(q.popleft(), pause_seconds)
        except FullDownloadsExceptcion:
            print("The maximum number of downloads has been reached")


if __name__ == '__main__':
    main()