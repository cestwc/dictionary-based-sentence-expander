import re
import os
import pickle

import nltk
nltk.download("wordnet")
from nltk.corpus import wordnet

import spacy
spacy.prefer_gpu()
from spacy.tokens import DocBin

nlp = spacy.load('en_core_web_trf')
nlp.vocab.vectors = spacy.load('en_core_web_lg').vocab.vectors


bracketRegex = re.compile(r'\([^\(\)]+\)')
semicRegex = re.compile(r';.*')
sbsthRegex = re.compile(r'some\w+$')

def simplify(regexes, gloss):
	
    for regex in regexes:
        gloss = regex.sub('', gloss).strip()
		
    return ' '.join(gloss.split())


def parseWnGlosses(path = '.', redo = False):
	
	directory = os.path.join(path, 'tokenized_glosses.spacy')
	wn = os.path.join(path, 'wn')
	
	if redo or not os.path.exists(directory):
		tokenized_glosses = {}
		for synset in wordnet.all_synsets():
			name = synset.name()
			gloss = simplify([bracketRegex, semicRegex, sbsthRegex], synset.definition())
			tokenized_glosses[name] = nlp(gloss)
		doc_bin_all = DocBin()
		seg = 1000
		for i in range(len(tokenized_glosses)//seg + 1):
			doc_bin = DocBin()
			for doc in list(tokenized_glosses.values())[i*seg:min((i+1)*seg, len(tokenized_glosses))]:
				doc_bin.add(doc)
			doc_bin_all.merge(doc_bin)
		doc_bin_all.to_disk(directory)
		with open(wn, 'wb') as f:
			pickle.dump(list(tokenized_glosses.keys()), f)

	else:
		doc_bin = DocBin().from_disk(directory)
		with open(wn, 'rb') as f:
			wordnames = pickle.load(f)
		tokenized_glosses = dict(zip(wordnames, list(doc_bin.get_docs(nlp.vocab))))
		
	return tokenized_glosses
		
