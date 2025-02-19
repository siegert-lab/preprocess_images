import os 
from io_images import get_images_infoframe
from utils import get_base_filename, set_new_filepath
from process_czi import get_czi_info, chunk_and_save_czi
from process_ims import get_ims_info, chunk_and_save_ims

# Parameters
# Path to the folder that contains the .czi files.
# windows = False
# folderpath = "/run/user/1001/gvfs/smb-share:server=fs.ista.ac.at,share=drives/tnegrell/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS"
# ON WINDOWS
windows = "nt" in os.name
project_path = r"\\fs.ista.ac.at\drives\aventuri\archive\siegegrp\AlVe\MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS"
folder_path = os.path.join(project_path, "raw_images")

# If there is a tree structure in the folder that contains the .czi files.
# The length of the list should be the depth of the tree in the root folder.
conditions = ['Age', 'Sex', 'Animal']

# Format of the files, for now can be .czi or .ims and soon .tif.
extension = '.czi'

# The root folder where .tif files will be saved.
# ON WINDOWS
result_foldername = "chunk_images"

# Size of the chunk in GB
chunk_size = 10

# Channel you want to segment microglia (usually EGFP or IBA1 or 1).
channel_name = 'EGFP'

# Get a pd.DataFrame that contains information about the different .czi files in the root folder.
# Most important is the name and the path of the .czi files.
infoframe = get_images_infoframe(folderpath = folder_path, 
                                 conditions = conditions, 
                                 extension = extension)

if "nt" in os.name:
    char = "\\"
else:
    char = "/" 

for i, row in infoframe.iterrows():
    # The general folder
    # The path folder Age/Sex/Animal/Slide
    file_name = row['file_name']
    base_filename, age, sex, animal, slide = get_base_filename(file_name)
    result_folderpath = os.path.join(project_path, result_foldername, str(age), str(sex), str(animal), str(slide))
    # Normalize the base path (handles OS-specific separator issues)
    result_folderpath = os.path.normpath(result_folderpath)

    file_path = row['file_path']
    file_extension = os.path.splitext(file_path)[1]  # Get the extension (e.g., '.czi', '.tif')

    print(f"The file {file_name} is selected for processing")
    if 'czi' in file_extension:
        czi_file = get_czi_info(file_path)
        chunk_and_save_czi(czi_file, 
                            save_folderpath = result_folderpath, 
                            base_filename = base_filename,
                            max_size_chunk_gb = chunk_size, 
                            channel_name = channel_name)
        # Modify the name of the czi file to label that it was chunked
        modified_file_path = set_new_filepath(file_path)
        infoframe.at[i, 'file_path'] = modified_file_path

    elif 'ims' in file_extension:
        get_ims_info(file_path)
        print("Chunk not yet tested for ims")
        # Modify the name of the czi file to label that it was chunked
        modified_file_path = set_new_filepath(file_path)
        infoframe.at[i, 'file_path'] = modified_file_path
    else:
        print("No function to process this file format.")


