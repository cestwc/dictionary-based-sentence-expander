# To find a correct definition among many definitions in WordNet for a word in a sentence
# we may have multiple ways to do that, here we use lesk algorithm from nltk, though it only gives us around 60% accuracy

from nltk.wsd import lesk

def wsd(listOfWords, word, pos = None):
	
	if pos == None:
		syn = lesk(listOfWords, word)
		return [syn] if isSynset(syn) else []
	else:
		syns = []
		for x in pos:
			syn = lesk(listOfWords, word, x)
			if isSynset(syn):
				syns.append(syn)
		return syns

def isSynset(syn):
	
	try:
		if syn == None:
			return 0
	except:
		return 1
