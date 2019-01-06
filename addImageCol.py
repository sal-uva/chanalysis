import sys
import os
import hashlib
import pandas as pd
import base64
import math

def addImageCol(df, source_path, image_col):
	"""
	Adds a column with hexidecimal md5 hashes from image hashes

	"""

	li_hex_hashes = []
	li_hashes = df[image_col].tolist()

	for old_hash in li_hashes:
		image_hash = old_hash

		#print(image_hash)

		if type(image_hash) == str:
			# Hash should be changed to hexademical
			# md5 = hashlib.md5(image_hash.encode()).hexdigest()
			# print(md5)
			# md5 = hashlib.md5()
			# md5.update(base64.b64decode(image_hash))
			#image_hash = image_hash.hexdigest() + '_'
			md5 = hashlib.md5()
			md5.update(base64.b64decode(str(image_hash)))
			#md5.hexdigest
			#image_hash = hashlib.md5(image_hash.encode()).hexdigest()
			li_hex_hashes.append(md5.hexdigest() + '_')
		else:
			li_hex_hashes.append(image_hash)
	
	df['image_names'] = li_hex_hashes

	df.to_csv(source_path[:-4] + '_with_imagenames.csv')
	print('done!')

# show manual if needed
if len(sys.argv) < 2:
	print()
	print("This script adds a column to a csv with the names of images downloaded with getImages.")
	print()
	print("Usage: python3 addImageCol.py [--source] [--imagecol]")
	print()
	print("--source: the relative path to a csv file from 4CAT (e.g. 'input/obama.csv').")
	print("--imagecol (optional): default 'image_md5'. The column with the image hashes in the csv. ")
	print()
	print("Example:")
	print("python3 addImageCol.py --source=input/obama.csv --imagecol=image_hash")
	print()
	sys.exit(1)

else:
	li_args = []
	source = ''
	filename = ''
	image_col = 'image_md5'

	# Interpret command line arguments
	for arg in sys.argv:
		if arg[0:9] == "--source=":
			source = arg[9:len(arg)]
			li_args.append(source)
		elif arg[0:11] == "--imagecol=":
			image_col = arg[11:len(arg)]
			li_args.append(image_col)
	print(li_args)

	if source == '' or not os.path.isfile(source):
		print("Please provide a valid input file like this: --source=input/datasheet.csv")
		sys.exit(1)

	df = pd.read_csv(source, encoding='utf-8')
	addImageCol(df, source, image_col)