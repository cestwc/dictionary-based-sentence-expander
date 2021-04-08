# dictionary-based-sentence-expander
Given a sentence, find a word and replace it using its dictionary definition

We have not fully verified how useful this entire project is, but technically, we managed to rewrite a sentence into a longer one (more wordy one).

To complete this task, there are a few steps required. First, we need to find a dictionary, and the one we use here is [WordNet](https://wordnet.princeton.edu/), and more specifically, the [nltk](https://pypi.org/project/nltk/) version. Then we need to know the syntax or constituent of each definition, as it isn't as straightforward as just replacing the word with a long chunk of text. You may suppose this to happen if a word is directly replaced. "This is an old house." --> "This is an 'having lived for a long' time house."

### Dependency Parsing
We use the most accurate [SpaCy](https://spacy.io/usage/facts-figures#comparison-features) dependency parser to analyze each definition / gloss (we may interchangeably use 'definition' and 'gloss' in the following explanation). This helps us understand how people define a word. For example, a noun is usually defined in a noun phrase, while an adjective is usually defined in a verb phrase. The table below shows relationship between the part-of-speech (POS) tag of a word and the POS tag of the root word of its definition. <-- I know, this is a bit wordy itself. The column names are the POS tags of the defined words, and the row names are the POS tags of the root words in the definitions.

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

Since the notation in WordNet and SpaCy for POS tag are different, we keep them as what they are. **s** as column name indicates 'ADJECTIVE SATELLITE' and **r** adverbs.

We noticed that majority or words are nouns and verbs, and we do see a pattern about what phrases are used to define which kind of words. Thus, we decided to work on the 10 most frequent relationships, i.e., n -> NOUN, a -> VERB, a -> ADP, s -> VERB, r -> ADP, etc., which accounts for over 90 percent of the vocabulary. Of course, we cleaned up the glosses a bit before input them to the parser. These cleanings are mainly about getting rid of content in parentheses.

In practice, we need to preparse the glosses and store them as a separate file, as we will still be using them when expanding the sentences. There are some small tricks done, to avoid taking too much memory (you can't have a very big SpaCy [DocBin](https://spacy.io/api/docbin#_title)). We do similar tricks to the sentences in the corpus we are expanding. Though we can process one sentence after another, preprocessing them together saves a lot of time.

### Word selection
Now that we have both tokenized (parsed) glosses and one (or more) tokenized sentence(s), we need to pick a word and replace it with its definition.
