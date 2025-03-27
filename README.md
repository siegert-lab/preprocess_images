# Installation

You can install the package using either Conda or pip. Follow the steps below based on your preferred package manager.

## Prerequisites
- Python 3.10 or higher is required
- Git
- ISTA credentials (username and password)

## Using Conda
1. Clone the Repository:
```
git clone git@github.com:siegert-lab/preprocess_images.git
cd preprocess_images
```

2. Create and Activate the Conda Environment:
```
conda env create -f environment.yml
conda activate preprocess-img
```

> **Note:** During environment creation, you will be prompted for your ISTA username and password when installing the bdv_toolz package (`git+https://git.ista.ac.at/csommer/bdv_toolz.git`).

3. Install the Package:
```
pip install -e .
```

## Using pip
1. Clone the Repository:
```
git clone git@github.com:siegert-lab/preprocess_images.git
cd preprocess_images
```

2. Ensure Python 3.10 is installed on your system, then create and activate the virtual environment:
```
python -m venv preprocess-img
```
On macOS/Linux:
```
source preprocess-img/bin/activate
```
On Windows:
```
preprocess-img\Scripts\activate
```

3. Install the Required Packages:
```
pip install -r requirements.txt
pip install -e .
```

> **Note:** During installation, you will be prompted for your ISTA username and password when installing the bdv_toolz package (`git+https://git.ista.ac.at/csommer/bdv_toolz.git`).

# Generate SWC from Filaments in IMS files  

## Overview

When you have created filaments in an IMS file, you can convert these filaments into SWC file where each microglia skeleton is stored in a SWC file.

This functionality is built on top of:
1. A MATLAB package called "ImarisReader" that allows reading IMS files directly in MATLAB
2. The "NLMorphologyConverter.exe" executable from NeuroLand, used to correct and standardize the SWC files

Both of these components are included in the `src/skeletonize` directory of this repository.

## How to Generate SWC from Filaments in IMS files Using the Windows Computer of the Lab

1) Open a terminal.

2) Go to the directory containing the code of interest. To do so, write in the terminal:  
   `cd C:\Users\siege\Desktop\preprocess_images\scripts`

3) Now you have to check 2 parameters:  
   - The first parameter is the path to the folder containing the new IMS files.  
   - The second parameter is the path to the folder to store the new SWC files.  

4) you can run the code with your parameters. To do so, write in the terminal:  
  `.\run_skeletonize.bat "your_input_folder_path" "your_output_folder_path"`
   - `your_input_folder_path` is a path like `\\fs.ista.ac.at\group\siegegrp\AlVe\_Bioimaging\Alessandro\Anesthetics (female)\BRAIN\KXA\FKBP5\FKBP5KO`
   - `your_output_folder_path` is a path like `\\fs.ista.ac.at\group\siegegrp\AlVe\_Bioimaging\Alessandro\Anesthetics (female)\BRAIN\KXA\FKBP5\FKBP5KO\SWC`
  
  a. Make sure to add "" around the paths.
  b. you can use ctrl c and ctrl v on terminal to copy and paste the paths.

# Rename and Store CZI Files

## Overview

When you receive the CZI files from the Iof, they can be automatically renamed and stored. The storage process is automated to ensure that the files are well organized in a tree structure as follows: `Age/Sex/Animal/`. 

Each file is renamed according to this pattern: `raw_image_Age_xm_Sex_y_Animal_z_Slide_i.czi`  
Where:  
- `x` is the age in months  
- `y` is either "M" (Male) or "F" (Female)  
- `z` is the index of the animal, starting from 1  
- `i` is the index of the slide, starting from 0  

This standardization of file names helps facilitate the next processing steps, such as chunking and tracking.

## Important Notes

- **Excel Register Update**: Ensure that the register Excel file is up-to-date. Specifically:  
  - The **Age** column should contain integers.  
  - The **Sex** column should use uppercase letters ("M" or "F").  
  - The **Animal** column should contain integers.  
  - The **Slide_no** column must contain a unique integer for each row. If two rows share the same number in the **Slide_no** column, they could be mixed up.

- **Register File Update**: After a CZI file is stored, the register Excel file is updated automatically by adding an "X" in the **renamed/stored** column of the row corresponding to the file that was renamed and stored.

## How to Rename and Store Using the Windows Computer of the Lab

1) The register Excel file containing the metadata of the slides should be closed.

