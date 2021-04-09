# dictionary-based-sentence-expander
Given a sentence, find a word and replace it using its dictionary definition

We have not fully verified how useful this entire project is, but technically, we managed to rewrite a sentence into a longer one (more wordy one).

To complete this task, there are a few steps required. First, we need to find a dictionary, and the one we use here is [WordNet](https://wordnet.princeton.edu/), and more specifically, the [nltk](https://pypi.org/project/nltk/) version. Then we need to know the syntax or constituent of each definition, as it isn't as straightforward as just replacing the word with a long chunk of text. You may suppose this to happen if a word is directly replaced. "This is an old house." --> "This is an 'having lived for a long' time house."

### Dependency Parsing
We use the most accurate [spaCy](https://spacy.io/usage/facts-figures#comparison-features) dependency parser to analyze each definition / gloss (we may interchangeably use 'definition' and 'gloss' in the following explanation). This helps us understand how people define a word. For example, a noun is usually defined in a noun phrase, while an adjective is usually defined in a verb phrase. The table below shows relationship between the part-of-speech (POS) tag of a word and the POS tag of the root word of its definition. <-- I know, this is a bit wordy itself. The column names are the POS tags of the defined words, and the row names are the POS tags of the root words in the definitions.

|       |    a |    s |    r |     n |     v |
|------:|-----:|-----:|-----:|------:|------:|
|  VERB | 3627 | 6354 |  221 |  3349 | 11586 |
|  DET  |    1 |    6 |    4 |  1594 |     0 |
|  ADJ  | 1053 | 2825 |   50 |   544 |   316 |
|  NOUN |  155 |  405 |   57 | 73527 |  1739 |
| CCONJ |    0 |    0 |    0 |    24 |     0 |
| PUNCT |    0 |    1 |    0 |     6 |     0 |
|  PART |    0 |    5 |    4 |     4 |     6 |
|  ADV  |   10 |   84 |  235 |    37 |    52 |
|  ADP  | 2615 |  972 | 3019 |   222 |    29 |
|  AUX  |    5 |    5 |    4 |   108 |     1 |
|  PRON |    0 |    3 |    2 |  1516 |     1 |
| SCONJ |    4 |   10 |   14 |     3 |    10 |
| PROPN |    0 |    6 |    0 |   534 |    15 |
|   X   |    2 |    2 |    2 |    16 |    19 |
|  NUM  |    1 |   16 |    8 |   658 |     0 |
|  INTJ |    1 |    1 |    3 |    13 |    12 |
|  SYM  |    0 |    0 |    0 |     0 |     0 |

Since the notation in WordNet and spaCy for POS tag are different, we keep them as what they are. **s** as column name indicates 'ADJECTIVE SATELLITE' and **r** adverbs.

We noticed that majority or words are nouns and verbs, and we do see a pattern about what phrases are used to define which kind of words. Thus, we decided to work on the 10 most frequent relationships, i.e., n -> NOUN, a -> VERB, a -> ADP, s -> VERB, r -> ADP, etc., which accounts for over 90 percent of the vocabulary. Of course, we cleaned up the glosses a bit before input them to the parser. These cleanings are mainly about getting rid of content in parentheses.

In practice, we need to preparse the glosses and store them as a separate file, as we will still be using them when expanding the sentences. There are some small tricks done, to avoid taking too much memory (you can't have a very big spaCy [DocBin](https://spacy.io/api/docbin#_title)). We do similar tricks to the sentences in the corpus we are expanding. Though we can process one sentence after another, preprocessing them together saves a lot of time. ```parse.py``` essentially serves to parse your dictionary (WordNet) or corpus. After parsing your corpus, a generator object is returned, while after parsing the dictionary, a list object is returned.

### Make the containers modifiable
Now we have tokenized out glosses and sentences, and both are in spaCy ```Doc``` format, a container of ```Token``` instances. This format, however, is not modifiable. So we need a helper class ```Node```, and a list of ```Node```s, in order to modify our sentences. We have a ```node.py```, which essentially handles all linguistic features here. ```replicator.py``` is used to bridge from spaCy objects to our customized objects.

### Word selection
Now that we have both tokenized (parsed) glosses and one (or more) tokenized sentence(s), we need to pick a word and replace it with its definition. There are two main categories that we want to avoid replacing. One is the most common words, like 'old', and the other is collocations and compounds. These are handled in the utility files.

### Word-gloss exchange
This is the core part of this project, but ... it is too long to explain here, you may check ```node.py``` if you are interested. There are too many miscellaneous tricks.

### Evaluate the synthesized sentence
We use two methods to evaluate how good a formed sentence looks like. The first is to take a language model and check its perplexity; the second is simply to run the dependency parser again, and see how many dependencies are different. (I know, a bit unclear here)

## Usage
The usage is pretty simple, though the main code looks like many patches. You need to install a few packages before running
```
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_trf
pip install pyinflect
```
We will tell you now why you need two language models. The transformer model of spaCy somehow does not have a vocabulary set!
```python
import spacy
spacy.prefer_gpu()

nlp = spacy.load('en_core_web_trf')
nlp.vocab.vectors = spacy.load('en_core_web_lg').vocab.vectors
```
load your corpus
```python
import json
with open('sample.json', 'r') as f:
	corpus = json.load(f)
```
Then the rest are pretty simple
```python
from parse import parseCorpus, parseWnGlosses
tokenized_glosses = parseWnGlosses()
parsedCorpus = parseCorpus(corpus)

from grafter import ExpandedSent
from util_perplexity import score

count = 0
e_sum = 0
a_sum = 0
err_list = []
syn_list = []
perplexityRootstock = 0
perplexityGemels = 0

for sent in parsedCorpus:
	es = ExpandedSent(sent, nlp)
	es.graft(tokenized_glosses)
	es.moreGraft(tokenized_glosses, 3) # three more times, if you want

	if es.gemels != None: # sometimes, you may fail to find a proper word in a sentence to replace
		syn_list.append(es.syn.name())
		count += 1

		perplexityRootstock += score(es.rootstock.sent())
		perplexityGemels += score(es.gemels.sent())

	error, accuracy, _ = es.evaluate()
	if error != None:
		err_list.append(error)
		syn_list.append(es.syn.name())
		e_sum += error
		a_sum += accuracy

print(count, "%.2f" % (e_sum / count), "%.2f" % (a_sum / count), "%.2f" % (perplexityRootstock/count), "%.2f" % (perplexityGemels/count))
```
Now you have the statistics of your expanded sentences. You can even see how they look like by using ```es.show()```. This command prints the gloss, the original sentence and the expanded sentence. It also plots the dependency for both sentences using [displaCy](https://spacy.io/usage/visualizers).

You may even want to know how many distinct words have been replaced. Try this
```python
from collections import Counter
print(Counter(err_list))

import statistics
print("error median: ", statistics.median(err_list))
print("replaced vocab: ", len(set(syn_list)))
print(Counter(syn_list))
```

## Afterword
Expanding a sentence with rules may look like a challenging task. However, if we view it from another perspective, it may help us write sentences more concisely!
