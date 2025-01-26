import aicspylibczi
import tifffile
import numpy as np
import os
import copy
# import xml.etree.ElementTree as ET
import math
from utils import divide_image_into_mesh, generate_mesh_coordinates, get_nb_pix_chunk_l, downsample_by_2

def get_channel_info(czi_file):
    if isinstance(czi_file, str):
        czi_file = aicspylibczi.CziFile(czi_file)
    # Pretty print metadata
    metadata = czi_file.meta
    # ET.dump(metadata)
    # Find the <DisplaySetting> tag
    display_setting = metadata.find(".//DisplaySetting")

    if display_setting is not None:
        # Find the <Channels> tag inside <DisplaySetting>
        channels = display_setting.find("Channels")
        
        if channels is not None:
            # Iterate over each <Channel> tag
            for channel in channels.findall("Channel"):
                channel_id = channel.get("Id")  # Get the channel ID attribute
                channel_name = channel.get("Name")  # Get the channel Name attribute
                
                # Extract additional details
                dye_name = channel.findtext("DyeName")
                emission = channel.findtext("DyeMaxEmission")
                excitation = channel.findtext("DyeMaxExcitation")
                color = channel.findtext("Color")
                
                print(f"Channel ID: {channel_id}")
                print(f"Name: {channel_name}")
                print(f"Dye: {dye_name}")
                print(f"Emission: {emission}")
                print(f"Excitation: {excitation}")
                print(f"Color: {color}")
                print("-" * 30)
        else:
            print("<Channels> tag not found inside <DisplaySetting>.")
    else:
        print("<DisplaySetting> tag not found in metadata.")
    return 


def get_czi_info(czi_file):
    if isinstance(czi_file, str):
        # Size
        file_size = os.path.getsize(czi_file)
        print(f"File size: {file_size / (1024 **3):.2f} GB")  
        czi_file = aicspylibczi.CziFile(czi_file)  
    # Content
    dims = czi_file.get_dims_shape()
    print("Number of tissue slices:", len(dims))
    for i, dim in enumerate(dims):
        for key in dim.keys():
            print(f"Seq {i}, {key} size:", dim[key][1]-dim[key][0])
        print('')
    return czi_file

        
def _get_chunk_bbox(czi_file, max_size_chunk_gb=30):
    # For each sequence get a vector that contains information for chunking.
    # So it returns a list of vectors.
    max_size_chunk = max_size_chunk_gb * 1024**3
    if isinstance(czi_file, str):
        czi_file = aicspylibczi.CziFile(czi_file)  
    bbox = czi_file.get_all_scene_bounding_boxes()
    dims = czi_file.get_dims_shape()
    pixel_type = czi_file.pixel_type
    if '16' in str(pixel_type):
        bytes_per_pix = 2
    else:
        # if uint8
        bytes_per_pix = 1
    nb_seq = len(bbox)
    chunk_idx_list = []
    for s in range(nb_seq):
        z_len = dims[s]['Z'][1] - dims[s]['Z'][0]  # Depth (Z-axis)
        x_min, y_min, w, h = bbox[s].x, bbox[s].y, bbox[s].w, bbox[s].h  # Bounding box details
        # The number of pixel on the side of the square
        nb_pix_chunk_l = get_nb_pix_chunk_l(max_size_chunk, z_len, bytes_per_pix)
        # The number of squares in x and y to divide the image
        nb_chunks_x, nb_chunks_y = divide_image_into_mesh(w, h, square_size=nb_pix_chunk_l)
        chunk_idx = [x_min, nb_chunks_x, y_min, nb_chunks_y, nb_pix_chunk_l, z_len, w, h]
        chunk_idx_list.append(chunk_idx)
    return chunk_idx_list


def _get_channel_idx(metadata, channel_name):
    # Get the idx of the channel in the array. 
    # Usually to get the idx that corresponds to GFP fro segmentation or DAPI for max projection.
    display_setting = metadata.find(".//DisplaySetting")
    channels = display_setting.find("Channels")
    channel_names = [channel.get("Name") for channel in channels.findall("Channel")]
    correct_channel_idx = channel_names.index(channel_name)
    return correct_channel_idx


