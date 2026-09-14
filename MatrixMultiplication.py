import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


SIZE = 100


class ProgressLog:
    """Stores the order in which matrix cells are completed."""

    def __init__(self):
        self.cells = []
        self.lock = threading.Lock()

    def add(self, row, column):
        # Prevent multiple threads from modifying the list at the same time.
        with self.lock:
            self.cells.append((row, column))


def create_matrix():
    """Create a random integer matrix."""

    # Generate a 100 x 100 matrix with values from 1 to 19.
    return tf.random.uniform(
        shape=(SIZE, SIZE),
        minval=1,
        maxval=20,
        dtype=tf.int32
    )


def calculate_cell(matrix_a, matrix_b, result, row, column, progress):
    """Calculate one cell of the result matrix."""

    # Select one row from Matrix A and one column from Matrix B.
    row_data = matrix_a[row, :]
    column_data = matrix_b[:, column]

    # Calculate the dot product to obtain one result cell.
    value = tf.reduce_sum(row_data * column_data)

    # Store the calculated value in the result matrix.
    result[row][column] = int(value.numpy())

    # Record the order in which this cell was completed.
    progress.add(row, column)


def multiply_matrices():
    # Create the two input matrices.
    matrix_a = create_matrix()
    matrix_b = create_matrix()

    # Initialize the result matrix with zeros.
    result = [[0 for _ in range(SIZE)] for _ in range(SIZE)]

    # Keep track of the order in which cells are completed.
    progress = ProgressLog()

    # Use the available CPU cores for the thread pool.
    workers = os.cpu_count() or 4

    print(f"Starting multiplication with {workers} threads...")

    start = time.perf_counter()

    tasks = []

    # Submit one task for every cell of the result matrix.
    with ThreadPoolExecutor(max_workers=workers) as executor:

        for row in range(SIZE):
            for column in range(SIZE):
                task = executor.submit(
                    calculate_cell,
                    matrix_a,
                    matrix_b,
                    result,
                    row,
                    column,
                    progress
                )
                tasks.append(task)

        # Wait until all calculations are completed.
        for task in as_completed(tasks):
            task.result()

    end = time.perf_counter()

    # Convert the execution time from seconds to milliseconds.
    elapsed = (end - start) * 1000

    print("Matrix multiplication completed.")
    print(f"Execution time: {elapsed:.2f} ms")

    # Display a small portion of the result for verification.
    print("\nFirst 3 x 3 part of the result:")
    for row in result[:3]:
        print(row[:3])

    return matrix_a, matrix_b, result, progress.cells


def create_animation(matrix_a, matrix_b, result, completed_cells):

    # Convert TensorFlow matrices to NumPy arrays for visualization.
    matrix_a = matrix_a.numpy()
    matrix_b = matrix_b.numpy()

    # Start with an empty result matrix for the animation.
    visible_result = np.full((SIZE, SIZE), np.nan)

    # Create three panels for Matrix A, Matrix B and Matrix C.
    figure, axes = plt.subplots(1, 3, figsize=(15, 5))

    ax_a = axes[0]
    ax_b = axes[1]
    ax_c = axes[2]

    ax_a.imshow(matrix_a, cmap="Blues", vmin=1, vmax=20)
    ax_b.imshow(matrix_b, cmap="Greens", vmin=1, vmax=20)

    # Matrix C will be filled as the animation progresses.
    result_image = ax_c.imshow(
        visible_result,
        cmap="Oranges"
    )

    ax_a.set_title("Matrix A")
    ax_b.set_title("Matrix B")
    ax_c.set_title("Matrix C")

    # Hide axis numbers for a cleaner display.
    for axis in axes:
        axis.set_xticks([])
        axis.set_yticks([])

    # Marker showing the current row being used from Matrix A.
    row_box = plt.Rectangle(
        (-0.5, -0.5),
        SIZE,
        1,
        fill=False,
        edgecolor="red",
        linewidth=2
    )

    # Marker showing the current column being used from Matrix B.
    column_box = plt.Rectangle(
        (-0.5, -0.5),
        1,
        SIZE,
        fill=False,
        edgecolor="red",
        linewidth=2
    )

    ax_a.add_patch(row_box)
    ax_b.add_patch(column_box)

    # Display the number of cells completed during the animation.
    status = figure.text(
        0.5,
        0.02,
        "",
        ha="center"
    )

    # Display 25 completed cells in each animation frame.
    cells_per_frame = 25

    total_frames = (
        len(completed_cells) + cells_per_frame - 1
    ) // cells_per_frame

    def update(frame):

        start_index = frame * cells_per_frame
        end_index = min(
            start_index + cells_per_frame,
            len(completed_cells)
        )

        current_row = 0
        current_column = 0

        # Show the cells completed during this frame.
        for index in range(start_index, end_index):

            row, column = completed_cells[index]

            visible_result[row][column] = result[row][column]

            current_row = row
            current_column = column

        # Update Matrix C in the animation.
        result_image.set_data(visible_result)

        # Move the row and column markers.
        row_box.set_y(current_row - 0.5)
        column_box.set_x(current_column - 0.5)

        # Update the progress message.
        status.set_text(
            f"Cells completed: {end_index}/{len(completed_cells)}"
            f"    C[{current_row}][{current_column}]"
        )

        return result_image, row_box, column_box, status

    # Create the animation using the actual completion order.
    animation = FuncAnimation(
        figure,
        update,
        frames=total_frames,
        interval=50,
        repeat=False
    )

    plt.tight_layout()
    plt.show()

    return animation


if __name__ == "__main__":

    # Run the matrix multiplication and record execution order.
    A, B, C, execution_order = multiply_matrices()

    # Create the visual animation of the multiplication.
    animation = create_animation(
        A,
        B,
        C,
        execution_order
    )

    # Save the animation as a GIF.
    animation.save(
        "matrix_multiplication.gif",
        writer="pillow",
        fps=10
    )

    print("\nGIF saved as matrix_multiplication.gif")
