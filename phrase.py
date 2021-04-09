# to determine whether a given list of strings form one phrase or collocation
# we may have multiple ways to do that, here we use vocabulary in WordNet as a pool of phrases.

def isPhrase(listOfWords):
	
	return inWordnet(listOfWords)


from nltk.corpus import wordnet

wnLemmas = set(wordnet.all_lemma_names())

def inWordnet(listOfWords):
	
	for conn in ['_', '-']:
		ngram = conn.join(listOfWords)
		if ngram in wnLemmas:
			return 1
		
	return 0
