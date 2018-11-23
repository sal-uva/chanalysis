import sys
import os
import io
import sqlite3
import pandas as pd
import urllib.request, json
import time
import hashlib
import base64
import datetime
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
   'Accept-Encoding': 'none',
   'Accept-Language': 'en-US,en;q=0.8',
   'Connection': 'keep-alive'}

def getImages(li_hashes, li_timestamps, li_counts, top=0, date='', output=''):
	"""
	Uses a image hash list to download corresponding images from 4plebs or 4CAT.
	If an image download fails, it stores it in "failed_hashes.csv"

	"""

	li_failedimgs = []
	timetosleep = 8

	# Timestamp of when the 4CAT started saving images
	time_4cat = 1541462400

	if top > 0:
		print('Only downloading the top ' + str(top) + ' most used images.')

	# Make folder for images
	if os.path.exists('output/') == False:
		os.makedirs('output/')
	if os.path.exists('output/images/') == False:
		os.makedirs('output/images/')
	if output != '':
		if not output.endswith('/'):
			output = output + '/'
		if os.path.exists('output/images/' + output) == False:
			os.makedirs('output/images/' + output)
	
	fetched_4cat = False

	for index, img_hash in enumerate(li_hashes):
		print('Attempting to fetch image ' + str(index + 1) + '/' + str(len(li_hashes)) + ' with hash ' + str(img_hash))
		
		img_time = datetime.datetime.strptime(li_timestamps[index], '%Y-%m-%d %H:%M:%S').timestamp()
		imagefile = False

		# Add a label for the counts for the ultimate filename
		top_label = ''
		if top > 0:
			top_label = '_' + str(li_counts[index])

		# Query 4CAT > 4plebs > Fireden
		# Try 4CAT if the timestamp is later than 5 November 2018
		if img_time > 1541410728:
			imagefile = get4CATImg(img_hash)
			fetched_4cat = True
		
		# If this failed, try 4plebs by searching through all its boards
		if imagefile == False:
			imagefile = get4plebsImg(img_hash)

		# If this still failed, try Fireden by searching through all its boards
		if imagefile == False:
			imagefile = getFiredenImg(img_hash)

		# If the request *still* failed, give up and add it to the failed images
		if imagefile == False:
			li_failedimgs.append(img_hash)
			df_failedimgs = pd.DataFrame()
			df_failedimgs['failed_hashes'] = li_failedimgs
			df_failedimgs.to_csv('output/images/' + output + 'failed-hashes.csv', mode='w', encoding='utf-8')
			print(str(len(li_failedimgs))+ '/' + str(len(li_hashes)) + ' failed images')

		else:
			# If the image was fetched, save it
			if imagefile != False and imagefile != 'webm':
				md5 = hashlib.md5()
				md5.update(base64.b64decode(str(img_hash)))
				imagefile.save('output/images/' + output + md5.hexdigest() + '_' + date + top_label + '.' + imagefile.format)
				print('Image saved at ' + 'output/images/' + output + md5.hexdigest() + '_' + date + top_label  + '.' + imagefile.format)

		if fetched_4cat:
			# Sleep less when the image was fetched from 4CAT
			print('sleeping for ' + str(1) + ' seconds...')
			time.sleep(1)
		else:
			# Sleep more when the image was fetched from 4plebs or Fireden, considering their limits
			print('sleeping for ' + str(timetosleep) + ' seconds...')
			time.sleep(timetosleep)

	print('Finished! ' + str(len(li_hashes) - len(li_failedimgs)) + ' images downloaded, ' + str(len(li_failedimgs)) + ' images failed.')

def get4CATImg(img_hash):
	"""
	Attempts to download an image from the 4CAT database
	
	"""
	print('Attempting to get image from 4CAT')

	# Hash should be changed to hexademical
	md5 = hashlib.md5()
	md5.update(base64.b64decode(img_hash))
	url_4cat = 'http://4cat.oilab.nl/api/image/' + md5.hexdigest()

	print('Requesting ' + url_4cat)
	request = urllib.request.Request(url_4cat, headers=headers)

	try:
		response = urllib.request.urlopen(request)
	except urllib.error.HTTPError as http_error:
		print('No corresponding image in the 4CAT archive')
		print(http_error)
		return False
	else:
		print('Image found in 4CAT database.')
		img = io.BytesIO(response.read())

		if '.webm' in img:
			print('Video file - discarding and adding to failed_hashes.csv')
			return False
		else:
			img = Image.open(img)
			return img

	return False

