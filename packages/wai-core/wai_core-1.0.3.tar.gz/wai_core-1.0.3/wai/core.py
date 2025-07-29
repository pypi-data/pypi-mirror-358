# Core wai
import logging
import re
from pathlib import Path

import torch

from .camera import CAMERA_KEYS, convert_camera_coeffs_to_pinhole_matrix
from .io import _get_method
from .ops import stack

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

WAI_MAIN_PATH = Path(__file__).parent.parent
WAI_COLORMAP_PATH = WAI_MAIN_PATH / "wai" / "colormaps"


def load_data(fname, format=None, **kwargs):
    """
    Loads data from a file using the appropriate method based on the file format.

    Args:
        fname (str or Path): The filename or path to load data from.
        format (str, optional): The format of the data. If None, it will be inferred from the file extension.
            Supported formats include: 'readable', 'scalar', 'image', 'binary', 'depth', 'normals',
            'numpy', 'ptz', 'mmap', 'scene_meta', 'labeled_image', 'mesh', 'labeled_mesh', 'caption'.
        **kwargs: Additional keyword arguments to pass to the loading method.

    Returns:
        The loaded data in the format returned by the specific loading method.

    Raises:
        ValueError: If the format cannot be inferred from the file extension.
        NotImplementedError: If the specified format is not supported.
        FileExistsError: If the file does not exist.
    """
    load_method = _get_method(fname, format, load=True)
    return load_method(fname, **kwargs)


def store_data(fname, data, format=None, **kwargs):
    """
    Stores data to a file using the appropriate method based on the file format.

    Args:
        fname (str or Path): The filename or path to store data to.
        data: The data to be stored.
        format (str, optional): The format of the data. If None, it will be inferred from the file extension.
        **kwargs: Additional keyword arguments to pass to the storing method.

    Returns:
        The result of the storing method, which may vary depending on the method used.
    """
    store_method = _get_method(fname, format, load=False)
    Path(fname).parent.mkdir(parents=True, exist_ok=True)
    return store_method(fname, data, **kwargs)


def load_modality_data(
    scene_root: Path | str,
    results: dict,
    modality_dict: dict,
    modality: str,
    frame: dict | None = None,
) -> dict:
    """
    Processes a modality by loading data from a specified path and updating the results dictionary.
    This function extracts the format and path from the given modality dictionary, loads the data
    from the specified path, and updates the results dictionary with the loaded data.
    Args:
        scene_root (str or Path): The root directory of the scene where the data is located.
        results (dict): A dictionary to store the loaded modality data and optional frame path.
        modality_dict (dict): A dictionary containing the modality information, including 'format'
            and the path to the data.
        modality (str): The key under which the loaded modality data will be stored in the results.
        frame (dict, optional): A dictionary containing frame information. If provided, that means we are loading
        frame modalities, otherwise it is scene modalities.
    Returns:
        dict: The updated results dictionary containing the loaded modality data.
    """
    modality_format = modality_dict["format"]
    modality_path = [v for k, v in modality_dict.items() if k != "format"][0]
    fname = frame[modality_path] if frame else modality_path
    loaded_modality = load_data(
        Path(scene_root, fname),
        modality_format,
        frame_key=frame["frame_name"] if frame else None,
    )
    results[modality] = loaded_modality
    if frame:
        results[f"{modality}_fname"] = frame[modality_path]
    return results


def load_modality(
    scene_root: Path | str,
    modality_meta: dict,
    modality: str,
    frame: dict | None = None,
) -> dict:
    """
    Loads modality data based on the provided metadata and updates the results dictionary.
    This function navigates through the modality metadata to find the specified modality,
    then loads the data for each modality found.
    Args:
        scene_root (str or Path): The root directory of the scene where the data is located.
        modality_meta (dict): A nested dictionary containing metadata for various modalities.
        modality (str): A string representing the path to the desired modality within the metadata,
            using '/' as a separator for nested keys.
        frame (dict, optional): A dictionary containing frame information. If provided, we are operationg
        on frame modalities, otherwise it is scene modalities.
    Returns:
        dict: A dictionary containing the loaded modality data.
    """
    results = {}
    modality_keys = modality.split("/")
    current_modality = modality_meta
    for key in modality_keys:
        try:
            current_modality = current_modality[key]
        except KeyError as err:
            error_message = f"Modality '{err.args[0]}' not found in modalities metadata. Please verify the scene_meta.json and the provided modalities."
            logger.error(error_message)
            raise KeyError(error_message) from err
    if "format" in current_modality:
        results = load_modality_data(
            scene_root, results, current_modality, modality, frame
        )
    else:
        for key, value in current_modality.items():
            results = load_modality_data(
                scene_root, results, value, f"{modality}/{key}", frame
            )
    return results


