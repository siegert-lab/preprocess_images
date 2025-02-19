import os
import numpy as np
import math
from imaris_ims_file_reader.ims import ims
import tifffile
from utils import divide_image_into_mesh, generate_mesh_coordinates, get_nb_pix_chunk_l

def get_ims_shape(ims_file):
    if isinstance(ims_file, str):
        ims_file = ims(ims_file)  
        
    # Extract shape and define axis labels
    dims = ims_file.shape
    axis = ['T', 'C', 'Z', 'X', 'Y']
    
    # Mapping of old keys to new names
    rename_keys = {'X': 'x_nb_pix', 'Y': 'y_nb_pix', 'Z': 'z_nb_pix'}
    
    # Create dictionary with renamed keys
    shape_dict = {rename_keys[ax]: dims[i] for i, ax in enumerate(axis) if ax in rename_keys}

    # Print the dimensions
    for i, ax in enumerate(axis):
        print(ax + ':', dims[i])

    return shape_dict

def get_ims_memory_size(ims_filepath):
    if isinstance(ims_filepath, str):
        file_size = os.path.getsize(ims_filepath)
        print(f"File size: {file_size / (1024 **3):.2f} GB") 
        return file_size
    else:
        print(f"{ims_filepath} not a path") 
        return None
    
def get_ims_pixel_size(ims_file):
    if isinstance(ims_file, str):
        ims_file = ims(ims_file)  
    z_mu_per_pix, x_mu_per_pix, y_mu_per_pix = ims_file.resolution
    return {'x_pix_per_mu':1/x_mu_per_pix, 'y_pix_per_mu':1/y_mu_per_pix, 'z_pix_per_mu':1/z_mu_per_pix}

def get_ims_info(ims_file):
    file_size = get_ims_memory_size(ims_file)
    if isinstance(ims_file, str):
        ims_file = ims(ims_file)
    pixel_size_dict = get_ims_pixel_size(ims_file)
    nb_pixels_dict = get_ims_shape(ims_file)

    result = {'img_size': file_size}
    result.update(pixel_size_dict)
    result.update(nb_pixels_dict)
    
    return ims_file, result

def _get_chunk_bbox(ims_file, max_size_chunk_gb=30):
    max_size_chunk = max_size_chunk_gb * 1024**3
    if isinstance(ims_file, str):
        ims_file = ims(ims_file)  
    
    pixel_type = ims_file.dtype
    if '16' in str(pixel_type):
        bytes_per_pix = 2
    else:
        # if uint8
        bytes_per_pix = 1
    
    _, _, z_len, x_len, y_len = ims_file.shape
    nb_pix_chunk_l = get_nb_pix_chunk_l(max_size_chunk, z_len, bytes_per_pix)
    nb_chunks_x, nb_chunks_y = divide_image_into_mesh(x_len, y_len, square_size=nb_pix_chunk_l)
    chunk_idx = [0, nb_chunks_x, 0, nb_chunks_y, nb_pix_chunk_l, z_len, x_len, y_len]
    return chunk_idx

def chunk_and_save_ims(ims_file, 
                       save_folderpath, 
                       base_filename,
                       max_size_chunk_gb = 30, 
                       channel_idx = 2):
    ims_file, metadata = get_ims_info(ims_file)
    # Create the folder were files are stored if doesn't exist.
    os.makedirs(save_folderpath, exist_ok = True)

    bbox = _get_chunk_bbox(ims_file, max_size_chunk_gb)
    X_min, nb_chunks_x, Y_min, nb_chunks_y, l, _, x_len, y_len = bbox
    xy_coordinates = generate_mesh_coordinates(num_squares_x = nb_chunks_x, 
                                                num_squares_y = nb_chunks_y, 
                                                square_size= l, 
                                                x0 = X_min, y0 = Y_min)
    X_max = X_min + x_len
    Y_max = Y_min + y_len
    nb_chunks = len(xy_coordinates)
    print(f"There are {nb_chunks} chunks")
    print(f"So, there are {nb_chunks} .tif files to save")
    for nn, xy in enumerate(xy_coordinates):
        x_min = xy[0]
        x_max = x_min + l 
        y_min = xy[1]
        y_max = y_min + l
        if x_max >= X_max:
            x_max = X_max-1
        if y_max >= Y_max:
            y_max = Y_max-1
        chunk_image = ims_file[0, channel_idx, :, x_min:x_max, y_min:y_max]
        # Construct the base of the file path first
        file_name = f"{base_filename}_chunk_{nn}_over_{nb_chunks-1}_x__{x_min}_{x_max}__y__{y_min}_{y_max}__"
        base_filepath = os.path.join(save_folderpath, file_name)
        save_filepath = f"{base_filepath}.tif"
        # Save the chunk as a TIFF file
        print('shape: ', chunk_image.shape)
        tifffile.imsave(save_filepath, chunk_image, metadata=metadata)
        del chunk_image
        print(f"chunk {nn} is saved in " + save_filepath)
    
    del ims_file
    print("")
    return 