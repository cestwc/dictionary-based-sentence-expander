import csv
from itertools import chain
from nltk.corpus import wordnet

def commonWords():
	
	commonWords = {}
	with open('common.csv','r') as f: 
		for line in csv.reader(f): 
			commonWords[line[0]] = [w for w in line[1:] if w != '']
			
	return commonWords

wnLemmas = set(wordnet.all_lemma_names())

def inWordnet(listOfWords):
	
    for conn in ['_', '-']:
        ngram = conn.join(listOfWords)
        if ngram in wnLemmas:
            return True
    return False

common = list(chain(*[v for v in commonWords().values()]))
