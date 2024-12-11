import math
import tifffile as tiff
import plotly.express as px

def plot_image(image, title='2D Image'):
    # Plot the first slice using Plotly
    fig = px.imshow(image, color_continuous_scale="gray")
    fig.update_layout(title=title, coloraxis_showscale=False)
    fig.show()

def load_and_plot_tiff(tiff_file, z=0):
    # Load the TIFF file
    array = tiff.imread(tiff_file)

    # Check the shape of the array
    print(f"Loaded TIFF shape: {array.shape}")

    # Extract the first 2D slice (assuming shape is [Z, Y, X])
    first_slice = array[z, :, :]
    plot_image(image=first_slice, title='First 2D Slice from TIFF')

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


def downsample_by_2(image):
    # Crop the image to make dimensions divisible by 2
    cropped_image = image[:image.shape[0] // 2 * 2, :image.shape[1] // 2 * 2]
    # Reshape and take the mean over 2x2 blocks
    downsampled = cropped_image.reshape(cropped_image.shape[0] // 2, 2, cropped_image.shape[1] // 2, 2).mean(axis=(1, 3))
    return downsampled
