import os
import glob
import numpy as np
import pandas as pd
import tifffile as tiff
from PIL import Image
from utils import plot_image, add_condition_columns, update_file_name_and_path
import shutil

def get_images_infoframe(folderpath, 
                         extension =".czi", 
                         conditions = []):
    if "nt" in os.name:
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

def move_files(dataframe):
    """
    This function saves the files in the dataframe following the file path in the file_path column.
    It ensures the destination directories exist and moves the files to the new locations.
    
    Parameters:
        dataframe (pd.DataFrame): The dataframe containing the file paths (file_path column).
    """

    for _, row in dataframe.iterrows():
        # Get the old and new file paths
        old_path = row['old_file_path']
        new_path = row['file_path']
        
        # Check if the source (old path) file exists
        if not os.path.exists(old_path):
            print(f"Source file {old_path} does not exist.")
            continue  # Skip if the file doesn't exist
        
        # Get the destination folder (path without file name)
        destination_folder = os.path.dirname(new_path)
        # Ensure the destination folder exists, if not create it
        os.makedirs(destination_folder, exist_ok=True)
        
        try:
            # Move the file from old path to new path
            shutil.move(old_path, new_path)
            print(f"Moved {old_path} to {new_path}")
        except Exception as e:
            print(f"Error moving {old_path} to {new_path}: {e}")

def store_raw_images(folderpath,
                     age_values, 
                     sex_values, 
                     animal_values,
                     extension = ".czi",
                     ):
    
    # Get the original infoframe with the new raw images
    dataframe = get_images_infoframe(folderpath, 
                                    extension = extension, 
                                    conditions = [])
    
    # Set the metadata of the new raw images
    dataframe = add_condition_columns(dataframe, 
                                      age_values, 
                                      sex_values, 
                                      animal_values)

    # Update file name and path depending on the metadata
    if 'old_file_path' not in dataframe.columns:
        dataframe = update_file_name_and_path(dataframe,
                                              project_path = folderpath,
                                              folder_name = 'raw_images')
    
    # Save the new raw images in the tree structure following metadata
    move_files(dataframe)

    # Get the updated infoframe
    raw_images_path = os.path.join(folderpath, "raw_images")
    dataframe = get_images_infoframe(raw_images_path, 
                                        extension = extension, 
                                        conditions = ['Age', 'Sex', 'Animal'])    
    return dataframe

def load_and_plot_tiff(tiff_filepath, z=0):
    # Load the TIFF file
    array = tiff.imread(tiff_filepath)

    # Check the shape of the array
    print(f"Loaded TIFF shape: {array.shape}")

    # Extract the first 2D slice (assuming shape is [Z, Y, X])
    slice = array[z, :, :]
    plot_image(image=slice, title= f'The 2D Slice {z} from TIFF')

def save_array(array, folder_path, save_name, extension, grey_scale=np.uint8, windows = False):
    array = array.astype(grey_scale)  # Convert to uint8

    # Save as PNG
    image = Image.fromarray(array)
    if "nt" in os.name:
        char = "\\"
    else:
        char = "/" 
    file_path = folder_path + char + save_name + extension
    image.save(file_path)
