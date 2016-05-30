"""
File: datahandler.py
Author: Yousef Hindy

This file is mainly used for debugging purposes.
It is used to figure out how many emails are in the data set.
"""

def findUniqueEmails(lines):
	used = set([])
	for line in lines:
		used.add(line)
	return len(used)

if __name__ == '__main__':
	with open('data/emaildata.txt', 'r') as f:
		lines = f.readlines()
		ids = [line.split()[0] for line in lines]
		len1 = len(lines)
		print("Number of emails: " + str(len1))
		print("Number of unique email ids: " + str(findUniqueEmails(lines)))