def get4plebsImg(img_hash):
	"""
	Attempts to download an image from 4plebs

	"""

	url_4plebs = 'https://archive.4plebs.org/_/search/image/' + img_hash.replace('/', '_')
	request = urllib.request.Request(url_4plebs, headers=headers)
	print('Attempting to get image from 4plebs')
	print('with ' + url_4plebs)
	
	#check if the thread is still active on 4plebs
	try:
		response = urllib.request.urlopen(request)

	#some threads get deleted and return a 404
	except urllib.error.HTTPError as httperror:
		print('HTTP error when requesting thread')
		print('Reason:', httperror.code)
		return False

	else:
		html = response.read()
		soup = BeautifulSoup(html, features="lxml")
		image_url = soup.findAll('a', {'class': 'thread_image_link'})
		
		# Request can be empty, or a timeout can occur. In this case, try Fireden instead.
		if image_url:
			image_url = image_url[0]['href']
		else:
			return False
		
		if '.webm' in image_url:
			print('Video file - discarding and adding to failed_hashes.csv')
			return False

		try:
			img_response = urllib.request.urlopen(image_url)
		except urllib.error.HTTPError as httperror:
			print('HTTP error when requesting image from 4plebs')
			print('Reason:', httperror.code)
		except ConnectionResetError as conn_error:
			print('Connection closed by 4plebs. Skipping image.')
			return False
		else:
			imagefile = io.BytesIO(img_response.read())

			if '.webm' not in imagefile:
				# Open and return the image
				image = Image.open(imagefile)
				return image

			else:
				print('Video file - discarding and adding to failed_hashes.csv')
				return False

	return False

def getFiredenImg(img_hash):
	"""
	Attempts to download an image from Fireden.net

	"""

	url_fireden =  'https://boards.fireden.net/_/search/image/' + img_hash.replace('/', '_')
	request = urllib.request.Request(url_fireden, headers=headers)
	print('Trying to get image from Fireden')
	print('with ' + url_fireden)
	
	#check if the thread is still active on 4plebs
	try:
		response = urllib.request.urlopen(request)

	#some threads get deleted and return a 404
	except urllib.error.HTTPError as httperror:
		print('HTTP error when requesting thread on fireden')
		print('Reason:', httperror.code)
		return False

	else:

		html = response.read()
		soup = BeautifulSoup(html, features="lxml")
		image_url = soup.findAll('a', {'class': 'thread_image_link'})
		
		# Request can be empty
		if image_url:
			image_url = image_url[0]['href']
		else:
			return False
			
		if '.webm' in image_url:
			print('Video file - discarding and adding to failed_hashes.csv')
			return False

		try:
			img_response = urllib.request.urlopen(image_url)
		except urllib.error.HTTPError as httperror:
			print('HTTP error when requesting image from Fireden')
			print('Reason:', httperror.code)
			return False
		except ConnectionResetError as conn_error:
			print('Connection closed by Fireden. Skipping image.')
			return False
		else:
			imagefile = io.BytesIO(img_response.read())

			if '.webm' not in imagefile:

				# Open and return the image
				image = Image.open(imagefile)
				return image

			else:
				print('Video file - discarding and adding to failed_hashes.csv')

	return False

# Show manual if needed
if len(sys.argv) < 2:
	print()
	print("Uses a image hash list to download corresponding images from 4plebs or 4CAT.")
	print("Will save the images in the highest possible resolution.")
	print()
	print("Usage: python3 getImages.py [--source] [--imagecol] [--top] [--timespan] [--timecol]")
	print()
	print("--source: the relative path to a csv file from 4CAT (e.g. 'data/datasheet.csv').")
	print("--output (optional): the name for the folder images will be saved in. Leave empty to save to output/images/.")
	print("--top (optional): default false - input a number, and if provided, downloads only the top n most used images based on grouping hashes.")
	print("--imagecol (optional): default 'image_md5' - the csv column with the image md5 hash.")
	print("--timespan (optional): if provided, will download top used images per month/day. Use 'months' or 'days'. Requires --top to work.")
	print("--timecol (optional): default 'timespan' - the csv column in which the time values are stored. Should start with format yyyy-mm-dd.")
	print()
	print("Example: python getImages.py --source=input/datasheet.csv --imagecol=image_md5 --top=50 --timespan=months --timecol=timestamp")
	print()
	sys.exit(1)

