Welcome to the Python Email Helper

I. General Overview:

This program will help you (with a little bit of effort) clean up your messy inbox by telling the computer which emails you want to see, and which emails you don't. After you've told the computer about enough of your emails, it will be able to predict which of your remaining and incoming emails are spam and which ones aren't. As of right now, this program only works for Google Gmail accounts, so if you do not have one of those this may not work for you. Writing this code was mainly an exercise in trying to understand the Google API's and figuring out the best way to decode and store the email data. In addition, it was my first (although brief and not really in depth) foray into the world of machine learning, as I relied extensively on the Naive Bayes classifying method from the scikit-learn module to actually do the classifying for me.

II. Technical Overview:

1) Storing Email Data:
The first challenge of this assignment was to navigate the Google API and figure out the best way to store the massive amounts of data that were encoded in each message. While I was only really interested in the subject, sender, recipient, and body of an email message, if you look at the actual JSON response that is received after querying Google for messages, there is so much other meta-data that needed to be sifted through in order to find something useful. This is where the email_utils.py module comes in. After sifting through some sample JSON messages, I determined that the most efficient way to store the data would be to keep each email's unique identifier instead of downloading an entire message. As a result, I decided to make an Email class that would be able to retrieve all of the necessary elements of an email message given the email's id. The actual email id's are stored in the emaildata.txt file, which on each line contains the pairing of an email id and a boolean to indicate whether or not that message is good (True for not spam, False for spam).

2) Collecting Email Data:
In order to have decent results with the machine learning algorithm, the computer needs to be trained on a large set of training data before it can make accurate predictions. Since the problem of classifying text deals with such a large number of permutations and combinations of tens of thousands of different words, one or two emails would not be able to cut it in terms of training the computer. As a result, in the first stage of development I wrote the datacollection.py file such that it would print out a nice, readable string representation of the email in question and then ask the user whether or not that email was spam. Once the user responded, the program would then write the answer to the emaildata.txt file for safe-keeping. Since going through and classifying each email is a tedious, time-consuming process (one of the problems with this program), I only was able to classify about 1000 emails before first trying the machine learning algorithms (I have about 1500 as of 5/29)

3) Making Sense of the Email Data:
Parts 1) and 2) are mainly focused on the datacollection.py and email_utils.py portions of the program. These were mostly just data collection and handling modules that tried to most efficiently store the data for the problem at hand. The actual module that solves the problem is the classifier.py module. This module contains a method called buildNecessaryData(), which first creates a dictionary with all of the words in the emails that have been analyzed so that for each email an array can be created of which words it has (represented as a "1" in the index of the word). Afterwards, it goes through all the emails that have been manually classified and determines which words from the dictionary the particular email has. This is stored in the trialdata.txt file as a dictionary where emailids are keys. The values in this dictionary are 1): an array of which words it has and 2): a 1 or a 0 to denote whether or not the email was spam. Afterwards, this data is made into two arrays. One of which is n x m (where n is the number of emails and m is the number of possible words) and the other is n x 1. The first represents each email's words and the second represents each email's spam status. These two are then fed into the scikit-learn Naive Bayes Bernoulli classifier, which specializes when the data is binary (the word is in the email or it isn't). This creates an object that can then be used to predict the outcomes of future emails. 

4) Checking My Work
After I finally was able to get the computer to make a prediction, I wanted to know how accurate those predictions were. I modified the datacollection.py file to have an option where the computer will print the friendly representation of the email and it's prediction about whether or not it was spam or not. The user then tells the computer the true status of the email. I noticed over time that when I had smaller sets of emails that the results were not as good as when the data set grew larger. I created a statistics.txt file to keep track of how many emails it correctly/incorrectly encoded. The stats can be a little bit skewed, however, as sometimes it will incorrectly label the same email thread several times in a row and contribute to a large number of wrong answers. I have also found that it usually classifies non-spam messages as spam more often than the other way around. 


III. Setup and Installation:

1. Make sure your requirements are up to date. You can use "pip install -r requirements.txt" in the command line. 
2. Run datacollection.py from the console and follow the instructions to sign in with your Google Account.
3. 

IV. Known Bugs:

1. Predictions can be wrong... a lot, usually they are good though
2. It is very difficult to update the dictionary as it means all the emails have to be recounted
3. Should have used email threads instead of email messages

V. Contact Information:
Yousef Hindy
yhindy@stanford.edu
(203)-979-2569

VI. Special Thanks:
Google & StackOverflow: you two know all the answers
The CS41 teaching staff (especially Sam), for teaching me all I know about Python


