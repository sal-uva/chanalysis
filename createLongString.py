import sys
import os
import re
import pandas as pd

def createLongString(li_text, text_column, output):
	
	# Write a txt file with all the strings
	if not os.path.exists('output/'):
		os.makedirs('output/')
	txtfile_full = open('output/longstring_' + output + '.txt', 'w', encoding='utf-8')
	

	for post in li_text:
		if post != 'nan':
			post = str(post).lower()
			regex = re.compile('[^a-zA-Z\)\(\.\,\-\n ]')	# includes brackets
			post = regex.sub('', post)
			txtfile_full.write('%s' % post)
		
# show manual if needed
if len(sys.argv) < 2:
	print()
	print("Creates a txt file of a long sequence of a column in a csv.")
	print("Useful to make Word Tree visualisations.")
	print()
	print("Usage: python3 createLongString.py [--source] [--output] [--timespan] [--timecol]")
	print()
	print("--source: the relative path to a csv file from 4CAT (e.g. 'data/datasheet.csv').")
	print("--textcol (optional): default 'body'. The text column in the csv. ")
	print("--timespan (optional): default 'days' - if provided, create text files for different timespans. Can be 'days' or 'months'.")
	print("--timecol (optional): default 'timespan' - the csv column in which the time values are stored. Should start with format yyyy-mm-dd.")
	print()
	print("Example:")
	print("python3 createLongString.py --source=input/datasheet.csv --timespan=days")
	print()
	sys.exit(1)

else:
	li_args = []
	source = ''
	output = 'longstring'
	text_column = 'body'
	timespan = False
	time_column = 'timestamp'

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
		elif arg[0:12] == "--textcol=":
			text_column = arg[7:len(arg)]
			li_args.append(text_column)
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

	df = pd.read_csv(source, encoding='utf-8')

	# If a timespan is provided, split the df and run the text module per timespan
	if timespan != False:
		li_all_dates = df[time_column].tolist()
		endstring = 10

		df = df.sort_values(by=[time_column])

		if timespan == 'days':
			endstring = 10
			li_dates = [date[0:endstring] for date in li_all_dates]
		elif timespan == 'months':
			endstring = 7
			li_dates = [date[0:endstring] for date in li_all_dates]
		else:
			print('Please provide a valid date format (\'days\' or \'months\')')
			sys.exit(1)
		df['dates_to_check'] = li_dates
		li_dates = set(li_dates)

		for date_slice in li_dates:
			df_date = df[df['dates_to_check'] == date_slice]
			li_posts = [text for text in df_date[text_column]]
			print(str(len(li_posts)) + ' posts in ' + date_slice)
			print(str(output) + '_' + date_slice + '.txt created.')
			createLongString(li_posts, text_column, output + '_' + date_slice)
	else:
		createLongString(df, text_column, output)
		print('Done! ' + str(output) + '.txt created.')