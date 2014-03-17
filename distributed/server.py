#!/usr/bin/python

import boto.sqs
from boto.sqs.message import RawMessage
from db import DB
import json
from queue import Queue
import time

database = DB("profiles.db")
queue = Queue()
pending = []

# Get the party started
while True:
    # Check to see if there is data waiting for us
    try:
        message = queue.GetData()
        if message is None:
            time.sleep(1)
            continue
    except KeyboardInterrupt:
        print "** bye **"
        quit()
    except:
        print "Error getting the message from the queue. Weird. Waiting a bit"
        time.sleep(30)

    # Save it to the DB and extract the links
    try:
        # Remove the current URL from our list of pending scrapes
        if message['url'] in pending:
            pending.remove(message['url'])
        database.SaveProfile(message)

        for link in message['links']:
            # If the link isn't pending or already scraped, add it to the queue
            if not link in pending and not database.HasVisited(link):
                pending.append(link)
                queue.AddUrl(link)
    except KeyboardInterrupt:
        print "** bye **"
        exit()
    except:
        print "Error adding the scraped data, ignoring..."
