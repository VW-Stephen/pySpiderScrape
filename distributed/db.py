#!/usr/bin/python

from bs4 import BeautifulSoup
import sqlite3

class DB:
    """
    Abstraction for the profile database
    """
    def __init__(self, filename):
        """
        Creates a new connection to the database

        filename - The name of the database file to use
        """
        self.Filename = filename
        self.Connection = sqlite3.connect(filename)
        self.Cursor = self.Connection.cursor()

    def SaveProfile(self, data):
        """
        Saves the profile to the database

        data - A dictionary of profile information
        """
        self.Cursor.execute("INSERT INTO profiles (url, e0, e1, e2, e3, e4, e5, e6, e7, e8, gender, age, orientation, status, location) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (data['url'], data['e0'], data['e1'], data['e2'], data['e3'], data['e4'], data['e5'], data['e6'], data['e7'], data['e8'], data['gender'], data['age'], data['orientation'], data['status'], data['location']))
        self.Connection.commit()

    def HasVisited(self, url):
        """
        Returns true if the given URL is in the database, false otherwise

        url - The URL to check
        """
        self.Cursor.execute("SELECT 1 FROM profiles WHERE url = ? LIMIT 1", (url,))
        return self.Cursor.fetchone() is not None
