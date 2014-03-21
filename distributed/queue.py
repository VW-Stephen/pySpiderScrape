#!/usr/bin/python

import boto.sqs
from boto.sqs.message import RawMessage
import json

class Queue:
    """
    Abstraction for working with SQS
    """
    def __init__(self):
        """
        Connects to the various SQS queues
        """
        key = "{SQS_key}"
        secret = "{SQS_secret}"
        region = "{SQS_region}"
        connection = boto.sqs.connect_to_region(region, aws_access_key_id=key, aws_secret_access_key=secret)
        
        self.URLQueue = connection.get_queue("pending_urls")
        self.URLQueue.set_message_class(RawMessage)
        self.DataQueue = connection.get_queue("scrape_data")
        self.DataQueue.set_message_class(RawMessage)

    def GetUrl(self):
        """
        Returns a pending URL from the queue
        """
        data = self.URLQueue.get_messages()
        if len(data) == 0:
            return None
        self.URLQueue.delete_message(data[0])
        return data[0].get_body()

    def AddUrl(self, url):
        """
        Adds the given URL to the pending queue

        url - The url to add to the queue
        """
        message = RawMessage()
        message.set_body(url)
        self.URLQueue.write(message)

    def GetData(self):
        """
        Returns scraped data from the queue
        """
        data = self.DataQueue.get_messages()
        if len(data) == 0:
            return None
        self.DataQueue.delete_message(data[0])
        return json.loads(data[0].get_body())

    def AddData(self, data):
        """
        Adds the given scraped data to the queue

        data - A dictionary of scrape data to add to the queue
        """
        message = RawMessage()
        message.set_body(json.dumps(data))
        self.DataQueue.write(message)
