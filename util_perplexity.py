# To compute perplexity of synthesized sentence string using a language model
# we may have multiple ways to do that, here we use GPT-2 from transformers

import math
import torch

from transformers import OpenAIGPTTokenizerFast, OpenAIGPTModel, OpenAIGPTLMHeadModel

# Load pre-trained model (weights)
model = OpenAIGPTLMHeadModel.from_pretrained('openai-gpt')
model.eval()

# Load pre-trained model tokenizer (vocabulary)
tokenizer = OpenAIGPTTokenizerFast.from_pretrained('openai-gpt')

def score(sentence):
	tokenize_input = tokenizer.tokenize(sentence)
	tensor_input = torch.tensor([tokenizer.convert_tokens_to_ids(tokenize_input)])
	loss=model(tensor_input, labels=tensor_input)
	return math.pow(2, loss[0])
