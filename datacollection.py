"""
File: datacollection.py
Author: Yousef Hindy

This file contains main functionality of the email helper. When run,
it gets the credentials for a google mail account from the google website
and then goes through each message in the inbox and asks the user if 
the message is spam or not. This builds up the data for the machine
learning algorithm.

N.B. This was adapted from the quickstart.py file from:
https://developers.google.com/gmail/api/quickstart/python

"""

import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import nltk

import classifier

import email_utils as e



try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CLIENT_SECRET_FILE = 'res/client_secret_email.json'
APPLICATION_NAME = "Yousef's Email Helper"

PAGE_COUNT = 25


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-email.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def getResponse():
    """
    This function gets a response from the user about the
    "goodness" of a given message
    """
    score = input("Enter 'G' for Good, 'S' for Spam, 'E' for Exit: ").lower()
    while score not in ['g', 's', 'e']:
        score = input("Invalid input, try again (G or S): ").lower()

    keepgoing = score != 'e'
    return score == 'g', keepgoing

def getResponse2(emailid):
    """
    This function uses the prediction methods to predict whether
    a given email is spam or not. It then asks the user if the 
    answer was right or wrong.
    """
    prediction = bool(classifier.classifyEmail(emailid)[0])
    if prediction:
        print("The prediction is: Not Spam")
    else:
        print("The prediction is: Spam")
    score, keepgoing = getResponse()

    return score, score == prediction, keepgoing


def isPredictionMode():
    if not os.path.isfile('data/trialdata.txt') or \
           os.stat('data/trialdata.txt').st_size == 0:
        return False

    response = input("Enter P for Prediction Mode, C for Collecting Mode: ").lower()

    while response not in ['p', 'c']:
        response = input("Invalid input, try again (P or C): ").lower()

    return response == 'p'


def main():
    """
    Creates a Gmail API service object and asks the user about several of his
    or her messages in his or her inbox.
    """

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    results = service.users().labels().list(userId='me').execute()
    nextpage = None

    keepgoing = True

    with open('data/trialdata.txt', 'a') as f: #creates the files if they do not exist
        pass
    with open('data/emaildata.txt', 'a') as f:
        pass
    with open('res/dictionary.txt', 'a') as f:
        pass

    predictionMode = isPredictionMode()

    with open('data/statistics.txt', 'r') as f: #first number is number right, #second is number wrong
        lines = f.readlines()
        right = int(lines[0].strip())
        wrong = int(lines[1].strip())

    with open('data/emaildata.txt', 'a') as f:
        classifier.buildNecessaryData() # update the training data
        emaildata = classifier.loadEmailData() # load email ids and results
        print('Messages: ')
        for i in range(PAGE_COUNT):
            messagejson = service.users().messages().list(userId='me', pageToken = nextpage).execute()
            nextpage = messagejson.get('nextPageToken')
            messages = messagejson.get('messages', [])
            for ind, message in enumerate(messages):
                if message['id'] not in list(emaildata.keys()):
                    curremail = e.Email(message['id'])
                    print (ind, curremail)
                    if predictionMode:
                        isgoodmessage, iscorrectprediction, keepgoing = getResponse2(message['id'])
                        if iscorrectprediction:
                            right += 1
                        else:
                            wrong += 1
                    else: 
                        isgoodmessage, keepgoing = getResponse()
                    if not keepgoing:
                        break
                    f.write(message['id'] + '\t' + str(isgoodmessage) + '\n')

            if not keepgoing:
                break

    with open('data/statistics.txt', 'w') as f:
        f.write(str(right) + '\n' + str(wrong))



if __name__ == '__main__':
    main()