import plotly.express as px

def plot_image(image, title='2D Image'):
    # Plot the first slice using Plotly
    fig = px.imshow(image, color_continuous_scale="gray")
    fig.update_layout(title=title, coloraxis_showscale=False)
    fig.show()