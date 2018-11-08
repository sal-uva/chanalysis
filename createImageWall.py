"""Script to generate an Image wall given a list of image files. Credits to Partha Das."""

__author__      = "Partha Das"

import sys
import glob
import os
import math
from PIL import Image

def waller(grid_x, grid_y, res_x, res_y, files, output_name, keep_ratio=False):
	imageWall = Image.new('RGB', (grid_x * res_x, grid_y * res_y))
	counter = 0
	loc_x = 0
	loc_y = 0
	l = grid_x * grid_y

	for x in range(grid_x):
		for y in range(grid_y):
			print('\rProcessed: %d%%' % (counter / l * 100), end='\r', flush=True)
			f = files[counter]
			# avoid video files
			pic = Image.open(f)
			if keep_ratio:
				pic.thumbnail((res_x, res_y))
			else:
				pic = pic.resize((res_x, res_y))
			imageWall.paste(pic, (x * res_x, y * res_y))
			counter += 1
	
	# Make the output folder
	if not os.path.exists('output/images/'):
		os.makedirs('output/images/')
	if not os.path.exists('output/images/imagewalls/'):
		os.makedirs('output/images/imagewalls/')

	print('Saving image...')
	imageWall.save('output/images/imagewalls/' + output_name)

	if keep_ratio:
		print('Completed the image wall with original image ratios.')
	else:
		print('Completed the image wall with square images.')
	print('Saved the image wall here: output/images/imagewalls/' + output_name)

# Show manual if needed
if len(sys.argv) < 2:
	print()
	print("Creates an image wall from a folder containing images.")
	print()
	print("Usage: python3 createImageWall.py [--source]")
	print()
	print("--source: the relative path to the folder containing the images (e.g. 'input/images/').")
	print()
	print("Example:")
	print("python3 createImageWall.py --source=input/images/")
	print()
	sys.exit(1)

else:
	li_args = []
	source = ''

	# Interpret command line arguments
	for arg in sys.argv:
		if arg[0:9] == "--source=":
			source = arg[9:len(arg)]
			li_args.append(source)

			if not source.endswith('/'):
				source = source + '/'

			# Use the folder name as the filename for the image wall
			filename = str(source).split('/')
			filename = filename[len(filename) - 2]

			li_args.append(filename)
		
	print(li_args)

	if source == '' or not os.path.isdir(source):
		print("Please provide a path to a valid folder like this: --source=input/images/")
		sys.exit(1)

	else:
		files = os.listdir(source)
		files = [source + file for file in files if file[-5:] != '.webm']
		#size = int(math.sqrt(len(files)))
		w = int(math.sqrt(len(files))) + int(math.sqrt(len(files)) / 3)
		h = int(math.sqrt(len(files))) - int(math.sqrt(len(files)) / 3)
		
		waller(w, h, 300, 300,
		   files,
		   filename + '-wall.png', True)
		waller(w, h, 300, 300,
		   files,
		   filename + '-wall-no-aspect.png')