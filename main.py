from process_czi import get_czi_info, chunk_and_save_czi, maxproject_for_registration
from process_ims import get_ims_info, chunk_and_save_ims 

from io_images import get_images_infoframe

# Parameters
# Path to the folder that contains the .czi files.
folderpath = "/run/user/1001/gvfs/smb-share:server=fs.ista.ac.at,share=drives/tnegrell/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS"

# If there is a tree structure in the folder that contains the .czi files.
# The length of the list should be the depth of the tree in the root folder.
conditions = []

# Format of the files, for now can be .czi or .ims and soon .tiff.
extension = '.czi'

# The root folder where .tiff files will be saved.
result_folderpath = 'results'

# Size of the chunk in GB
chunk_size = 3

# Channel you want to segment microglia (usually EGFP or IBA1 or 1).
channel_name = 'EGFP'

# Get a pd.DataFrame that contains information about the different .czi files in the root folder.
# Most important is the name and the path of the .czi files.
# TODO 
    # Add info like the number of sequence, the idx of the channels of interest, 
    # a new name that is link to something like the animal, age of animal, order of the slice in the sequence of slices.
infoframe = get_images_infoframe(folderpath, conditions=conditions, extension=extension)

for i, row in infoframe.iterrows():
    file_name = row['file_name']
    save_foldername = file_name[:-4]
    save_folderpath = result_folderpath + "/" + save_foldername

    file_path = row['file_path']
    print(f"The file {save_foldername} is selected for processing")
    extension = file_name[-4:]
    print(file_name)
    if 'czi' in extension:
        get_czi_info(file_path)
        chunk_and_save_czi(file_path, save_folderpath, 
                           max_size_chunk_gb = chunk_size, channel_name = channel_name)
        maxproject_for_registration(file_path, save_folderpath, channel_name = 'DAPI')

        
    elif 'ims' in extension:
        get_ims_info(file_path)
        chunk_and_save_ims(file_path, save_folderpath, 
                           max_size_chunk_gb = chunk_size, channel_idx = 1)
    else:
        print("No function to chunk this file format.")