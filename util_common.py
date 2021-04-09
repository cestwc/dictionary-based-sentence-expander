# to obtain a list of common words in English
# we may have multiple ways to do that, here we use a hardcoded word list 'common.csv'

import csv
from itertools import chain

def commonWords(lexical = None):
	
	commonWords = {}
	with open('common.csv','r') as f: 
		for line in csv.reader(f): 
			commonWords[line[0]] = [w for w in line[1:] if w != '']
			
	return commonWords[lexical] if lexical != None else list(chain(*[v for v in commonWords.values()]))
