import os
import numpy as np
import math
import re
import pandas as pd

def add_condition_columns(dataframe, register_path, age_values, sex_values, animal_values):
    '''
    Add columns 'Age', 'Sex', 'Animal', and 'Slide' to a dataframe. The 'Slide' column
    will assign a unique index (0 to N) for rows with the same values for Age, Sex, and Animal.
    Each column is populated based on the given index ranges: [value, start_idx, end_idx].

    Parameters:
        dataframe (pd.DataFrame): The dataframe you want to modify.
        age_values (list of tuples): List of triples for the 'Age' column.
            Each tuple is of the form [value, start_idx, end_idx].
        sex_values (list of tuples): List of triples for the 'Sex' column.
            Each tuple is of the form [value, start_idx, end_idx].
        animal_values (list of tuples): List of triples for the 'Animal' column.
            Each tuple is of the form [value, start_idx, end_idx].

    Returns:
        pd.DataFrame: The dataframe with the new 'Age', 'Sex', 'Animal', and 'Slide' columns added.
    '''
    
    # Helper function to fill a column based on value and index ranges

    # Extract numeric part of the file_name to sort by
    dataframe['file_number'] = dataframe['file_name'].str.extract('(\d+)', expand=False).astype(int)

    # Sort the dataframe by the extracted file number
    dataframe = dataframe.sort_values('file_number')
    # Initialize the new columns with None or a default value
    dataframe['Age'] = None
    dataframe['Sex'] = None
    dataframe['Animal'] = None
    
    if register_path is not None:
        # Read the Excel file into a DataFrame
        register_frame = pd.read_excel(register_path)
        # Ignore the files that were already renamed and store
        new_slides_frame = register_frame[register_frame['renamed/stored'].isna()].copy()
        # Ignore the rows in the excel file that are not labeled with the number of the glass slide
        new_slides_frame_defined = new_slides_frame[new_slides_frame['Slide_no'].notna()].copy()
        new_slides_frame_defined['Slide_no'] = new_slides_frame_defined['Slide_no'].astype(int)
        # Loop through each row of interest in the excel file 
        for _, row in new_slides_frame_defined.iterrows():
            slide_no = row['Slide_no']  # Get Slide_no from the current row
            # Find the matching file_name in dataframe that contains the Slide_no as a substring
            dataframe['diff'] = dataframe['file_name'].apply(
                lambda x: np.nan if pd.isna(x) else np.abs(int(re.search(r'\d+', x).group()) - int(slide_no))
            )
            closest_index = register_frame['diff'].idxmin()
            if not row.empty:
                # Use .loc to update the correct row in the original dataframe
                dataframe.loc[closest_index, 'Age'] = str(int(row['Age (mo)'])) + 'm'
                dataframe.loc[closest_index, 'Sex'] = row['Sex']
                dataframe.loc[closest_index, 'Animal'] = 'Animal_' + str(int(row['Animal_replicate']))
            dataframe = dataframe.drop('diff', axis=1)

    else:
        def fill_column(column_name, value_ranges):
            for value, start_idx, end_idx in value_ranges:
                dataframe.loc[start_idx:end_idx, column_name] = value
        # Fill 'Age', 'Sex', and 'Animal' columns using the helper function
        fill_column('Age', age_values)
        fill_column('Sex', sex_values)
        fill_column('Animal', animal_values)
    
    dataframe = dataframe.dropna()
    # Create the 'Slide' column based on groups of 'Age', 'Sex', 'Animal'
    dataframe['Slide'] = dataframe.groupby(['Age', 'Sex', 'Animal']).cumcount().astype(int).apply(lambda x: f"Slide_{x}")

    return dataframe

