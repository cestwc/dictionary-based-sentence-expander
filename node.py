from pyinflect import getInflection

from util_phrase import isPhrase

class Node:

	def __init__(self):
		# the token head
		self.head = None
		# children
		self.children = [[],[]]
		# node's data frame
		self.attr = None

	def __repr__(self):
		return self.attr['text']

	def __str__(self):
		return self.attr['text']

	# show the tree under this node as a list
	def linear(self):
		return list( chain( *[x.linear() for x in self.children[0]] + [[self]] + [x.linear() for x in self.children[1]]))

	# adjust nodes if two or more form a known phrase
	def phraseRetokenize(self):
		doc = self.linear()
		spans = []
		i = 0
		while i < len(doc):
			n = min(5, len(doc)-i)            
			while isPhrase([x.attr['lemma'] for x in doc[i:i+n]]) == 0 and n >= 2:
				n -= 1
			if n >= 2:
				spans.append(doc[i:i+n])
			i += n
		for span in spans:
			depths = [x.getDepth() for x in span]
			remain = depths.index(min(depths))
			span[remain].attr['text'] = ' '.join([x.attr['text'] for x in span])
			span[remain].attr['lemma'] = ' '.join([x.attr['lemma'] for x in span])
			for i in range(len(span)):
				if i != remain:
					span[i].head.drop(span[i])
		return None

	# get the depth of self (node)
	def getDepth(self):
		if self.head == None:
			return 0
		else:
			return 1 + self.head.getDepth()

	# get the text of head node
	def getHeadText(self):
		if self.head != None:
			return self.head.attr['text']
		else:
			return None

	# find the root of the current node
	def getRoot(self):
		if self.head == None:
			return self
		else:
			return self.head.getRoot()

	# get the side where it belongs to its head
	def getSide(self):
		return [i for i in range(2) if self in self.head.children[i]][0] if self.head != None else None

	# get index among siblings
	def getIndex(self):        
		return self.head.children[self.getSide()].index(self) if self.head != None else None

	# assign / change head
	def setHead(self, node):
		self.head = node
		return 0

	# assign / change children
	def dominate(self, children):
		self.children = children
		return 0

	# assign / change data frame
	def setAttr(self, attr):
		self.attr = attr
		return 0

	# insert a child node to self (node)
	def insert(self, node, side = 0, index = 0):
		if node != None:
			node.setHead(self)
			self.children[side].insert(index, node)
		return 0

	# drop a child node
	def drop(self, node):
		del self.children[node.getSide()][node.getIndex()]
		node.setHead(None)
		return 0

	# replace self (node) with a given node
	def replace(self, node):
		node.attr['dep'] = self.attr['dep']
		if self.head != None:
			self.head.insert(node, self.getSide(), self.getIndex())
			self.head.drop(self)
		return node.getRoot()

	# find a list of nodes under the root node, each element in which matches the condition
	def inquire(self, condition):
		return [n for n in self.linear() if any([all([n.attr[u[0]] == u[1] for u in r])for r in condition for u in r])]

	# sentence in string
	def sent(self):
		return ' '.join([n.attr['text'] for n in self.linear()])

	# compare dependency with a node
	def lookLike(self, node):
		return self.getHeadText() == node.getHeadText() and self.attr['dep'] == node.attr['dep']

	# transfer children from self (node) to a given node
	def simpleChildrenTransferTo(self, node):
		node.children[0][0:0] = self.children[0]
		node.children[1] += self.children[1]
		for y in node.children:
			for z in y:
				z.setHead(node)
		return None

	### specific methods for verbs, nouns, adjectives, and adverbs are as follows
	#noun
	def detDeduplicate(self):
		det = 0
		i = 0
		while i < len(self.children[0]):
			if self.children[0][i].attr['dep'] in ('det', 'poss'):
				if det == 0:
					self.children[0].insert(0, self.children[0].pop(i))
					det = 1
				else:
					self.drop(self.children[0][i])
					i -= 1
			i += 1
		return None

	#noun
	def nounInflect(self, morph): #self.joint.attr['morph']
		if morph['Number'] == 'Plur':
			for c in self.children[0]:
				if c.attr['pos'] == 'DET':
					self.drop(c)
			self.attr['text'] = getInflection(self.attr['text'], 'NNS', inflect_oov=True)[0]
		return None

	#noun
	def nounReplace(self, node):
		node.nounInflect(self.attr['morph'])
		self.simpleChildrenTransferTo(node)
		node.detDeduplicate()
		return self.replace(node)


	#verb
	def verbInflect(self, morph):
		morph = {**{'Tense':'', 'Aspect':'', 'Person':'', 'Number':''}, **morph}
		start = self.linear()[0]
		if start.attr['text'] == 'to':
			self.drop(start)
			start = self.linear()[0]
		hasAUX = 0
		for n in self.children[0]:
			if n.attr['pos'] == 'AUX':
				hasAUX = 1
				n.verbInflect(morph)
		if hasAUX == 0:
			text = self.attr['text'].split()
			if morph['Tense'] == 'Pres':
				if morph['Aspect'] == 'Prog':
					text[0] = getInflection(text[0], 'VBG', inflect_oov=True)[0]
				if morph['Number'] == 'Sing' and morph['Person'] in ('Three' or '3'):
					text[0] = getInflection(text[0], 'VBZ', inflect_oov=True)[0]
			elif morph['Tense'] == 'Past':
				if morph['Aspect'] == 'Perf':
					text[0] = getInflection(text[0], 'VBN', inflect_oov=True)[0]
				else:
					text[0] = getInflection(text[0], 'VBD', inflect_oov=True)[0]
			self.attr['text'] = ' '.join(text)
		for n in self.children[1]:
			if n.attr['pos'] == 'VERB' and n.attr['dep'] == 'conj':
				n.verbInflect(morph)
		return None

	#verb (if this VERB or ADP is transitive)
	def isTransitive(self):
		if not any([sc.attr['dep'] in ('dobj', 'pobj', 'conj') for sc in self.children[1]]):
			if self.attr['pos'] == 'ADP':
				return True
			elif self.attr['pos'] == 'VERB':
				if self.attr['dep'] == 'conj':
					if self.head.attr['dep'] in ('ROOT', 'pcomp', 'xcomp'):
						return True
				elif self.attr['dep'] in ('ROOT', 'pcomp', 'xcomp'):
					return True
		return False

	#verb
	def verbReplace(self, node):
		node.verbInflect(self.attr['morph'])
		transitives = [x for x in node.linear() if x.isTransitive()]
		if transitives == []:
			if self.children[1] != []:
				if self.children[1][0].attr['dep'] in ('dobj', 'pobj'):                    
					dummyADP = Node()
					dummyADP.setAttr({'text':'to', 'lemma':'to', 'dep':'prep', 'pos':'ADP'})
					self.children[1][0].setHead(dummyADP)
					self.children[1][0].attr['dep'] = 'pobj'
					dummyADP.insert(self.children[1][0], 1, 0)
					self.children[1][0] = dummyADP
			self.simpleChildrenTransferTo(node)
			return self.replace(node)
		k = 0
		for sc in self.children[1]:
			if sc.attr['dep'] in ('dobj', 'pobj') and k < 1:# and len(sc.linear()) < sum([len(x.linear()) for x in transitives[-1].children[1]]) + 19:
				transitives[-1].insert(sc, 1, 0)
				k += 1
			else:
				node.insert(sc, 1, len(node.children[1]))            
		node.children[0][0:0] = self.children[0]
		for z in node.children[0]:
			z.setHead(node)
		return self.replace(node)




	#adj
	def adjReplace(self, node):
		head = self.head
		while head.attr['dep'] == 'compound':
			head = head.head
		for c in reversed(self.children[0]):
			if c.attr['dep'] == 'amod':
				self.drop(c)
				head.insert(c, self.getSide(), self.getIndex())
				head.detDeduplicate()
		self.simpleChildrenTransferTo(node)

		if self.attr['dep'] in ('acomp', 'pcomp'):
			return self.replace(node)
		else: # amod
			node.attr['dep'] = 'acl' if node.attr['pos'] == 'VERB' else 'amod' if node.attr['pos'] == 'ADJ' else 'prep'
			head.insert(node, 1, 0)
			self.head.drop(self)
			return node.getRoot()

	#adv
	def advReplace(self, node):
		head = self.head
		while head.attr['dep'] == 'compound':
			head = head.head
		for c in reversed(self.children[0]):
			if c.attr['dep'] == 'advmod':
				self.drop(c)
				head.insert(c, self.getSide(), self.getIndex())
		self.simpleChildrenTransferTo(node)

		node.attr['dep'] = 'prep'
		if self.getSide() == 1:
			head.insert(node, 1, self.getIndex())
		elif head.attr['pos'] == 'VERB' and head.children[1] != [] and head.children[1][0].attr['dep'] in ('dobj', 'pobj'):
			head.insert(node, 1, 1)
		else:
			head.insert(node, 1, 0)

		self.head.drop(self)
		return node.getRoot()
