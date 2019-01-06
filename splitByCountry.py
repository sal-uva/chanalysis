import sys
import os
import pandas as pd

def splitByCountry(df, country_col, output):
	"""
	Splits a 4CAT csv by its country flags

	"""

	countries_done = []

	if not os.path.exists('output/'):
		os.makedirs('output/')
	if not os.path.exists('output/' + str(output) + '/'):
		os.makedirs('output/' + str(output) + '/')
	for country in df[country_col]:
		if country not in countries_done:
			print('Splitting the file for ' + str(country))
			df_country = df[df[country_col] == country]
			df_country.to_csv('output/' + str(output) + '/' + str(output) + '_' + str(country) + '.csv', encoding='utf-8')
			countries_done.append(country)

	print('Done! Wrote ' + str(len(os.listdir('output/' + str(output) + '/'))) + ' files in "output/' + str(output) + '/"')

# show manual if needed
if len(sys.argv) < 2:
	print()
	print("This script splits a 4CAT csv by its country code.")
	print("Creates a csv per post per country in the folder output/country_csv/.")
	print()
	print("Usage: python3 splitByCountry.py [--source] [--countrycol]")
	print()
	print("--source: the relative path to a csv file from 4CAT (e.g. 'input/obama.csv').")
	print("--countrycol (optional): default 'country_name'. The column with the country name in the csv. ")
	print()
	print("Example:")
	print("python3 splitByCountry.py --source=input/obama.csv --timecol=country_name")
	print()
	sys.exit(1)

else:
	li_args = []
	source = ''
	filename = ''
	country_col = 'country_name'

	# Interpret command line arguments
	for arg in sys.argv:
		if arg[0:9] == "--source=":
			source = arg[9:len(arg)]
			if '/' in source:
				filename = source.split('/')
			print(filename)
			filename = filename[len(filename) - 1]
			filename = filename[:-4]
			li_args.append(source)
			li_args.append(filename)
		elif arg[0:14] == "--country_col=":
			country_col = arg[14:len(arg)]
			li_args.append(country_col)
	print(li_args)
	if source == '' or not os.path.isfile(source):
		print("Please provide a valid input file like this: --source=data/datasheet.csv")
		sys.exit(1)

	df = pd.read_csv(source, encoding='utf-8')
	splitByCountry(df, country_col, filename)