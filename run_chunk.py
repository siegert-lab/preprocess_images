from process_czi import get_czi_info, chunk_and_save_czi
from process_ims import get_ims_info, chunk_and_save_ims

from io_images import get_images_infoframe

# Parameters
# Path to the folder that contains the .czi files.
# folderpath = "/run/user/1001/gvfs/smb-share:server=fs.ista.ac.at,share=drives/tnegrell/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS"
# ON WINDOWS
windows = True
folderpath = r"\\fs.ista.ac.at\drives\aventuri\archive\siegegrp\AlVe\MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS"

# If there is a tree structure in the folder that contains the .czi files.
# The length of the list should be the depth of the tree in the root folder.
conditions = []

# Format of the files, for now can be .czi or .ims and soon .tiff.
extension = '.czi'

# The root folder where .tiff files will be saved.
# result_folderpath = 'results'
# ON WINDOWS
result_foldername = r"\chunk_images"
result_folderpath = folderpath + result_foldername

# Size of the chunk in GB
chunk_size = 10

# Channel you want to segment microglia (usually EGFP or IBA1 or 1).
channel_name = 'EGFP'

# Get a pd.DataFrame that contains information about the different .czi files in the root folder.
# Most important is the name and the path of the .czi files.
infoframe = get_images_infoframe(folderpath, 
                                 conditions=conditions, 
                                 extension=extension, 
                                 windows=windows)

if windows:
    char = "\\"
else:
    char = "/" 

for i, row in infoframe.iterrows():
    ### TO REMOVE
    if i > 0:
        file_name = row['file_name']
        save_foldername = file_name[:-len(extension)]
        save_folderpath = result_folderpath + char + save_foldername

        file_path = row['file_path']
        print(f"The file {file_name} is selected for processing")
        extension = file_name[-len(extension):]
        if 'czi' in extension:
            czi_file = get_czi_info(file_path)
            chunk_and_save_czi(czi_file, 
                            save_folderpath, 
                                max_size_chunk_gb = chunk_size, 
                                channel_name = channel_name)
        elif 'ims' in extension:
            get_ims_info(file_path)
            print("Chunk not yet tested for ims")
        else:
            print("No function to process this file format.")