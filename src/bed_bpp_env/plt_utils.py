
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

def visualize_heightmap_and_cps(heightmap: np.ndarray,
                                corner_points: list,
                                title_map: str = "Height-Map",
                                cmap: str = 'viridis') -> None:
    """
    Visualize heightmap and overlay corner points as red dots.

    Args:
        heightmap (np.ndarray): 2D array of shape (W, L).
        corner_points (list): List of tuples (x, y, z).
        title_map (str): Title for heightmap plot.
        cmap (str): Colormap for heightmap.
    """
    if heightmap.ndim != 2:
        raise ValueError(f"Input heightmap must be (W, L). Got {heightmap.shape}")

    W, L = heightmap.shape

    # --- Adaptive figure size based on heightmap dimensions ---
    # Scale width and height proportionally (0.5 inch per 10 cells)
    fig_width_in = max(6, L * 0.4)
    fig_height_in = max(4, W * 0.4)

    # --- Custom colormap for heightmap ---
    base_cmap = plt.get_cmap(cmap)
    colors = base_cmap(np.linspace(0, 1, 256))
    colors[0] = np.array([210/255, 180/255, 140/255, 1])  # Light brown for zero
    custom_cmap = ListedColormap(colors)

    # --- Create figure ---
    fig, ax = plt.subplots(figsize=(fig_width_in, fig_height_in), dpi=100)

    # Plot heightmap
    im = ax.imshow(heightmap, cmap=custom_cmap, origin='upper', interpolation='nearest')
    ax.set_title(f"{title_map} size {(L, W)}")
    ax.set_xlabel(f'L-Axis (Cols) [0 → {L-1}]')
    ax.set_ylabel(f'W-Axis (Rows) [0 → {W-1}]')

    # Grid setup
    ax.set_xticks(np.arange(-0.5, L, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, W, 1), minor=True)
    ax.grid(which='minor', color='black', linestyle='-', linewidth=0.5, alpha=0.3)
    ax.tick_params(which='minor', size=0)
    ax.set_xticks(np.arange(0, L, 1), minor=False)
    ax.set_yticks(np.arange(0, W, 1), minor=False)
    ax.set_xticklabels(np.arange(0, L, 1))
    ax.set_yticklabels(np.arange(0, W, 1))
    ax.tick_params(which='major', size=0)

    # Colorbar
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label='Normalized Height')

    # Overlay corner points as red dots
    xs = [cp[0] for cp in corner_points]
    ys = [cp[1] for cp in corner_points]
    ax.scatter(xs, ys, color='red', s=50, marker='o', label='Corner Points')

    # Legend
    ax.legend(loc='upper right')

    plt.tight_layout()
    plt.show()
   
