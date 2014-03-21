#!/usr/bin/python

from bs4 import BeautifulSoup
from datetime import datetime
from db import db
import os
import re
import time
import twill
from twill.commands import *
import urllib
import warnings

# Tweak these as needed
DATABASE = "profiles.db"
USERNAME = "{okc_username}"
PASSWORD = "{okc_password}"
TEMPFILE = "current.html"
STARTURL = "http://www.okcupid.com/profile/{some_profile}"
SLEEPSEC = 1

# Init the DB, add the starting url if it needs to be
db = db(DATABASE)
db.AddPending(STARTURL)

# Shut twill up
f = open(os.devnull, "w")
twill.set_output(f)

# Sign in to the site
twill.commands.
twill.commands.go("https://www.okcupid.com")
try:
    twill.commands.fv("4", "username", USERNAME)
    twill.commands.fv("4", "password", PASSWORD)
    twill.commands.submit("sign_in_button")
except:
    # Maybe I'm already signed in?
    print "Error logging in, might be logged in already?"

# Scrape away
runScrapes = 0
while True:
    # Visit the next URL
    url = db.GetPending()
    if url is None:
        print "Out of URLs to scrape!"
        break

    try:
        print "[%s] Scrapes this run: %d, current URL: %s" % (str(datetime.now().time()), runScrapes, url)
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
        db.SaveProfile(url, soup)
        
        links = soup.find_all("a")
        for l in links:
            # Get the URL. If it is only a profile and NOT something deeper nested, then add it to the list of URLs to scrape
            href = l.get('href')
            match = re.match('/profile/(.+)\?', href)
            badmatch = re.match('/profile/(.+)/', href)
            if match and not badmatch:
                full = "http://www.okcupid.com" + match.group(0)[0:-1]
                db.AddPending(full)
    except Exception, e:
        print "Error parsing HTML", e
        pass

    # Don't hammer their servers, sleep a bit
    if SLEEPSEC > 0:
        time.sleep(0);

print "** Bye! **"
