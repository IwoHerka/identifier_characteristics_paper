import matplotlib.pyplot as plt
import numpy as np


def draw_one_dimensional_scatter(values):
    """
    Draws a one-dimensional scatter plot of the given numeric values.

    Parameters:
    - values: A list of numeric values to plot.

    """
    # Generate a fixed x-coordinate with slight random jitter
    x = np.ones(len(values))
    
    plt.figure(figsize=(3, 15))
    # Plotting the values
    plt.scatter(x, values)
    
    # Adding labels and title for clarity
    # plt.title('One-dimensional Scatter Plot')
    plt.yticks(values)  # Optionally, mark the values on the y-axis
    # plt.xlabel('Fixed Position with Slight Jitter')
    # plt.ylabel('Values')
    plt.savefig('build/plots/java_projects.png')
    
    # Show the plot
    plt.show()

# Example usage:
values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
draw_one_dimensional_scatter(values)

