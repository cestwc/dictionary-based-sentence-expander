import copy
import random

from replicator import doc2root, doc2linear
from util_lexical import conditionsAvailToReplace, posAsInNLTK, acceptedRootPOS
from util_common import commonWords

class ExpandedSent:
	
	def __init__(self, sentence, nlp):
		self.s = sentence
		self.nlp = nlp
		self.doc = sentence #nlp(sentence)
		self.rootstock = doc2root(self.doc)
		self.scion = None
		self.joint = None
		self.syn = None # a specific sense in nltk.corpus wordnet Synset object
		self.gemels = None # from the Latin word meaning "a pair"

	# general (with selection on lexical categories)
	def graft(self, tokenized_glosses, lexical = None):
		candidates = [w for w in self.rootstock.inquire(conditions[lexical]) if w.attr['lemma'] not in commonWords(lexical)]
		if candidates == []:
			return None
		random.seed(42)
		self.joint = random.choice(candidates)
		pos = self.joint.attr['pos']
		syn = wsd(self.rootstock.linear(), '_'.join(self.joint.attr['text'].split()), posAsInNLTK(pos))
		if not isSynset(syn):
			return None
		self.syn = syn
		scion = doc2root(tokenized_glosses[self.syn.name()])
		if scion.attr['pos'] not in acceptedRootPOS(pos):
			return None
		self.scion = scion
		self.rootstock = copy.deepcopy(self.rootstock)
		if pos == 'NOUN':
			self.gemels = self.joint.nounReplace(self.scion)
		elif pos == 'VERB':
			self.gemels = self.joint.verbReplace(self.scion)
		elif pos == 'ADJ':
			self.gemels = self.joint.adjReplace(self.scion)
		else:           #ADV
			self.gemels = self.joint.advReplace(self.scion)
		self.gemels.phraseRetokenize()
		return None


	def show(self):
		if self.gemels == None:
			return 'N/A'
		print(*[self.syn.definition(), self.rootstock.sent(), self.gemels.sent()], sep = '\n')
		displacy.render(self.doc, style='dep', jupyter = True,  options={'distance': 100})
		displacy.render(self.contrast, style='dep', jupyter = True,  options={'distance': 100})

	def evaluate(self):
		if self.gemels == None:
			return None, None, None
		self.contrast = phraseTokenize(self.nlp(self.gemels.sent()))
		contrastLinear = doc2linear(self.contrast)
		gemelLinear = self.gemels.linear()
		difference = [(gemelLinear[i], contrastLinear[i]) for i in range(min(len(gemelLinear), len(contrastLinear))) if not gemelLinear[i].lookLike(contrastLinear[i])]
		return (len(difference), 1 - len(difference) / len(gemelLinear), difference)# if difference != None else (None, None, None)
