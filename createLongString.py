import sys
import os
import re
import pandas as pd

<<<<<<< HEAD
def createLongString(df, text_column, output, punctuation=True):
=======
def createLongString(li_text, text_column, output):
>>>>>>> bd1163bc92d99a0804656454184b279dc09e2338
	
	# Write a txt file with all the strings
	if not os.path.exists('output/'):
		os.makedirs('output/')
	txtfile_full = open('output/longstring_' + output + '.txt', 'w', encoding='utf-8')
	

<<<<<<< HEAD
	for item in df[text_column]:
		if item != 'nan':
			item = str(item).lower()
			if punctuation:
				regex = re.compile('[^a-zA-Z\)\(\.\,\-\n ]')	# includes punctuation and brackets
			else:
				regex = re.compile('[^a-zA-Z\)\(\-\n ]')
			item = regex.sub('', item)
			txtfile_full.write('%s' % item)
=======
	for post in li_text:
		if post != 'nan':
			post = str(post).lower()
			regex = re.compile('[^a-zA-Z\)\(\.\,\-\n ]')	# includes brackets
			post = regex.sub('', post)
			txtfile_full.write('%s' % post)
>>>>>>> bd1163bc92d99a0804656454184b279dc09e2338
		
# show manual if needed
if len(sys.argv) < 2:
	print()
	print("Creates a txt file of a long sequence of a column in a csv.")
	print("Useful to make Word Tree visualisations.")
	print()
	print("Usage: python3 createLongString.py [--source] [--output] [--timespan] [--timecol] [--puct]")
	print()
	print("--source: the relative path to a csv file from 4CAT (e.g. 'data/datasheet.csv').")
	print("--textcol (optional): default 'body'. The text column in the csv. ")
	print("--timespan (optional): default 'days' - if provided, create text files for different timespans. Can be 'days' or 'months'.")
	print("--timecol (optional): default 'timespan' - the csv column in which the time values are stored. Should start with format yyyy-mm-dd.")
	print("--timecol (optional): default 'timespan' - the csv column in which the time values are stored. Should start with format yyyy-mm-dd.")
	print("--punct (optional): defulat true. Whether to keep commas and periods. Use true and false (e.g. '--punct=false') ")
	print()
	print("Example:")
	print("python3 createLongString.py --source=input/datasheet.csv --timespan=days --punct=false")
	print()
	sys.exit(1)

else:
	li_args = []
	source = ''
	output = 'longstring'
	text_column = 'body'
	timespan = False
	time_column = 'timestamp'
	punct = False

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
		elif arg[0:8] == "--punct=":
			punct = arg[8:len(arg)]
			li_args.append(punct)
			if punct == 'true':
				punct = True
			elif punct == 'false':
				punct = False
			else:
				print("Invalid value for punct. Please use true or false (like --punct=true")
				sys.exit(1)
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
<<<<<<< HEAD
			li_input = df_date[text_column].tolist()
			createLongString(df, text_column, output + '_' + date_slice, punct)
			print(str(output) + '_' + date_slice + '.txt created.')
	else:
		createLongString(df, text_column, output, punct)
=======
			li_posts = [text for text in df_date[text_column]]
			print(str(len(li_posts)) + ' posts in ' + date_slice)
			print(str(output) + '_' + date_slice.replace('\/', '-') + '.txt created.')
			createLongString(li_posts, text_column, output + '_' + date_slice)
	else:
		li_posts = [text for text in df[text_column]]
		createLongString(li_posts, text_column, output)
>>>>>>> bd1163bc92d99a0804656454184b279dc09e2338
		print('Done! ' + str(output) + '.txt created.')