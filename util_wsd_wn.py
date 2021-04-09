# To find a correct definition among many definitions in WordNet for a word in a sentence
# we may have multiple ways to do that, here we use lesk algorithm from nltk, though it only gives us around 60% accuracy

from nltk.wsd import lesk

def wsd(listOfWords, word, pos = None):
	if pos == None:
		return lesk(listOfWords, word)
	else:
		i = 0
		syn = None
		while i < len(pos) and not isSynset(syn):
			syn = lesk(listOfWords, word, pos[i])
			i += 1
		return syn

def isSynset(syn):
	
	try:
		if syn == None:
			return 0
	except:
		return 1
