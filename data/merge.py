import glob
import pandas as pd
import os

""" 
Checks if file is not empty
Args:
	fpath: the file path
Returns:
	true if the file is not empty. Otherwise, false.
""" 
def is_non_zero_file(fpath):  
    return True if os.path.isfile(fpath) and os.path.getsize(fpath) > 0 else False

"""
Concats data from files with the same name from different apartments_exports directories
"""
def main():
	# Create export directory if not already created
	EXPORT_DIR = "./export/"
	if not os.path.exists(EXPORT_DIR):
	    os.mkdir(EXPORT_DIR)

	# Create dataframe with single column of file fullpath (e.g. "./apartments_exports_van/abbotsford.csv")
	files = pd.DataFrame([file for file in glob.glob("./apartments_exports_*/*")], columns=["fullpath"])

	# Split fullpath into path-to-file (e.g. "./apartments_exports_van") 
	# and file name (e.g. "abbotsford.csv")
	files_split = files['fullpath'].str.rsplit("/", 1, expand=True).rename(columns={0: 'path', 1:'filename'})

	# Create dataframe with 3 columns: fullpath, path, and filename
	files = files.join(files_split)

	# Iterate over each unique filename
	for f in files['filename'].unique():
		# Get list of fullpaths from unique filenames
	    paths = files[files['filename'] == f]['fullpath']
	    print(paths)
	    # Get a list of dataframes from CSV file paths
	    dfs = [pd.read_csv(path, header=0) for path in paths if is_non_zero_file(path)]
	    if len(dfs) > 0:
		    # Concat dataframes into one if dataframe(s) exists for filename
		    concat_df = pd.concat(dfs)
		    # Save dataframe
		    concat_df.to_csv(EXPORT_DIR + f, index=False)

if __name__ == "__main__":
    main()
