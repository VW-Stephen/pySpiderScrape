#!/usr/bin/python

from bs4 import BeautifulSoup
import sqlite3

###
# An abstraction to the profile database
###
class DB:
    ###
    # Creates a new database at the given filename
    ###
    def __init__(self, filename):
        self.Filename = filename
        self.Connection = sqlite3.connect(filename)
        self.Cursor = self.Connection.cursor()

    ###
    # Saves the profile to the database
    ###
    def SaveProfile(self, data):
        self.Cursor.execute("INSERT INTO profiles (url, e0, e1, e2, e3, e4, e5, e6, e7, e8, gender, age, orientation, status, location) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (data['url'], data['e0'], data['e1'], data['e2'], data['e3'], data['e4'], data['e5'], data['e6'], data['e7'], data['e8'], data['gender'], data['age'], data['orientation'], data['status'], data['location']))
        self.Connection.commit()

    ###
    # Returns if the given URL exists in the database or not
    ###
    def HasVisited(self, url):
        self.Cursor.execute("SELECT 1 FROM profiles WHERE url = ? LIMIT 1", (url,))
        return self.Cursor.fetchone() is not None
