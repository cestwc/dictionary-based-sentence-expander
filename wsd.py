#synset nltk
def isSynset(syn):
	
	try:
		if syn == None:
			return 0
	except:
		return 1

def wsd(tokens, word, pos = None):
	#lesk nltk
	if pos == None:
		return lesk(tokens, word)
	else:
		i = 0
		syn = None
		while i < len(pos) and not isSynset(syn):
			syn = lesk(tokens, word, pos[i])
			i += 1
		return syn
