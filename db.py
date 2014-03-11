#!/usr/bin/python

from bs4 import BeautifulSoup
import sqlite3

class db:
    def __init__(self, filename):
        self.Filename = filename
        self.Connection = sqlite3.connect(filename)
        self.Cursor = self.Connection.cursor()

    def SaveProfile(self, url, soup):
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
    
        self.Cursor.execute("INSERT INTO profiles (url, e0, e1, e2, e3, e4, e5, e6, e7, e8, gender, age, orientation, status, location) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (url, e0, e1, e2, e3, e4, e5, e6, e7, e8, gender, age, orientation, status, location))
        self.Connection.commit()

    def AddPending(self, url):
        # If the url is already visited/pending, then do nothing
        self.Cursor.execute("SELECT url FROM profiles WHERE url = ? UNION SELECT url FROM pending_urls WHERE url = ?", (url, url))
        results = self.Cursor.fetchone()
        if results is not None:
            return

        # Otherwise add it
        self.Cursor.execute("INSERT INTO pending_urls (url) VALUES (?)", (url,))
        self.Connection.commit()

    def GetPending(self):
        self.Cursor.execute("SELECT url FROM pending_urls LIMIT 1")
        results = self.Cursor.fetchone()
        if results is None:
            return None;

        ret = results[0]

        self.Cursor.execute("DELETE FROM pending_urls WHERE url = ?", (ret,))
        self.Connection.commit()

        return ret