def get_frame_index(
    scene_meta: dict,
    frame_key: int | str,
) -> int:
    """
    Returns the frame index from scene_meta based on name or index.

    Args:
        scene_meta: Dictionary containing scene metadata
        frame_key: Either a string (frame name) or integer (frame index)

    Returns:
        Frame index (int)

    Raises:
        ValueError: If frame_key is not a string or integer
    """
    if isinstance(frame_key, str):
        return scene_meta["frame_names"][frame_key]

    if isinstance(frame_key, int):
        return frame_key

    raise ValueError(f"Frame key not supported: {frame_key} ({type(frame_key)})")


def get_frame(scene_meta: dict, frame_key: int | str) -> dict:
    """
    Get a frame from scene_meta based on name or index.

    Args:
        scene_meta: Dictionary containing scene metadata
        frame_key: Either a string (frame name) or integer (frame index)

    Returns:
        The frame data (dict)
    """
    frame_idx = get_frame_index(scene_meta, frame_key)
    return scene_meta["frames"][frame_idx]


def set_frame(
    scene_meta: dict,
    frame_key: int | str,
    new_frame: dict,
    sort: bool = False,
) -> dict:
    """
    Replace a frame in scene_meta with a new frame.

    Args:
        scene_meta: Dictionary containing scene metadata
        frame_key: Either a string (frame name) or integer (frame index)
        new_frame: New frame data to replace the existing frame
        sort: If True, sort the keys in the new_frame dictionary

    Returns:
        Updated scene_meta dictionary
    """
    frame_idx = get_frame_index(scene_meta, frame_key)
    if sort:
        new_frame = {k: new_frame[k] for k in sorted(new_frame)}
    scene_meta["frames"][frame_idx] = new_frame
    return scene_meta


def load_frame(scene_root, frame_key, modalities=None, scene_meta=None):
    if scene_meta is None:
        scene_meta = load_data(Path(scene_root, "scene_meta.json"), "scene_meta")
    frame = get_frame(scene_meta, frame_key)
    # compact, standarized frame representation
    wai_frame = {}
    if "transform_matrix" in frame:
        wai_frame["extrinsics"] = (
            torch.tensor(frame["transform_matrix"]).reshape(4, 4).float()
        )
    camera_model = frame.get(
        "camera_model",
        scene_meta["camera_model"] if "camera_model" in scene_meta else None,
    )
    wai_frame["camera_model"] = camera_model
    if camera_model == "PINHOLE":
        wai_frame["intrinsics"] = convert_camera_coeffs_to_pinhole_matrix(
            scene_meta, frame
        )
    elif camera_model in ["OPENCV", "OPENCV_FISHEYE"]:
        # optional per-frame intrinsics
        for camera_key in CAMERA_KEYS:
            if camera_key in frame:
                wai_frame[camera_key] = float(frame[camera_key])
            elif camera_key in scene_meta:
                wai_frame[camera_key] = float(scene_meta[camera_key])
    else:
        raise NotImplementedError(f"Camera model not supported: {camera_model}")
    wai_frame["w"] = frame.get("w", scene_meta["w"] if "w" in scene_meta else None)
    wai_frame["h"] = frame.get("h", scene_meta["h"] if "h" in scene_meta else None)
    wai_frame["frame_name"] = frame["frame_name"]
    wai_frame["frame_idx"] = get_frame_index(scene_meta, frame_key)

    if modalities is not None:
        if isinstance(modalities, str):
            modalities = [modalities]
        for modality in modalities:
            # Handle regex patterns in modality
            if any(char in modality for char in ".|*+?()[]{}^$\\"):
                # This is a regex pattern
                pattern = re.compile(modality)
                matching_modalities = [
                    m for m in scene_meta["frame_modalities"] if pattern.match(m)
                ]
                if not matching_modalities:
                    raise ValueError(f"No modalities match the pattern: {modality}")
                # Use the first matching modality
                modality = matching_modalities[0]

            modality_meta = scene_meta["frame_modalities"]
            current_modalities = load_modality(
                scene_root, modality_meta, modality, frame
            )
            wai_frame.update(current_modalities)

    return wai_frame


def load_frames(scene_root, frame_keys, modalities=None, scene_meta=None):
    if scene_meta is None:
        scene_meta = load_data(Path(scene_root, "scene_meta.json"), "scene_meta")
    wai_frames = []
    for frame_key in frame_keys:
        wai_frames.append(load_frame(scene_root, frame_key, modalities, scene_meta))
    wai_frames = stack(wai_frames)
    return wai_frames


def load_scene(scene_root, modalities=None, scene_meta=None):
    if scene_meta is None:
        scene_meta = load_data(Path(scene_root, "scene_meta.json"), "scene_meta")

    scene_data = {"meta": scene_meta}
    if modalities is not None:
        if isinstance(modalities, str):
            modalities = [modalities]
        for modality in modalities:
            modality_meta = scene_meta["scene_modalities"]
            current_modalities = load_modality(scene_root, modality_meta, modality)
            scene_data.update(current_modalities)

    return scene_data
