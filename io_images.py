import glob
import numpy as np
import pandas as pd
from PIL import Image

def get_images_infoframe(folderpath, 
                         extension =".czi", 
                         conditions = [], 
                         windows = False):
    if windows:
        char0 = "%s%s\\*%s"
        char1 = "\\*"
        char2 = "\\"
    else:
        char0 = "%s%s/*%s"
        char1 = "/*"
        char2 = "/"  
    
    # get all the file paths in folder_location
    filepaths = glob.glob(
        char0 % (folderpath, char1 * len(conditions), extension)
    )
    print("Found %d files..." % len(filepaths))

    # convert the filepaths to array for metadata
    file_info = np.array(
        [_files.replace(folderpath, "").split(char2)[1:] for _files in filepaths]
    )

    # create the dataframe for the population of cells
    info_frame = pd.DataFrame(data=file_info, columns=conditions + ["file_name"])
    info_frame["file_path"] = filepaths
    
    # print a sample of file names
    nb_files = len(filepaths)
    print(f"There are {nb_files} files in folder_location")

    return info_frame



def save_array(array, folder_path, save_name, extension, grey_scale=np.uint8, windows = False):
    array = array.astype(grey_scale)  # Convert to uint8

    # Save as PNG
    image = Image.fromarray(array)
    if windows:
        char = "\\"
    else:
        char = "/" 
    file_path = folder_path + char + save_name + extension
    image.save(file_path)
