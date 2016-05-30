"""
File: classifier.py
Author: Yousef Hindy

This file contains the high level of what this email program does.
It does not get into the nitty-gritty of downloading emails from the 
internet and instead reads data from files and can update those files.
The meat of this file is the classifyEmail method, which takes in an 
email and uses the rest of the module to determine whether or not it
is spam.
"""

import email_utils as e
import httplib2
import os
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import csv
from collections import OrderedDict
import numpy as np
from nltk.corpus import stopwords
from sklearn.naive_bayes import BernoulliNB
import json
import warnings

stop_words = set(stopwords.words('english')) #set of words to take out

def createWordList(emailids, emaildata): #creates word list of all the words used in email bodies
    """
    This function takes in a list of emailids and a dictionary of email
    data and writes all of the word stems into a dictionary that will 
    be used later to count what words are in an email.
    """
    with open('res/dictionary.txt', 'w') as f:
        words = set([])
        for emailid in emailids:
            email = e.Email(emailid)
            subject = set(email.parsedsubject)
            body = set(email.body)
            try:
                emailcontent = body.union(subject)
                for word in emailcontent:
                    if not word in words:
                        words.add(word)
                        f.write(word + '\n')
            except AttributeError:
                print(body)
          

def updateWordList(emailids):
    """
    This function takes in a list of emailids and updates the dictionary to 
    reflect all of the words in the emails
    """
    with open('res/dictionary.txt', 'r') as f:
        lines = f.readlines()
        words = set([line.strip() for line in lines])

    with open('res/dictionary.txt', 'a') as f:
        for emailid in emailids: 
            email = e.Email(emailid)
            subject = set(email.parsedsubject)
            body = set(email.body)
            try:
                emailcontent = body.union(subject)
                for word in emailcontent:
                    if not word in words:
                        words.add(word)
                        f.write(word + '\n')
            except AttributeError:
                print(body)


def importDictionary():
    """
    This function reads in the words from the dictionary file
    """
    with open('res/dictionary.txt', 'r') as f:
        lines = f.readlines()
        result = [word.strip() for word in lines]
    return result


def loadEmailData():
    """
    This function returns a dictionary of data from the emaildata.txt
    file and returns it in the form {emailid:isspam}
    """
    if os.stat('data/trialdata.txt').st_size == 0:
        return {}

    with open('data/emaildata.txt', 'r') as f:
        lines = f.readlines()
        ids = [line.split()[0] for line in lines]
        results = ([int(line.split()[1] == 'True') for line in lines])
        data = {id:result for id, result in zip(ids, results)}

        return data


def findUniqueResults(ids, results):
    """
    This function finds the total number of unique
    emails in the data. Used mainly for debugging
    """
    ordered = OrderedDict(sorted(data.items(), key=lambda t: t[0]))
    return list(ordered.values())


def countAllWords(emaildata, englishwords):
    """
    This function takes in a dictionary of email data and a set of words to count
    and writes to the trialdata.txt file the array of word counts for each email.
    """
    print("Loading...")
    emailids = emaildata.keys()
    count = 0

    if os.path.isfile('data/trialdata.txt'):
        with open('data/trialdata.txt', 'r') as f:
            if os.stat('data/trialdata.txt').st_size != 0: #if the file isn't empty
                data = json.load(f)
            else:
                data = {}
    else:
        data = {}

    with open('data/trialdata.txt', 'w') as f:
        for emailid in emailids:
            if not emailid in list(data.keys()):
                if count % 100 == 0:
                    print(count)
                count = count + 1
                data[emailid] = [countWords(emailid, englishwords), emaildata[emailid]]
        json.dump(data, f)       

    print(count)


def countWords(emailid, englishwords):
    """
    This function takes in an emailid and a dictionary of words and returns a list
    of the words in the email represented as a 1 or a 0 in each entry of the list.
    The list is the same length as englishwords.
    """
    email = e.Email(emailid)
    words = email.body
    subject = email.parsedsubject
    emailcontent = subject.update(words)
    counter = {word:0 for word in englishwords}
    ordered = OrderedDict(sorted(counter.items(), key=lambda t: t[0]))
    for word in words:
        if word in counter:
            counter[word] = counter[word] + 1

    return list(counter.values())


def getTrialData():
    """
    This function reads the trial data file and 
    gets the JSON data from it and turns it into a dictionary
    """
    with open('data/trialdata.txt', 'r') as f:
        data = json.load(f)
        return data


def buildNecessaryData():
    """
    This function takes the necessary steps in order for the 
    machine learning algorithms to be run. It first loads the email data
    and creates the dictionary of words that will be counted. It then counts the
    words and does not return anything.
    """
    emaildata = loadEmailData()
    emailids = list(emaildata.keys())
    if os.stat('res/dictionary.txt').st_size == 0:
        print("Creating word list...")
        createWordList(emailids, emaildata)
    print("Counting all words...")
    englishwords = importDictionary()
    countAllWords(emaildata, englishwords)

def updateWordCounts():
    """
    This function can be called from client modules, and it basically
    just updates the word counts in the trialdata.txt file.
    """
    emaildata = loadEmailData()
    englishwords = importDictionary()
    countAllWords(emaildata, englishwords)

def classifyEmail(emailid):
    """
    This function is the main part of this program. It takes in an emailid
    and returns whether or not that email is predicted to be spam according
    to the Naive Bayes algorithm. It uses the scikit-learn module to run
    the algorithm.
    """
    trialdata = getTrialData()
    emailids = trialdata.keys()
    wordcounts = np.array([np.array(value[0]) for value in trialdata.values()])
    results = np.array([value[1] for value in trialdata.values()])
    clf = BernoulliNB()
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    clf.fit(wordcounts, results)
    englishwords = importDictionary()
    wordlist = countWords(emailid, englishwords)
    return clf.predict(wordlist)

if __name__ == '__main__':
    buildNecessaryData()
    pass



