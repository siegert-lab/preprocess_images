import os
import numpy as np
import math
from imaris_ims_file_reader.ims import ims
import tifffile
from utils import divide_image_into_mesh, generate_mesh_coordinates, get_nb_pix_chunk_l

def get_ims_info(ims_file):
    if isinstance(ims_file, str):
        # Size
        file_size = os.path.getsize(ims_file)
        print(f"File size: {file_size / (1024 **3):.2f} GB")  
        ims_file = ims(ims_file)
    # Content
    dims = ims_file.shape
    axis = ['T', 'C', 'Z', 'X', 'Y']
    for i, ax in enumerate(axis):
        print(ax + ':', dims[i])
    return


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


def chunk_and_save_ims(ims_file, save_folderpath, max_size_chunk_gb = 30, channel_idx = 1):
    if isinstance(ims_file, str):
        ims_file = ims(ims_file)  

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
    print(f"There are {nb_chunks} to save")
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
    
        print(chunk_image.shape)
        save_filepath = os.path.join(save_folderpath, f"chunk_{nn}:{nb_chunks}_x:{(x_min, x_max)}_y:{(y_min, y_max)}.tif")
        # Save the chunk as a TIFF file
        tifffile.imsave(save_filepath, chunk_image)