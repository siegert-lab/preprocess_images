import glob
import numpy as np
import pandas as pd

def get_images_infoframe(folderpath, extension =".czi", conditions = []):
    # get all the file paths in folder_location
    filepaths = glob.glob(
        "%s%s/*%s" % (folderpath, "/*" * len(conditions), extension)
    )
    print("Found %d files..." % len(filepaths))

    # convert the filepaths to array for metadata
    file_info = np.array(
        [_files.replace(folderpath, "").split("/")[1:] for _files in filepaths]
    )

    # create the dataframe for the population of cells
    info_frame = pd.DataFrame(data=file_info, columns=conditions + ["file_name"])
    info_frame["file_path"] = filepaths
    
    # print a sample of file names
    nb_files = len(filepaths)
    print(f"There are {nb_files} files in folder_location")

    return info_frame