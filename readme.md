# Chanalysis scrips (beta)
The chanalysis Python scripts in this repository offer a convenient approach to map trends, shifts, and other characteristics with 4chan data, or any data with a similar structure. The scripts can help moving beyond the consideration of the anonymous imageboard as an un-researchable and homogeneous blob.

Note that these scripts are a work in progress and may contain bugs.

The current chanalysis scripts include:

1. `createHistogram.py` **Frequency histograms**: Visualise the occurances of a particular word over time
2. `getReplies.py` **Identifying popular posts**: Show which posts are most replied to and thus garnered attention.
3. `createTokens.py` **Tokenization**: Tokenise the text (lemmatization and stemming).
4. `createLongString.py` **Creating a text file**: Takes text in a csv column and outputs as a long text in a .txt file. Useful in tandem with jasondavies.com/wordtree/.
4. `getImages.py` **Downloading images**: Download images from a set of posts
5. `createImageWall.py` **Making an image wall**: Use downloaded images to create an image wall.
6. `getTfidf.py` **Get popular terms**: (work in progress) Outputs popular words in the dataset via tf-idf.

More scripts will be added later.

## Usage
The scripts require Python 3.
Once you have installed Python 3 on your computer, clone or download this repository.
Go to the folder of the scrips in a terminal and install the requirements (`python -m pip install -r requirements.txt`). When executing the scripts (e.g. `python3 createLongString.py`) without parameters, it will show the functions and various options. Run the scripts e.g. like so: `python createLongString.py --source=input/star-wars.csv`.

All the resulting data files are saved in the `output/` folder.