#!/usr/bin/python

import boto.sqs
from boto.sqs.message import RawMessage
import json

###
# Abstraction for working with SQS
###
class Queue:
    ###
    # Creates a new Queue abstraction, opens connections to the appropriate SQS queues
    ###
    def __init__(self):
        key = "{SQS_key}"
        secret = "{SQS_secret}"
        region = "{SQS_region}"
        connection = boto.sqs.connect_to_region(region, aws_access_key_id=key, aws_secret_access_key=secret)
        
        self.URLQueue = connection.get_queue("pending_urls")
        self.URLQueue.set_message_class(RawMessage)
        self.DataQueue = connection.get_queue("scrape_data")
        self.DataQueue.set_message_class(RawMessage)

    ###
    # Returns a pending URL from the queue
    ###
    def GetUrl(self):
        data = self.URLQueue.get_messages()
        if len(data) == 0:
            return None
        self.URLQueue.delete_message(data[0])
        return data[0].get_body()
    
    ###
    # Adds the given URL to the pending queue
    ###
    def AddUrl(self, url):
        message = RawMessage()
        message.set_body(url)
        self.URLQueue.write(message)

    ###
    # Gets scrape data from the queue
    ###
    def GetData(self):
        data = self.DataQueue.get_messages()
        if len(data) == 0:
            return None
        self.DataQueue.delete_message(data[0])
        return json.loads(data[0].get_body())

    ###
    # Adds the given scrape data to the queue
    ###
    def AddData(self, data):
        message = RawMessage()
        message.set_body(json.dumps(data))
        self.DataQueue.write(message)