def chunk_and_save_czi(czi_file, 
                       save_folderpath, 
                       base_filename, 
                       max_size_chunk_gb = 30, 
                       channel_name = 'EGFP'):
    # If czi_file is a string it may be the filepath.
    # Else the file was already readen.
    if isinstance(czi_file, str):
        czi_file = aicspylibczi.CziFile(czi_file)

    # Take the correct chanel that contains the microglia
    metadata = czi_file.meta
    correct_channel_idx = _get_channel_idx(metadata, channel_name)
    
    # Get the number of bytes per pixel depending on the dtype of pixels
    pixel_type = czi_file.pixel_type
    if '16' in pixel_type:
        pixel_type = np.uint16
    else:
        # if uint8
        pixel_type = np.uint8

    # Iterate through sequences i.e. slices of brain on one slide
    sequences = czi_file.get_dims_shape()
    # Get the list of the [x_min, nb_chunks_x, y_min, nb_chunks_y, nb_pix_chunk_l, z_len, w, h]
    bbox_list = _get_chunk_bbox(czi_file, max_size_chunk_gb)
    
    nb_seq = len(sequences)
    print("Start chunking")
    print(f"There are {nb_seq} tissue slices in this file")

    # Create the folder were files are stored if doesn't exist.
    os.makedirs(save_folderpath, exist_ok = True)
    for s, seq in enumerate(sequences):
        if seq['S'][1]-seq['S'][0] == 1:
            X_min, nb_chunks_x, Y_min, nb_chunks_y, l, z_len, x_len, y_len = bbox_list[s]
            xy_coordinates = generate_mesh_coordinates(num_squares_x = nb_chunks_x, 
                                           num_squares_y = nb_chunks_y, 
                                           square_size= l, 
                                           x0 = X_min, y0 = Y_min)
            X_max = X_min + x_len
            Y_max = Y_min + y_len
            nb_chunks = len(xy_coordinates)
            print(f"There are {nb_chunks} chunks for seq {s}")
            print(f"So, there are {nb_chunks} .tiff files to save")
            for nn, xy in enumerate(xy_coordinates):
                x_min = xy[0]
                x_max = x_min + l
                y_min = xy[1]
                y_max = y_min + l
                if x_max >= X_max:
                    x_max = X_max-1
                if y_max >= Y_max:
                    y_max = Y_max-1
                z_stack_list = [czi_file.read_mosaic(region = (x_min, y_min, x_max-x_min, y_max-y_min), 
                                             scale_factor = 1.0, 
                                             C = correct_channel_idx, 
                                             Z = z,
                                            dtype = pixel_type,
                                            )
                                    for z in range(z_len)]
                
                # Replace None with null_array and store the indices of None                
                null_array = np.zeros((x_max-x_min, y_max-y_min), dtype=np.uint8)
                none_indices = []
                for idx, item in enumerate(z_stack_list):
                    if item is None:
                        none_indices.append(idx)
                        z_stack_list[idx] = null_array
                    else:
                        z_stack_list[idx] = item[0][0] # The function .read_mosaic() returns an array (1,1,y,x)
                
                chunk_image = np.stack(z_stack_list, axis=0)
                chunk_image = np.transpose(chunk_image, (0, 2, 1))
                # Construct the base of the file path first
                file_name = f"{base_filename}_seq_{s}_chunk_{nn}_over_{nb_chunks-1}_x__{x_min}_{x_max}__y__{y_min}_{y_max}__"
                base_filepath = os.path.join(save_folderpath, file_name)
                # Add the `none_indices` part only if it has elements
                if len(none_indices) > 0:
                    save_filepath = f"{base_filepath}z_fails_{none_indices}.tiff"
                else:
                    save_filepath = f"{base_filepath}.tiff"
                # Save the chunk as a TIFF file
                print('shape: ', chunk_image.shape)
                tifffile.imsave(save_filepath, chunk_image)
                del chunk_image
                print(f"chunk {nn} of sequence {s} is saved in " + save_filepath)
        else:
            print("image is weird")
            print(seq['S'])
    del czi_file
    print("")
    return 


def maxproject_for_registration(czi_file, save_folderpath, channel_name = 'DAPI'):
    if isinstance(czi_file, str):
        czi_file = aicspylibczi.CziFile(czi_file)
    # Take the correct chanel that contains the nucleus
    metadata = czi_file.meta
    correct_channel_idx = _get_channel_idx(metadata, channel_name)

    bbox = czi_file.get_all_scene_bounding_boxes()
    sequences = czi_file.get_dims_shape()
    nb_seq = len(sequences)
    print("Start zmax projections")
    print(f"There are {nb_seq} tissue slices in this file")
    print(f"So, there are {nb_seq} images that will be saved as .tiff files")

    # Create the folder were files are stored if doesn't exist.
    os.makedirs(save_folderpath, exist_ok = True)
    for s, seq in enumerate(sequences):
        if seq['S'][1]-seq['S'][0] == 1:
            x_min, y_min, w, h = bbox[s].x, bbox[s].y, bbox[s].w, bbox[s].h  # Bounding box details
            z_len = sequences[s]['Z'][1] - sequences[s]['Z'][0]  # Depth (Z-axis)
            previous_image = np.zeros((w, h))
            previous_image = downsample_by_2(previous_image)
            for z in range(z_len):
                mosaic = czi_file.read_mosaic(region = (x_min, y_min, w, h), 
                                                scale_factor = 1.0, 
                                                C = correct_channel_idx, 
                                                Z = z,
                                                dtype = np.uint8,
                                                # background_color = (0.0,0.0,0.0)
                )
                # If you have RuntimeError:  - ERR=-1 (WMP_errFail)
                # In the library aicspylibczi replace 
                '''
                img = self.reader.read_mosaic(
                        plane_constraints, scale_factor, region, background_color
                    )
                return img
                '''
                # By
                '''
                try:
                    img = self.reader.read_mosaic(
                        plane_constraints, scale_factor, region, background_color
                    )
                    return img
                except RuntimeError as e:
                    print(f"Error reading image: {e}")
                    return None
                '''
                if mosaic is None:
                    continue
                z_image = mosaic[0][0] # The function returns an array (1,1,y,x)
                z_image = downsample_by_2(z_image)
                z_image = np.transpose(z_image, (1, 0))
                previous_image = np.maximum(z_image, previous_image)
            save_filepath = os.path.join(save_folderpath, f"zmax_proj_seq_{s}.tiff")
            # Save the chunk as a TIFF file
            tifffile.imsave(save_filepath, previous_image)
            del previous_image
            print(f"zmax projection of sequence {s} is saved in " + save_filepath)
        else:
            print("image is weird")
            print(seq['S'])
    del czi_file
    print("")
    return 
