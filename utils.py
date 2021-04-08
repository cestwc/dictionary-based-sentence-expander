import csv
from itertools import chain

def commonWords():
	
	commonWords = {}
	with open('common.csv','r') as f: 
		for line in csv.reader(f): 
			commonWords[line[0]] = [w for w in line[1:] if w != '']
			
	return commonWords

common = list(chain(*[v for v in commonWords().values()]))
