import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches


# Load the JSON data
def load_json_data(filepath):
    with open(filepath, "r") as file:
        data = json.load(file)
    return data


# Estimate reading time
def estimate_reading_time(readings):
    # Placeholder for reading times
    return [30 for _ in readings]


# Generate the progress bar with more visibly rounded corners
def generate_progress_bar(data, output_path):
    core_readings = data["core_readings"]
    reading_times = estimate_reading_time(core_readings)
    total_time = sum(reading_times)

    # Define a list of colors to cycle through for each block
    colors = ["#B48BFF", "#FFC107", "#03A9F4", "#4CAF50", "#FF5722"]

    # Create a figure and a single subplot
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_xlim(0, total_time)
    ax.set_ylim(
        0, 10
    )  # Adjust the y-axis limit to increase the "height" of the progress bar area
    ax.axis("off")  # Hide the axis

    current_time = 0
    for i, reading in enumerate(core_readings):
        color = colors[i % len(colors)]  # Cycle through the list of colors
        # Adjust the height and pad to maximize the appearance of rounded corners
        height = 5  # Increased height for more visible rounding
        pad = 0.3  # Adjust pad for rounding; play with this value
        rect = patches.FancyBboxPatch(
            (current_time, 2.5),
            reading_times[i],
            height,
            boxstyle=f"round,pad={pad}",
            color=color,
            ec="none",
        )
        ax.add_patch(rect)
        # Include reading time in the text annotation
        text_label = f"{reading['title']}\n({reading_times[i]} min)"
        plt.text(
            current_time + reading_times[i] / 2,
            8,
            text_label,
            ha="center",
            va="bottom",
            rotation=45,
            fontsize=8,
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
