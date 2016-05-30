"""
File: email_utils.py
Author: Yousef Hindy

This file contains some useful things for dealing with Google's gmail
API. It implements an email class, which has a sender, recipient, subject,
body, and id. All it needs for creation is the emailid, which is taken
from what the GMail API's JSON gives.
"""


import datacollection
import httplib2
import os
import base64 #base64.urlsafe_b64decode
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import regex

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

stop_words = set(stopwords.words('english'))
ps = PorterStemmer()

class Email:
    """
    Class: Email

    This class represents an email message. It holds several pieces of data for it.
    1. subject: the email's subject as a plain string
    2. parsedsubject: the email's subject as a set of stemmed words
    3. sender
    4. recipient
    5. body: the email's body as a set of stemmed words
    6. labels: categories the email belongs to
    7. id: a unique identifier which identifies this message
    """

    def __init__(self, id):
        credentials = datacollection.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http=http)
        text = service.users().messages().get(userId ='me', id=id, format = 'full').execute()
        headers = text.get('payload').get('headers')
        parts = text.get('payload').get('parts')
        for header in headers:
            if header.get('name') == 'Subject':
                self.subject = (header.get('value'))
                self.parsedsubject = set(parseString(self.subject.split()))
            if header.get('name') == 'From':
                self.sender = getEmailAddress(header.get('value'))
            if header.get('name') == 'Delivered-To': #there are two ways to get the recipient
                self.recipient = getEmailAddress(header.get('value'))
            if header.get('name') == 'To':
                self.recipient = getEmailAddress(header.get('value'))

        if parts is not None: 
            self.body = parseEmailData(parts)
        else: #sometimes the payload is just a body and it doesn't have any parts
            encoded = text.get('payload').get('body').get('data')
            self.body = set(parseString(decodeBase64(encoded)))

        self.labels = text.get('labelIds')
        self.id = id

    def __str__(self):
        try:
            return "ID: {id}, From: {sender}, To: {recipient}, Subject: {subject}".format(id = self.id, sender = self.sender, recipient = self.recipient, subject = str(self.subject))
        except AttributeError:
            return "From: {sender}, Subject: {subject}".format(sender = self.sender, subject = str(self.subject))

def getEmailAddress(rawemail):
    """
    This function takes a rawemail address in the form {First} {Last} <{emailaddress}>
    and extracts the email address.
    """
    try:
        return regex.search(r'[\w\.-]+@[\w\.-]+', rawemail).group(0)
    except AttributeError:
        return "Me"


def parseEmailData(parts):
    """
    This function tries to find the portion of the email data that is actually the 
    text and decodes it from base64url encoding into regular UTF-8 and returns a 
    stemmed set of the words in the email. 
    """
    if parts[0].get('mimeType') == 'multipart/alternative':
        return parseEmailData(parts[0].get('parts'))
    for part in parts:
        if (part.get('mimeType') == 'text/plain'):
            data = part.get('body').get('data') #get the base64url encoded data
            words = decodeBase64(data)
            return set(parseString(words))
    return "An error has occurred"

def decodeBase64(data):
    """
    This function takes in data in the form of base64url data and returns a 
    list of the words that are represented by it.
    """
    try:    
        htmldata = base64.urlsafe_b64decode(data) # decode it into html
        soup = BeautifulSoup(htmldata, 'html.parser') # recover the text from html
        words = word_tokenize(soup.get_text()) # break up the text into tokens
        return words
    except TypeError:
        return []

def parseString(listofwords):
    """
    This function takes a list of words and returns the stems of the words that are not
    common "stop-words" (i.e. words that do not really add to the meaning of the text)
    """
    return [ps.stem(word.lower()) for word in listofwords if not word in stop_words and word.isalpha()]

