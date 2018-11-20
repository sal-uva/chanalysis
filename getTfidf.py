import sys
import os
import pandas as pd
import pickle as p
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

def no_tokenizer(doc):
	return doc

def getTfidf(li_tokens, li_filenames, filename, min_df=0, max_df=0, top_n=25):
	"""
	Creates a csv with the top n highest scoring tf-idf words.

	:param input,		list of tokens. Should be unpickled first
	:param filename,	the name of the output folder, based on the input
	:param max_df,		sklearn TfidfVectorizer function to filter words that appear in all token lists
	:

	"""

	# Create an output folder if it doesn't exist yet
	if not os.path.exists('output/'):
		os.makedirs('output/')
	if not os.path.exists('output/tfidf/'):
		os.makedirs('output/tfidf/')
	if min_df == 0:
		min_df = len(li_tokens)
	else:
		min_df = len(li_tokens) - min_df
		print('Terms must appear in at least ' + str(min_df) + ' of the total ' + str(len(li_tokens)) + ' files.')
	if max_df == 0:
		max_df = len(li_tokens)
	else:
		max_df = len(li_tokens) - max_df
		print('Terms may not appear in ' + str(max_df) + ' of the total ' + str(len(li_tokens)) + ' files.')

	output = 'output/tfidf/' + filename + '_tfidf.csv'

	print('Vectorizing!')
	tfidf_vectorizer = TfidfVectorizer(min_df=min_df, max_df=max_df, analyzer='word', token_pattern=None, tokenizer=lambda i:i, lowercase=False)
	tfidf_matrix = tfidf_vectorizer.fit_transform(li_tokens)
	#print(tfidf_matrix[:10])

	feature_array = np.array(tfidf_vectorizer.get_feature_names())
	tfidf_sorting = np.argsort(tfidf_matrix.toarray()).flatten()[::-1]
	
	# Print and store top n highest scoring tf-idf scores
	top_words = feature_array[tfidf_sorting][:top_n]
	#print(top_words)

	weights = np.asarray(tfidf_matrix.mean(axis=0)).ravel().tolist()
	df_weights = pd.DataFrame({'term': tfidf_vectorizer.get_feature_names(), 'weight': weights})
	df_weights = df_weights.sort_values(by='weight', ascending=False).head(100)
	#df_weights.to_csv(output[:-4] + '_top100_terms.csv')
	#print(df_weights.head())

	df_matrix = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf_vectorizer.get_feature_names())
	
	# Turn the dataframe 90 degrees
	df_matrix = df_matrix.transpose()
	#print('Amount of words: ' + str(len(df_matrix)))
	
	print('Writing tf-idf vector to csv')

	# Do some editing of the dataframe
	df_matrix.columns = li_filenames
	cols = df_matrix.columns.tolist()
	cols = li_filenames

	df_matrix = df_matrix[cols]
	#df_matrix.to_csv(output[:-4] + '_matrix.csv')
	
	df_full = pd.DataFrame()

	print('Writing top ' + str(top_n) + ' terms per token file to "' + output[:-4] + '_full.csv"')
	# Store top terms per doc in a csv
	for index, doc in enumerate(df_matrix):
		df_tim = (df_matrix.sort_values(by=[doc], ascending=False))[:top_n]
		df_timesep = pd.DataFrame()
		df_timesep[doc] = df_tim.index.values[:top_n]
		df_timesep['tfidf_score_' + str(index + 1)] = df_tim[doc].values[:top_n]
		df_full = pd.concat([df_full, df_timesep], axis=1)

	df_full.to_csv(output[:-4] + '_full.csv')

	print('Writing a Rankflow-proof csv to "' + output[:-4] + '_rankflow.csv"')
	df_rankflow = df_full
	#df_rankflow = df_rankflow.drop(df_rankflow.columns[0], axis=1)
	
	cols = df_rankflow.columns
	for index, col in enumerate(cols):
		#print(col)
		if 'tfidf' in col:
			li_scores = df_rankflow[col].tolist()
			vals = [int(tfidf * 100) for tfidf in li_scores]
			df_rankflow[col] = vals

	df_rankflow.to_csv(output[:-4] + '_rankflow.csv', encoding='utf-8', index=False)

	print('Done!')

