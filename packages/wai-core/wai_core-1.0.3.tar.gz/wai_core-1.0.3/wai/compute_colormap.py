import argparse
import logging
import os

import numpy as np
import torch
from colour import difference, sRGB_to_XYZ, XYZ_to_Lab
from tqdm import tqdm
from wai import store_data, WAI_COLORMAP_PATH
from wai.semantics import INVALID_COLOR, INVALID_ID

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """Converts RGB colors to the CIE Lab color space."""
    rgb_normalized = rgb / 255.0
    xyz = sRGB_to_XYZ(rgb_normalized)
    lab = XYZ_to_Lab(xyz)
    return lab


def calculate_cie2000_distance_matrix(colors: np.ndarray) -> np.ndarray:
    lab_colors = rgb_to_lab(colors)
    num_colors = colors.shape[0]
    distance_matrix = np.zeros((num_colors, num_colors), dtype=np.float32)

    for i in tqdm(range(num_colors)):
        j = i + 1
        colors2 = lab_colors[j:, :]
        colors1 = np.tile(lab_colors[i, :], (colors2.shape[0], 1))
        distances = difference.delta_E_CIE2000(colors1, colors2)
        distance_matrix[i, j:] = distances
        distance_matrix[j:, i] = distances  # symmetric distance metric

    return distance_matrix


def reorder_colors(colors: np.ndarray, metric: str) -> np.ndarray:
    """Farthest point sampling."""

    logger.info("Precomputing color distances...")
    if metric == "ciede2000":
        distance_matrix = calculate_cie2000_distance_matrix(colors)  # TODO
        distance_matrix = torch.from_numpy(distance_matrix).cuda()
    elif metric == "rgb":
        torch_colors = torch.from_numpy(colors).cuda().float()
        distance_matrix = torch.cdist(torch_colors, torch_colors)
    else:
        raise NotImplementedError(f"Unknown distance metric {metric}.")

    logger.info("Reordering colors...")
    num_colors = colors.shape[0]
    selected_indices = torch.zeros(num_colors, dtype=torch.long)

    # Start with the first color, i.e., the invalid color
    selected_indices[0] = INVALID_ID
    min_distances = distance_matrix[0, :]
    for idx in range(1, num_colors):
        # Find the index of the color that maximizes the minimum distance to the previously selected colors
        next_index = torch.argmax(min_distances)
        selected_indices[idx] = next_index
        # Update the minimum distances
        min_distances = torch.min(min_distances, distance_matrix[next_index, :])

    return colors[selected_indices, :]


def generate_rgb_colors(stride: int, threshold: int) -> np.ndarray:
    """Generates a NumPy array of RGB colors, regularly sampled in the RGB color space."""
    r_values = np.arange(0, 256, stride, dtype=np.uint8)
    g_values = np.arange(0, 256, stride, dtype=np.uint8)
    b_values = np.arange(0, 256, stride, dtype=np.uint8)
    r_grid, g_grid, b_grid = np.meshgrid(r_values, g_values, b_values, indexing="ij")

    # N colors with shape (N, 3)
    colors = np.stack((r_grid, g_grid, b_grid), axis=-1).reshape(-1, 3)

    # Filter out the invalid color
    invalid_color = np.array(INVALID_COLOR, dtype=np.uint8)
    colors = colors[~np.all(colors == INVALID_COLOR, axis=1)]

    # Exclude colors that are too close to black or white
    black_distances = np.linalg.norm(colors, axis=1)
    white_distances = np.linalg.norm(255 - colors, axis=1)
    colors = colors[(black_distances > threshold) & (white_distances > threshold)]

    # Add the invalid color as the very first color
    colors = np.vstack((invalid_color, colors))

    return colors


parser = argparse.ArgumentParser(description="RGB colormap generation")
parser.add_argument(
    "--stride",
    type=int,
    default=15,
    help="The step size between consecutive values for each RGB component.",
)
parser.add_argument(
    "--threshold",
    type=float,
    default=100,
    help="The minimum Euclidean distance from black or white in RGB space that a color must have "
    "to be included in the colormap.",
)
parser.add_argument(
    "--metric",
    type=str,
    choices=["rgb", "ciede2000"],
    default="rgb",
    help="The metric used during farthest point sampling. Colors in the colormap will be reordered "
    "to maximize distinctness between the colors. Valid choices are 'rgb', which uses the Euclidean "
    "distance in the RGB space, and 'ciede2000', which computes the CIEDE2000 color distance between "
    "colors in the CIE L*a*b* color space.",
)


if __name__ == "__main__":
    args = parser.parse_args()

    logger.info("Generating colors...")
    colors = generate_rgb_colors(stride=args.stride, threshold=args.threshold)
    logger.info(f"Generated {colors.shape[0]} colors")

    # Furthest point sampling to maximize distinctness between colors
    colors = reorder_colors(colors, metric=args.metric)

    # Export
    logger.info("Exporting colors...")
    rounded_num_colors = round(colors.shape[0], -3)  # round to the nearest thousand
    formatted_num_colors = f"{rounded_num_colors // 1000}k"
    if not WAI_COLORMAP_PATH.exists():
        os.makedirs(WAI_COLORMAP_PATH)
    fname = f"colors_fps_{formatted_num_colors}.npz"
    store_data(WAI_COLORMAP_PATH / fname, colors, "numpy")
