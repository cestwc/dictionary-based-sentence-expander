# To handle some methods according to lexicals
# Due to the different notation used by SpaCy, and nltk, we have to use a few dictionaries to translate them

from itertools import chain

def conditionsAvailToReplace(lexical = None):
	cond = {
    'NOUN':[[('pos','NOUN'), ('dep','nsubj')], [('pos','NOUN'), ('dep', 'dobj')], [('pos','NOUN'), ('dep', 'pobj')]],
    'VERB':[[('pos','VERB'), ('dep','ROOT')], [('pos','VERB'), ('dep', 'pcomp')], [('pos','VERB'), ('dep', 'conj')], [('pos','VERB'), ('dep', 'acl')], [('pos','VERB'), ('dep', 'relcl')]],
    'ADJ':[[('pos','ADJ'), ('dep','amod')], [('pos','ADJ'), ('dep', 'acomp')], [('pos','ADJ'), ('dep', 'pcomp')]],
    'ADV':[[('pos','ADV'), ('dep','advmod')], [('pos','ADV'), ('dep', 'acomp')], [('pos','ADV'), ('dep', 'pcomp')], [('pos','ADV'), ('dep', 'ccomp')], [('pos','ADV'), ('dep', 'oprd')], [('pos','ADV'), ('dep', 'prt')]]
	}
	
	return cond[lexical] if lexical != None else list(chain(*[v for v in cond.values()]))

def posAsInNLTK(lexical):
	pos2nltk = {'NOUN':('n'), 'VERB':('v'), 'ADJ':('s', 'a'), 'ADV':('r')}
	return pos2nltk[lexical]


def acceptedRootPOS(lexical):
	pos2root = {'NOUN':('NOUN'), 'VERB':('VERB'), 'ADJ':('VERB', 'ADP', 'ADJ'), 'ADV':('ADP')}
	return pos2root[lexical]
