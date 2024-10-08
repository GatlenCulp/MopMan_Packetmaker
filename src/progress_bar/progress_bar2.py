import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path


# Load the JSON data
def load_json_data(filepath):
    with open(filepath, "r") as file:
        data = json.load(file)
    return data


# Estimate reading time
def estimate_reading_time(readings):
    # Placeholder for reading times
    return [30 for _ in readings]


# Function to create a rectangle with rounded corners
def rounded_rect(start_x, width, height, radius):
    """
    Create a matplotlib path representing a rectangle with rounded corners.
    """
    # Vertices of the rectangle
    vertices = [
        (start_x + radius, 0),  # Start
        (start_x + width - radius, 0),  # Line to right before bottom right curve
        (start_x + width - radius, 0),  # Control point 1 for bottom right curve
        (start_x + width, 0),  # Control point 2 for bottom right curve
        (start_x + width, radius),  # End of bottom right curve, start of right line
        (start_x + width, height - radius),  # Line up to just before top right curve
        (start_x + width, height - radius),  # Control point 1 for top right curve
        (start_x + width, height),  # Control point 2 for top right curve
        (start_x + width - radius, height),  # End of top right curve, start of top line
        (start_x + radius, height),  # Line to just before top left curve
        (start_x + radius, height),  # Control point 1 for top left curve
        (start_x, height),  # Control point 2 for top left curve
        (start_x, height - radius),  # End of top left curve, start of left line
        (start_x, radius),  # Line down to just before bottom left curve
        (start_x, radius),  # Control point 1 for bottom left curve
        (start_x, 0),  # Control point 2 for bottom left curve
        (start_x + radius, 0),  # End of bottom left curve, closing the path
    ]

    # Codes for drawing the path
    codes = [Path.MOVETO] + [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4] * 4

    path = Path(vertices, codes)
    return path


# Generate the progress bar with custom-rounded corners
def generate_progress_bar(data, output_path):
    core_readings = data["core_readings"]
    reading_times = estimate_reading_time(core_readings)
    total_time = sum(reading_times)

    # Define a list of colors to cycle through for each block
    colors = ["#B48BFF", "#FFC107", "#03A9F4", "#4CAF50", "#FF5722"]

    # Create a figure and a single subplot
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_xlim(0, total_time)
    ax.set_ylim(0, 10)  # Adjust the y-axis limit if needed
    ax.axis("off")  # Hide the axis

    current_time = 0
    for i, reading in enumerate(core_readings):
        color = colors[i % len(colors)]  # Cycle through the list of colors
        # Create a rectangle with custom-rounded corners
        radius = 1  # Radius of the rounded corners
        height = 1  # Adjust this value to make the rectangles thinner
        path = rounded_rect(current_time, reading_times[i], height, radius)
        patch = patches.PathPatch(path, facecolor=color, lw=0)
        ax.add_patch(patch)
        # Include reading time in the text annotation
        fontsize = 12  # Adjust this value to make the text larger
        text_label = f"{reading['title']}\n({reading_times[i]} min)"
        plt.text(
            current_time + reading_times[i] / 2,
            height + 1,
            text_label,
            ha="center",
            va="bottom",
            rotation=20,
            fontsize=fontsize,
            wrap=True,
        )
        current_time += reading_times[i]

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)


# Example usage
if __name__ == "__main__":
    json_filepath = "./progress_bar/precontext.json"
    output_image_path = "./progress_bar/progress_bar.png"
    json_data = load_json_data(json_filepath)
    generate_progress_bar(json_data, output_image_path)