# show manual if needed
if len(sys.argv) < 2:
	print()
	print("Creates a csv file of a tf-idf results.")
	print("Use getTokens.py first to get a folder with tokens which this script can then use.")
	print()
	print("Usage: python3 getTfidf.py [--source] [--min_count] [--min_df] [--max_df] [--top]")
	print()
	print("--source: the relative path to a folder containing tokens created with getTokens (e.g. 'output/obama_tokens/').")
	print("--max_df (optional): filters out the terms that appear less than this amount in one token file.\n E.g. --min_count=50 will delete all the words that appear less than 50 times in the month/week.")
	print("--max_df (optional): filters out the terms that appear in less than this amount.\nE.g. with tokens from 12 months, --min_df=5 will mean terms must appear in 5 months.")
	print("--max_df (optional): filters out the terms that appear in all documents.\nE.g. with tokens from 12 months, --max_df=1 will mean terms can only appear in 11 months.")
	print("--top (optional): default 25. the amount of terms to keep in the csv.")
	print()
	print("Example:")
	print("python3 getTfidf.py --source=data/obama_tokens/ --max_df=1 --top=50")
	print()
	sys.exit(1)

else:
	li_args = []
	source = ''
	min_count = 0
	max_df = 0
	min_df = 1
	top = 25

	# Interpret command line arguments
	for arg in sys.argv:
		if "--source=" in arg:
			source = arg[9:len(arg)]
			li_args.append(source)

			if not source.endswith('/'):
				source = source + '/'

			# Use the folder name as the filename for the tokens
			filename = str(source).split('/')
			filename = filename[len(filename) - 2]
			li_args.append(filename)
		elif "--min_count=" in arg:
			min_count = int(arg[12:len(arg)])
			li_args.append(min_count)
		elif "--max_df=" in arg:
			max_df = int(arg[9:len(arg)])
			li_args.append(max_df)
		elif "--min_df=" in arg:
			min_df = int(arg[9:len(arg)])
			li_args.append(min_df)
		elif "--top=" in arg:
			top = int(arg[6:len(arg)])
			li_args.append(top)

	print(li_args)
	if source == '' or not os.path.isdir(source):
		print("Please provide a valid input file like this: --source=output/obama_tokens/")
		sys.exit(1)

	li_tokens = []
	li_filenames = []
	di_counts = {}

	# Unpickle the tokens
	for index, file in enumerate(os.listdir(source)):
		if file.endswith('.p'):
			li_filenames.append(file)
			token_filename = source + file
			tokens = p.load(open(token_filename, 'rb'))
			# Make a flat list of tokens for the full document
			time_tokens = []

			for tokenlist in tokens:
				#print(tokenlist)
				words = set(tokenlist)
				#print(words)
				for word in words:
					time_tokens.append(word)

					# Keep track of how many times the word is used
					if word not in di_counts:
						di_counts[word] = 1
					else:
						di_counts[word] = di_counts[word] + 1
			
			li_tokens.append(time_tokens)
			
			#tokens = [token for tokenlist in tokens for token in tokenlist]
			#li_tokens.append(tokens)

	print('Files to compare and get tf-idf terms for:')
	print(li_filenames)

	#print(di_counts[:10])
	# Get rid of rarely used terms
	print('Deleting words that appeared less than ' + str(min_count) + ' times')
	if min_count != 0:
		li_frequent_tokens = []
		for index, all_tokens in enumerate(li_tokens):
			frequent_tokens = []
			for single_token in all_tokens:
				if di_counts[single_token] >= min_count:
					frequent_tokens.append(single_token)
			li_frequent_tokens.append(frequent_tokens)
			print(str(len(frequent_tokens)) + ' terms in file ' + str(index + 1) + ' used more than ' + str(min_count) + ' times.')
		
		li_tokens = li_frequent_tokens

	print('Getting tf-idf terms for the following token files:')
	print(li_filenames)

	getTfidf(li_tokens, li_filenames, filename, min_df=min_df, max_df=max_df, top_n=top)