#!/usr/bin/python

from bs4 import BeautifulSoup
from datetime import datetime
import gc
import os
from queue import Queue
import re
import time
import twill
from twill.commands import *
import urllib
import warnings

# Tweak these constants as needed
USERNAME = "{okc_username}"
PASSWORD = "{okc_password}"
TEMPFILE = "current.html"
SLEEPSEC = 0.5

def GetInnerHtml(soup, tag, id):
    """
    Searches the soup for the given tag+id, and returns the inner HTML, or an empty string when the tag+id doesn't exist.

    soup - BeautifulSoup object for the page
    tag  - The tag type to search for
    id   - The ID attribute of the tag
    """
    t = soup.find(tag, {"id" : id})
    if t is None:
        return ''
    return t.text

def ParsePage(url, soup):
    """
    Parses the given soup, returns a dictionary of raw profile information.

    url  - The URL of the page being parsed
    soup - BeautifulSoup object for the page
    """
    links = soup.find_all("a")
    goodLinks = []
    for l in links:
        # Get the URL. If it is only a profile and NOT something deeper nested, then add it to the list of URLs to scrape
        href = l.get('href')
        match = re.match('/profile/(.+)\?', href)
        badmatch = re.match('/profile/(.+)/', href)
        if match and not badmatch:
            full = "http://www.okcupid.com" + match.group(0)[0:-1]
            goodLinks.append(full)

    # Return a dictionary of the scraped data
    return {
        'e0': GetInnerHtml(soup, "div", "essay_text_0"),
        'e1': GetInnerHtml(soup, "div", "essay_text_1"),
        'e2': GetInnerHtml(soup, "div", "essay_text_2"),
        'e3': GetInnerHtml(soup, "div", "essay_text_3"),
        'e4': GetInnerHtml(soup, "div", "essay_text_4"),
        'e5': GetInnerHtml(soup, "div", "essay_text_5"),
        'e6': GetInnerHtml(soup, "div", "essay_text_6"),
        'e7': GetInnerHtml(soup, "div", "essay_text_7"),
        'e8': GetInnerHtml(soup, "div", "essay_text_8"),
        'gender': GetInnerHtml(soup, "span", "ajax_gender"),
        'age': GetInnerHtml(soup, "span", "ajax_age"),
        'orientation': GetInnerHtml(soup, "span", "ajax_orientation"),
        'status': GetInnerHtml(soup, "span", "ajax_status"),
        'location': GetInnerHtml(soup, "span", "ajax_location"),
        'url': url,
        'links' : goodLinks
    }

# Shut twill up
f = open(os.devnull, "w")
twill.set_output(f)

# Sign in to the site
twill.commands.agent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36")
twill.commands.go("https://www.okcupid.com")
try:
    twill.commands.fv("4", "username", USERNAME)
    twill.commands.fv("4", "password", PASSWORD)
    twill.commands.submit("sign_in_button")
except:
    # Maybe I'm already signed in?
    print "Error logging in, might be logged in already?"

# Scrape away
queue = Queue()
runScrapes = 0
while True:
    # Visit the next URL
    url = queue.GetUrl()
    if url is None:
        time.sleep(1)
        continue

    try:
        print "[%s] Scrapes this run: %d , current URL: %s" % (str(datetime.now().time()), runScrapes, url)
        twill.commands.go(url)
        runScrapes += 1

        # Get the page content.
        # TODO: Is there a cooler way to get this as not a file, but a string? So much I/O...
        twill.commands.save_html(TEMPFILE)
        infile = open(TEMPFILE)
        html = infile.read()
        infile.close()
    except:
        print "** Error getting HTML for %s, ignoring that URL **" % url
        continue

    # Clean up the HTML, because it's not parseable otherwise
    while True:
        start = html.find("<script")
        end = html.find("</script>") + 9
        if start == -1:
            break
        html = html[0:start] + html[end:]

    # Save the profile, add the links we find too
    try:
        soup = BeautifulSoup(html)
        data = ParsePage(url, soup)
        queue.AddData(data)
        
        soup.decompose()
        gc.collect()
    except Exception, e:
        print "Error parsing HTML", e
        pass
    
    # Don't murder their servers, sleep a bit
    if SLEEPSEC > 0:
        time.sleep(SLEEPSEC)
    
print "** Bye! **"
