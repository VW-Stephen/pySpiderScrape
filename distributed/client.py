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

USERNAME = "{okc_username}"
PASSWORD = "{okc_password}"
TEMPFILE = "current.html"
SLEEPSEC = 0.5

def ParsePage(url, soup):
    # Extract the info from the soup and save it
    e0 = soup.find("div", {"id" : "essay_text_0"})
    e0 = '' if e0 is None else e0.text
    e1 = soup.find("div", {"id" : "essay_text_1"})
    e1 = '' if e1 is None else e1.text
    e2 = soup.find("div", {"id" : "essay_text_2"})
    e2 = '' if e2 is None else e2.text
    e3 = soup.find("div", {"id" : "essay_text_3"})
    e3 = '' if e3 is None else e3.text
    e4 = soup.find("div", {"id" : "essay_text_4"})
    e4 = '' if e4 is None else e4.text
    e5 = soup.find("div", {"id" : "essay_text_5"})
    e5 = '' if e5 is None else e5.text
    e6 = soup.find("div", {"id" : "essay_text_6"})
    e6 = '' if e6 is None else e6.text
    e7 = soup.find("div", {"id" : "essay_text_7"})
    e7 = '' if e7 is None else e7.text
    e8 = soup.find("div", {"id" : "essay_text_8"})
    e8 = '' if e8 is None else e8.text
    gender = soup.find("span", {"id" : "ajax_gender"})
    gender = '' if gender is None else gender.text
    age = soup.find("span", {"id" : "ajax_age"})
    age = '' if age is None else age.text
    orientation = soup.find("span", {"id" : "ajax_orientation"})
    orientation = '' if orientation is None else orientation.text
    status = soup.find("span", {"id" : "ajax_status"})
    status = '' if status is None else status.text
    location = soup.find("span", {"id" : "ajax_location"})
    location = '' if location is None else location.text

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

    return {
        'e0': e0,
        'e1': e1,
        'e2': e2,
        'e3': e3,
        'e4': e4,
        'e5': e5,
        'e6': e6,
        'e7': e7,
        'e8': e8,
        'gender': gender,
        'age': age,
        'orientation': orientation,
        'status': status,
        'location': location,
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
