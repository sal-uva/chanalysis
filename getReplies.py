import sys
import os
import re
import pandas as pd
from collections import Counter

def getReplies(df, output, top=0, text_column='body', date=''):
	
	# Extract all the mentions from the posts
	print('Counting all >> mentions in the posts...')
	li_posts = df[text_column].tolist()
	li_mentions = []
	for post in li_posts:
		#print(post)
		if type(post) == str:
			reg = re.compile('\>\>[0-9]{7,10}')
			mentions = reg.findall(post)
			li_mentions.append(mentions)
	li_all_mentions = []

	# how to do this in nested for loop?
	for mentions in li_mentions:
		for mention in mentions:
			li_all_mentions.append(mention[2:])
	
	# Rank the mentions
	ranks = Counter(li_all_mentions)
	
	# Add mentions to the dataframe and sort on this column
	print('Adding mentions to a new csv...')
	li_sorted_mentions = [0] * len(df)
	for index, no in enumerate(df['id']):
		for key in ranks.keys():
			#print(type(key), type(no))
			if int(key) == no:
				li_sorted_mentions[index] = ranks[key]
			
	df['mentions'] = li_sorted_mentions
	
	# If only the top n should be returned, slice the DataFrame
	top_label = 'all'
	if top > 0:
		df = df.sort_values(by='mentions', ascending=False)
		df = df[:top]
		top_label = 'top-' + str(top) + '-'

	print('Writing to csv...')
	if not os.path.exists('output/'):
		os.makedirs('output/')
	df.to_csv('output/' + output + '-most-replied-to-' + top_label + date + '.csv', encoding='utf-8')
	print('Done! ' + output + '-most-replied-to-' + top_label + date + '.csv created.')


# Show manual if needed
if len(sys.argv) < 2:
	print()
	print("Counts which posts have been replied to the most.")
	print("Adds a 'replies' column and makes a new csv.")
	print("Use the 'top' parameters to only save the top n replied to posts.")
	print()
	print("Usage: python3 getReplies.py [--source] [--textcol] [--top] [--timespan] [--timecol]")
	print()
	print("--source: the relative path to a csv file from 4CAT (e.g. 'data/datasheet.csv').")
	print("--top  (optional): default 0 - input a number, and if provided, saves the csv only with the top n most replies to posts.")
	print("--textcol  (optional): default 'body' - the csv column with the body texts.")
	print("--timespan (optional): if provided, make separate csvs with the most replied to posts per month or day. Use 'months' or 'days'.")
	print("--timecol (optional): default 'timespan' - the csv column in which the time values are stored. Should start with format yyyy-mm-dd.")
	print()
	print("Example: python getReplies.py --source=input/datasheet.csv --textcol=body --top=50 --timespan=days --timecol=timestamp")
	print()
	sys.exit(1)

else:
	li_args = []
	source = ''
	top = 0
	text_column = 'body'
	time_column = 'timestamp'
	timespan = False

	# Interpret command line arguments
	for arg in sys.argv:
		if arg[0:9] == "--source=":
			source = arg[9:len(arg)]
			output = source[:-4]
			if "/" in output:
				output = output.split("/")
				output = output[len(output) - 1]
			li_args.append(source)
			li_args.append(output)
		elif arg[0:7] == "--text=":
			text_column = arg[7:len(arg)]
			li_args.append(text_column)
		elif "--top=" in arg:
			top = int(arg[6:len(arg)])
			li_args.append(top)
		elif arg[0:11] == "--timespan=":
			timespan = arg[11:len(arg)]
			li_args.append(timespan)
		elif arg[0:10] == "--timecol=":
			time_column = arg[10:len(arg)]
			li_args.append(time_column)

	print(li_args)
	if source == '' or not os.path.isfile(source):
		print("Please provide a valid input file like this: --source=data/datasheet.csv")
		sys.exit(1)

	else:
		df = pd.read_csv(source)

		if timespan == False:
			getReplies(df, output, top=top, text_column=text_column)
		else:
			print('Getting most replied to posts per ' + timespan)
			# Get the dates to make files for
			li_all_dates = df[time_column].tolist()
			if timespan == 'days':
				li_dates = [date[0:10] for date in li_all_dates]
			elif timespan == 'months':
				li_dates = [date[0:7] for date in li_all_dates]
			else:
				print('Please provide a valid date format (\'days\' or \'months\')')
				sys.exit(1)

			li_dates = set(li_dates)
			print('Dates to check: ', li_dates)
			for date_slice in li_dates:
				print('Getting most replied to for ' + date_slice)
				getReplies(df[df[time_column].str.contains(date_slice)], output, top=top, text_column=text_column, date=date_slice)