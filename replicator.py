import spacy
spacy.prefer_gpu()

from node import Node

def token2node(t, cols, headNode = None):
	
	rows = [t.text, t.lemma_, t.pos_, t.tag_, spacy.explain(t.pos_), t.dep_, t.morph.to_dict(), t.is_stop, t.n_lefts, t.n_rights]
	n = Node()
	n.setAttr(dict(zip(cols, rows)))
	n.setHead(headNode)
	n.dominate([[token2node(x, cols, n) for x in t.lefts], [token2node(x, cols, n) for x in t.rights]])
	return n

def doc2root(doc):
	cols = ('text', 'lemma', "pos", "tag", "explain", "dep", "morph", "stop", "nlefts", "nrights")
	for t in doc:
		if t == t.head:
			return token2node(t, cols)

def doc2linear(doc):
	linear = [Node() for i in range(len(doc))]
	cols = ('text', 'lemma', "pos", "tag", "explain", "dep", "morph", "stop", "nlefts", "nrights")
	for i in range(len(linear)):
		t = doc[i]
		rows = [t.text, t.lemma_, t.pos_, t.tag_, spacy.explain(t.pos_), t.dep_, t.morph.to_dict(), t.is_stop, t.n_lefts, t.n_rights]
		linear[i].setAttr(dict(zip(cols, rows)))
		if t != t.head:
			linear[i].setHead(linear[t.head.i])
		linear[i].dominate([[linear[x.i] for x in t.lefts], [linear[x.i] for x in t.rights]])
	return linear

# merge tokens that form a collocation
from util_phrase import isPhrase

def phraseTokenize(doc):
	spans = []
	i = 0
	while i < len(doc):
		n = min(5, len(doc)-i)
		while isPhrase(doc[i:i+n].lemma_.split()) == 0 and n >= 2:
			n -= 1
		if n >= 2:
			spans.append(doc[i:i+n])
		i += n
	with doc.retokenize() as retokenizer:
		for span in spans:
			retokenizer.merge(span)
	return doc
