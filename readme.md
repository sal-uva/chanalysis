# Chanalysis scrips
The chanalysis Python scripts in this repository offer a convenient approach to map trends, shifts, and characteristics in 4chan data, or any data with a similar structure. This way, it helps moving beyond considering the imageboard as an un-researchable anonymous blob.

It's a work in progress, but the current chanalysis scripts include:

1. **Frequency histograms**: Visualise the occurances of a particular word over time
2. **Identifying popular posts**: Show which posts are most replied to and thus garnered attention.
3. **Word trees**: Show what words usually follow on another word or set of words.
4. **Downloading images**: Download images from a set of posts
5. **Making an image wall**: Use images to create an image wall.

Note that these scripts might contain some bugs. More scripts will be added later.

## Usage
The scripts require Python 3.
Once you have installed Python 3 on your computer, clone or download this repo.
Go to the folder of the scrips in a terminal and install the requirements (`python -m pip install -r requirements.txt`). When executing the scripts (e.g. `python3 createLongString.py`) without parameters, it will show the functions and various options. Run the scripts e.g. like so: `python createLongString.py --source=input/star-wars.csv`.

All the resulting data files are saved in the `output/` folder.