2) Open a terminal as admnistrator, right click run as administrator.

3) Activate the environment containing the necessary Python packages. To do so, write in the terminal:  
   `conda activate preprocess-img`

4) Go to the directory containing the code of interest. To do so, write in the terminal:  
   `cd C:\Users\siege\Desktop\preprocess_images\scripts`

5) Now you have to check 3 parameters:  
   - The first parameter is the path to the folder containing the new CZI files.  
     By default: `\\scratch4.ista.ac.at\scratch\siegegrp\_ImageDrop\Zeiss-AxioScan-Z1\Alessandro_20250318`  
   - The second parameter is the path to the folder of the project. This folder should contain a folder `raw_images` and a register Excel file.  
     By default: `\\fs.ista.ac.at\drives\aventuri\archive\siegegrp\AlVe\MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS`  
   - The third parameter is the name of the register Excel file that should be in the folder of the project.  
     By default: `slide_register_JoNa.xlsx`

6) If the default parameters are correct, you can run the code. To do so, write in the terminal:  
   `python run_a_store_czi.py`

   If the default parameters are not correct, you can run the code with your parameters. To do so, write in the terminal:  
   `python run_a_store_czi.py --input_folderpath a --output_folderpath b --register_name c`  
   where:
   - `a` is a path like `\\scratch4.ista.ac.at\scratch\siegegrp\_ImageDrop\Zeiss-AxioScan-Z1\7568_siegegrp_AlVe`
   - `b` is a path like `\\fs.ista.ac.at\drives\aventuri\archive\siegegrp\AlVe\MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS`
   - `c` is a name of a file like `slide_register_JoNa.xlsx`

   If some parameters are already correct by default, you do not need to rewrite them. For example, if the project folder has a new name, you can write:  
   `python run_a_store_czi.py --output_folderpath \\fs.ista.ac.at\drives\aventuri\archive\siegegrp\AlVe\new_name`

> **Note:** Instead of writing the full command with the long argument names, you can use the shortened versions:  
> Instead of:  
> `run_a_store_czi.py --input_folderpath a --output_folderpath b --register_name c`  
> You can write:  
> `run_a_store_czi.py -ifp a -ofp b -rn c`

# Chunk czi files in tif files

# Convert ND2 Files to BDV/XML+N5 Format

## Overview

This tool allows you to convert Nikon ND2 microscopy files to BigDataViewer (BDV) compatible N5 format. This conversion preserves the multidimensional structure of microscopy data while making it accessible through the BDV viewer.

## How to Convert ND2 Files

1) Activate the environment containing the necessary Python packages. To do so, write in the terminal:  
   ```
   conda activate preprocess-img
   ```

2) Go to the directory containing the scripts:  
   ```
   cd path/to/preprocess_images/scripts
   ```

3) Run the conversion script, specifying the input folder containing ND2 files and the output folder for N5 files:  
   ```
   python run_convert_nd2.py -ifp input_folder_path -ofp output_folder_path
   ```
   - `input_folder_path` is the path to the folder containing ND2 files
   - `output_folder_path` is the path where the converted N5 files will be saved

4) The script will:
   - Find all ND2 files in the input folder
   - Convert each file to N5 format with the same base name
   - Display a progress bar showing the conversion status

> **Note:** The conversion relies on the bdv_toolz package, which is installed as part of the environment setup.

# TrAIce tif files
CUDA_VISIBLE_DEVICES=0 trAIce img2swc -ip   /mnt/archive/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS/chunk_images/glass_slide/tif_filename -wss "(128, 128, 16)" -wsb "(128, 128, 16)" -spd /mnt/archive/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS/traced_microglia -mp ./ -spsl ./ -nw 1 -bsp ./


Updated command:

CUDA_VISIBLE_DEVICES=0 trAIce img2swc -ip /mnt/archive/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS/chunk_images/age/sex/animal/slide/microglia_Age_age_Sex_sex_animal_slide_seq_3_chunk_1_over_5_x__-37461_-27220__y__25669_35929__.tif -wss "(128, 128, 16)" -wsb "(128, 128, 16)" -tp "(0.3, 0.3, 1.0)" -spd /mnt/archive/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS/traced_microglia/animal/sex/animal/slide/microglia_Age_age_sex_animal_slide_seq_3_chunk_1_over_5_x__-37461_-27220__y__25669_35929__.tif -mp ./ -spsl ./ -nw 1 -bsp ./