else:
	li_args = []
	source = ''
	board = ''
	top = 0
	img_column = 'image_md5'
	time_column = 'timestamp'
	output = ''
	timespan = False

	# Interpret command line arguments
	for arg in sys.argv:
		if arg[0:9] == "--source=":
			source = arg[9:len(arg)]
			li_args.append(source)
		elif arg[0:9] == "--output=":
			output = arg[9:len(arg)]
			li_args.append(output)
		elif "--imagecol=" in arg:
			img_column = arg[12:len(arg)]
			li_args.append(img_column)
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

		if timespan == False and top == 0:
			# Get the images for the raw csv file
			li_input = []
			li_timestamps = []

			# Make a list of the hashes and of the corresponding time of posting to know whether to query 4CAT
			for index, row in df.iterrows():
				# Filter out nans (with rows wihout images)
				if type(row[img_column]) == str:
					li_input.append(row[img_column])
					li_timestamps.append(row[time_column])

			# Get the images!
			getImages(li_input, li_timestamps, board, top=0)

		elif timespan == False and top > 0:

			# Get the top n images from the csv file
			df_ranks = df[img_column].value_counts()

			print('Most used hashes:')
			print(df_ranks[:top])

			li_hashes = df_ranks.index.tolist()[:top]
			li_counts = df_ranks.tolist()[:top]

			# Get the corresponding time values (could be made more efficient)
			li_timestamps = [df.loc[df[img_column] == img_hash] for img_hash in li_hashes]
			li_timestamps = [row[time_column].values for row in li_timestamps]
			li_timestamps = [times[0] for times in li_timestamps]
			
			# Get the images!
			getImages(li_hashes, li_timestamps, li_counts, top=top, output=output)

		elif timespan != False and top > 0:
			# Get top n images per timeframe (days or months)

			print('Getting top ' + str(top) + ' images by ' + timespan)
			
			# Get the dates to make files for
			li_all_dates = df[time_column].tolist()
			if timespan == 'days':
				li_dates = [date[0:10] for date in li_all_dates]
			elif timespan == 'months':
				li_dates = [date[0:7] for date in li_all_dates]
			else:
				print('Please provide a valid date format (\'days\' or \'months\')')
				sys.exit(1)

			df['dates_to_check'] = li_dates
			li_dates = set(li_dates)

			print('Dates to check: ')
			for date in li_dates:
				print(date)

			# Make a list of the hashes and of the corresponding time of posting to know whether to query 4CAT
			for date_slice in li_dates:
				
				print('Getting images for ' + date_slice)
				df_date = df[df[time_column].str.contains(date_slice)]
				
				# Get the top n images from the csv file
				df_ranks = df_date[img_column].value_counts()

				print('Most used hashes:')
				print(df_ranks[:top])

				li_hashes = df_ranks.index.tolist()[:top]
				li_counts = df_ranks.tolist()[:top]

				# Get the corresponding time values (could be made more efficient)
				li_timestamps = [df_date.loc[df_date[img_column] == img_hash] for img_hash in li_hashes]
				li_timestamps = [row[time_column].values for row in li_timestamps]
				li_timestamps = [times[0] for times in li_timestamps]

				# Get the images!
				getImages(li_hashes, li_timestamps, li_counts, top=top, date=date_slice, output=output)

		elif timespan != False and top == 0:
			print('You can only use time filtering by downloading the top most used images in that daterange.')
			print('Use --top=n and replace n by the amount of most-used images you want to fetch.')
			sys.exit(1)

		else:
			print('Incorrect parameters. Please check your input.')
			print("Example 1: python3 getImages.py --source=data/datasheet.csv")
			print("Example 2: python3 getImages.py --source=data/datasheet.csv --top=10 --timespan=days")