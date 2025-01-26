from io_images import store_raw_images

# Parameters
# Path to the folder that contains the .czi files.
# windows = False
# folderpath = "/run/user/1001/gvfs/smb-share:server=fs.ista.ac.at,share=drives/tnegrell/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS"
# ON WINDOWS
windows = True
folderpath = r"\\fs.ista.ac.at\drives\aventuri\archive\siegegrp\AlVe\MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS"

age_values = [[]] 
sex_values = [[]] 
animal_values = [[]] 

infoframe = store_raw_images(folderpath = folderpath, 
                            age_values = age_values,
                            sex_values = sex_values, 
                            animal_values = animal_values,
                            extension = ".czi",
                            windows = windows)