def update_file_name_and_path(dataframe, project_path=None, folder_name = 'raw_images'):
    '''
    Rename the file names in the column file_name in the pattern 
    folder_name_Age_x_Sex_y_Animal_z_Slide_i.[ext].
    And change the file pathes in the column file_path in the pattern 
    project_path/folder_name/x/y/z/folder_name_Age_x_Sex_y_Animal_z_Slide_i.[ext].
    Or if not raw image 
    project_path/folder_name/x/y/z/i/folder_name_Age_x_Sex_y_Animal_z_Slide_i.[ext].

    Parameters:
        dataframe (pd.DataFrame): The dataframe you want to modify.
        project_path (str): Path to the folder that contains the folder folder_name.
            If None, the project_path in the column file_path is reused.
    '''
    update_path = 'old_file_path' not in dataframe.columns

    for index, row in dataframe.iterrows():
        # Extract variables from the dataframe row
        age = row['Age']
        sex = row['Sex']
        animal = row['Animal']
        slide = row['Slide']
        file_name = row['file_name']
        file_path = row['file_path']
        
        # Store the original file path in the new column 'old_file_path'
        if update_path:
            dataframe.at[index, 'old_file_path'] = file_path
        
        # Detect the file extension
        file_extension = os.path.splitext(file_path)[1]  # Get the extension (e.g., '.czi', '.tif')
        
        # Generate the new file name based on the pattern
        if folder_name == 'raw_images':
            new_file_name = f"raw_image_Age_{age}_Sex_{sex}_{animal}_{slide}{file_extension}"
        # TODO
        # elif folder_name == 'chunk_images':
        #     new_file_name = f"microglia_Age_{age}_Sex_{sex}_{animal}_{slide}_{file_name[10:]}"
        # elif folder_name == 'zmax_projections':
        #     new_file_name = f"zmax_proj_Age_{age}_Sex_{sex}_{animal}_{slide}_{file_name}"

        # Update the 'file_name' column
        dataframe.at[index, 'file_name'] = new_file_name
        
        # Determine the project path (either the one passed in or from the file_path column)
        if project_path is None:
            # Extract the current base path (everything up to 'folder_name')
            base_path = os.path.dirname(file_path)
        else:
            base_path = project_path
        
        # Normalize the base path (handles OS-specific separator issues)
        base_path = os.path.normpath(base_path)
        
        # Create the new file path based on the pattern
        if folder_name == 'raw_images':
            new_file_path = os.path.join(base_path, folder_name, str(age), str(sex), str(animal), new_file_name)
        # TODO
        # else:
        #     new_file_path = os.path.join(base_path, folder_name, str(age), str(sex), str(animal), str(slide), new_file_name)

        # Normalize the new file path (handles OS-specific separator issues)
        new_file_path = os.path.normpath(new_file_path)
        
        # Update the 'file_path' column
        dataframe.at[index, 'file_path'] = new_file_path

    return dataframe

def get_base_filename(file_name):
    # Use regular expressions to extract the components
    match = re.match(r"raw_image_Age_(\d+m)_Sex_(\w)_Animal_(\d+)_Slide_(\d+)_", file_name)
    
    if match:
        # Extract values from the match groups
        age = match.group(1)    # Age, e.g., '18m'
        sex = match.group(2)    # Sex, e.g., 'F'
        animal = match.group(3) # Animal, e.g., '1'
        slide = match.group(4)  # Slide, e.g., '0'
        
        # Create the base filename
        base_filename = f"microglia_Age_{age}_Sex_{sex}_Animal_{animal}_Slide_{slide}_"
        return base_filename, age, sex, animal, slide
    else:
        raise ValueError("Filename does not match expected pattern")

def set_new_filepath(file_path):
    file_extension = os.path.splitext(file_path)[1]  # Get the extension (e.g., '.czi', '.tif')
    file_path_wo = os.path.splitext(file_path)[0]
    # Modify the file name by appending '_chunked' to the filename
    modified_file_path = f"{file_path_wo}_chunked{file_extension}"
    print(f"Modified file path: {modified_file_path}")
    
    # Rename the file in the folder
    if not os.path.exists(modified_file_path):  # Ensure the new file doesn't already exist
        os.rename(file_path, modified_file_path)  # Rename the file on disk
        print(f"File renamed to: {modified_file_path}")
    else:
        print(f"File already exists: {modified_file_path}, skipping renaming.")
    return modified_file_path

# Utils function to define the chunking bbox
def get_nb_pix_chunk_l(max_size_chunk, z_len, bytes_per_pix):
    nb_pix_chunk = int(max_size_chunk / bytes_per_pix)
    nb_pix_chunk_xy = int(nb_pix_chunk / z_len)
    nb_pix_chunk_l = int(math.sqrt(nb_pix_chunk_xy))
    return nb_pix_chunk_l

def divide_image_into_mesh(width, height, square_size):
    """
    Divide an image into a grid of squares of a given size.

    Parameters:
        width (int): The width of the image.
        height (int): The height of the image.
        square_size (int): The size (length) of each square.

    Returns:
        num_squares_x (int): The number of squares along the x-axis.
        num_squares_y (int): The number of squares along the y-axis.
    """
    # Calculate the number of squares in each dimension
    num_squares_x = math.ceil(width / square_size)
    num_squares_y = math.ceil(height / square_size)

    return num_squares_x, num_squares_y

def generate_mesh_coordinates(num_squares_x, num_squares_y, square_size, x0=0, y0=0):
    # Generate the grid of coordinates
    coordinates = []
    for i in range(num_squares_y):
        for j in range(num_squares_x):
            x = x0 + j * square_size
            y = y0 + i * square_size
            coordinates.append((x, y))
    
    return coordinates

# For the registration/alignment we reduce the resolution of the z max projection 
def downsample_by_2(image):
    # Crop the image to make dimensions divisible by 2
    cropped_image = image[:image.shape[0] // 2 * 2, :image.shape[1] // 2 * 2]
    # Reshape and take the mean over 2x2 blocks
    downsampled = cropped_image.reshape(cropped_image.shape[0] // 2, 2, cropped_image.shape[1] // 2, 2).mean(axis=(1, 3))
    return downsampled
