import math
import tifffile as tiff
import plotly.express as px

def load_and_plot_tiff(tiff_file):
    # Load the TIFF file
    array = tiff.imread(tiff_file)

    # Check the shape of the array
    print(f"Loaded TIFF shape: {array.shape}")

    # Extract the first 2D slice (assuming shape is [Z, Y, X])
    first_slice = array[0, :, :]

    # Plot the first slice using Plotly
    fig = px.imshow(first_slice, color_continuous_scale="gray")
    fig.update_layout(title="First 2D Slice from TIFF", coloraxis_showscale=False)
    fig.show()


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
            y = y0 - i * square_size
            coordinates.append((x, y))
    
    return coordinates
