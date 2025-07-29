import gzip
import io
import json
import logging
import os
import random
import subprocess
import time
from pathlib import Path

import numpy as np
import pkg_resources
import torch
import trimesh
from PIL import Image, PngImagePlugin
from plyfile import PlyData, PlyElement
from torchvision.io import decode_image as decode_image_torchvision

from .ops import to_dtype_device
from .semantics import (
    apply_id_to_color_mapping,
    INVALID_ID,
    load_semantic_color_mapping,
)

try:
    import orjson

    ORJSON_AVAILABLE = True
except ImportError:
    import json

    ORJSON_AVAILABLE = False

from datetime import datetime

import cv2
import portalocker
import yaml

# pyre-unsafe
from iopath.common.file_io import PathManagerFactory
from yaml import CLoader

pathmgr = PathManagerFactory.get("wai")

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Try to register the Manifold path handler
try:
    from iopath.fb.gaia import GaiaPathHandler  # type: ignore
    from iopath.fb.manifold import ManifoldPathHandler  # type: ignore

    pathmgr.register_handler(ManifoldPathHandler(num_retries=10))
    pathmgr.register_handler(GaiaPathHandler())

except ImportError:
    pass

WAI_MAIN_PATH = Path(__file__).parent.parent.parent
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

if os.environ.get("DISABLE_IOPATH", "0") == "1":
    _imwrite_cv2 = cv2.imwrite
    _imread_cv2 = cv2.imread
    decode_image = decode_image_torchvision
    path_exists = os.path.exists
else:
    path_exists = pathmgr.exists

    open = pathmgr.open

    def _is_native_path(path: str | os.PathLike) -> bool:
        """
        Determines if a path is a native filesystem path.

        Args:
            path (Union[str, os.PathLike]): The path to check.

        Returns:
            bool: True if the path is a native filesystem path, False if it's handled by a registered path handler.
        """
        # This is based on the logic in iopath's `PathManager.__get_path_handler`
        path = os.fspath(path)
        for p, handler in pathmgr._path_handlers.items():
            if path.startswith(p):
                return False
        return True

    def _imwrite_cv2(fname, data, params=None):
        """
        Writes an image to a file using OpenCV.

        Args:
            fname (str): The filename to save the image to.
            data (numpy.ndarray, torch.tensor): The image data to save. Must be a 2D or 3D array.
            params (list, optional): A list of parameters to pass to the image writer. Defaults to None, which uses 16-bit with zip compression.

        Returns:
            bool: True if succeded
        """
        # If possible, write directly to a native filesystem path.
        # This will be faster for image formats like EXR, for which OpenCV
        # (as of version 4.11) does not support encoding to a memory buffer,
        # and instead saves the image to a temporary file like
        # `/tmp/__opencv_temp.sY7gT5` that is then read into a memory buffer,
        # only to be written to a file again. Clearly that is wasteful.
        if _is_native_path(fname):
            return cv2.imwrite(fname, data, params if params else [])

        with open(fname, "wb") as f:
            retval, buf = cv2.imencode(
                os.path.splitext(fname)[1], data, params if params else []
            )
            f.write(buf)
        return retval

    def _imread_cv2(fname, flags=cv2.IMREAD_COLOR):
        """
        Reads an image from a file using OpenCV.

        Args:
            fname (str): The filename to read the image from.
            flags (int): The flags to pass to the image reader.

        Returns:
            numpy.ndarray: The image data.
        """
        # If possible, read directly from a native filesystem path.
        # This will be faster for image formats like EXR, for which OpenCV
        # (as of version 4.11) does not support decoding from a memory buffer,
        # and instead creates a temporary file like `/tmp/__opencv_temp.sY7gT5`
        # that is then read in again. Clearly that is wasteful.
        if _is_native_path(fname):
            return cv2.imread(fname, flags)

        with open(fname, "rb") as f:
            data = np.asarray(bytearray(f.read()), dtype="uint8")
            return cv2.imdecode(data, flags)

    def decode_image(fname, **kwargs):
        """
        Decodes an image from a file using torchvision.

        Args:
            fname (str): The filename to read the image from.

        Returns:
            torch.Tensor: The image data.
        """
        with open(fname, "rb") as f:
            data = torch.frombuffer(bytearray(f.read()), dtype=torch.uint8)
            return decode_image_torchvision(data, **kwargs)


def _write_exr(fname, data, params=None) -> bool:
    """
    Writes an image as an EXR file using OpenCV.

    Args:
        fname (str): The filename to save the image to.
        data (numpy.ndarray, torch.tensor): The image data to save. Must be a 2D or 3D array.
        params (list, optional): A list of parameters to pass to OpenCV's imwrite function.
            Defaults to None, which uses 16-bit with zip compression.

    Returns:
        bool: True if the image was saved successfully, False otherwise.

    Raises:
        ValueError: If the input data has less than two or more than three dimensions.

    Notes:
        Only 32-bit float (CV_32F) images can be saved. For comparison of different
        compression methods, see P1732924327 [[P1732924327](https://www.internalfb.com/intern/paste/P1732924327)].
        This resource provides benchmarking results for various compression methods,
        including nocompress, rle, piz, pxr24, b44, zips, half-nocompress, half-rle,
        half-piz, half-pxr24, half-zip, and half-zips.
    """
    if params is None:
        # by default use 16-bit with zip compression
        params = [
            cv2.IMWRITE_EXR_TYPE,
            cv2.IMWRITE_EXR_TYPE_HALF,
            cv2.IMWRITE_EXR_COMPRESSION,
            cv2.IMWRITE_EXR_COMPRESSION_ZIP,
        ]
    if Path(fname).suffix != ".exr":
        raise ValueError(
            f"Only filenames with suffix .exr allowed but received: {fname}"
        )
    ## Note: only 32-bit float (CV_32F) images can be saved
    data = to_dtype_device(data, device=np.ndarray, dtype=np.float32)
    if (data.ndim > 3) or (data.ndim < 2):
        raise ValueError(
            f"Image needs to contain two or three dims but received: {data.shape}"
        )

    return _imwrite_cv2(fname, data, params if params else [])


def _read_exr(fname, fmt="torch"):
    """
    Reads an EXR image file using OpenCV.
    Args:
        fname (str): The filename of the EXR image to read.
        fmt (str, optional): The format of the output data. Can be one of:
            - "torch": Returns a PyTorch tensor.
            - "np": Returns a NumPy array.
            - "PIL": Returns a PIL Image object.
            Defaults to "torch".
    Returns:
        The EXR image data in the specified output format.
    Raises:
        NotImplementedError: If the specified output format is not supported.
    Notes:
        The EXR image is read in its original format, without any conversion or rescaling.
    """
    data = _imread_cv2(fname, cv2.IMREAD_UNCHANGED)
    if data is None:
        raise FileNotFoundError(f"Failed to read EXR file: {fname}")
    if fmt == "torch":
        # Convert to PyTorch tensor with float32 dtype
        data = torch.from_numpy(data).float()
    elif fmt == "np":
        # Convert to NumPy array with float32 dtype
        data = np.array(data, dtype=np.float32)
    elif fmt == "PIL":
        # Convert to PIL Image object
        data = Image.fromarray(data)
    else:
        raise NotImplementedError(f"fmt not supported: {fmt}")
    return data


def _store_depth(fname, data, **kwargs) -> bool:
    """
    Stores depth image data in an EXR file.
    Args:
        fname (str): The filename to save the depth image to.
        data (numpy.ndarray, torch.tensor): The depth image data to save.
    Returns:
        bool: True if the depth image was saved successfully, False otherwise.
    Raises:
        ValueError: If the input data does not have two dimensions after removing singleton dimensions.
    """
    data = to_dtype_device(data, device=np.ndarray, dtype=np.float32)
    data = data.squeeze()  # remove all 1-dim entries
    if data.ndim != 2:
        raise ValueError(f"Depth image needs to be 2d, but received: {data.shape}")

    return _write_exr(fname, data)


def _load_depth(fname, fmt="torch", **kwargs):
    """
    Loads a depth image from an EXR file.
    Args:
        fname (str): The filename of the EXR file to load.
        fmt (str, optional): The format of the output data. Can be one of:
            - "torch": Returns a PyTorch tensor.
            - "np": Returns a NumPy array.
            - "PIL": Returns a PIL Image object.
            Defaults to "torch".
    Returns:
        The loaded depth image in the specified output format.
    Raises:
        ValueError: If the loaded depth image does not have two dimensions.
    Notes:
        This function assumes that the EXR file contains a single-channel depth image.
    """
    data = _read_exr(fname, fmt)
    if (fmt != "PIL") and (data.ndim != 2):
        raise ValueError(f"Depth image needs to be 2d, but loaded: {data.shape}")
    return data


def _store_normals(fname, data, **kwargs) -> bool:
    """
    Stores a normals image in an EXR file.

    Args:
        fname (str): The filename to save the normals image to.
        data (numpy.ndarray): The normals image data to save. Will be converted to a 32-bit float array.

    Returns:
        bool: True if the normals image was saved successfully, False otherwise.

    Raises:
        ValueError: If the input data has more than three dimensions after removing singleton dimensions.
        ValueError: If the input data does not have exactly three channels.
        ValueError: If the input data is not normalized (i.e., maximum absolute value exceeds 1).

    Notes:
        This function assumes that the input data is in HWC (height, width, channels) format.
        If the input data is in CHW (channels, height, width) format, it will be automatically transposed to HWC.
    """
    data = to_dtype_device(data, device=np.ndarray, dtype=np.float32)
    data = data.squeeze()  # remove all singleton dimensions
    if data.ndim != 3:
        raise ValueError(f"Normals image needs to be 3-dim but received: {data.shape}")
    if (data.shape[0] == 3) and (data.shape[2] != 3):
        # ensure HWC format
        data = data.transpose(1, 2, 0)
    if data.shape[2] != 3:
        raise ValueError(
            f"Normals image needs have 3 channels but received: {data.shape}"
        )
    if not np.allclose(np.linalg.norm(data, axis=-1), 1.0):
        raise ValueError("Normals image must be normalized")

    return _write_exr(fname, data)


def _load_normals(fname, fmt="torch", **kwargs):
    """
    Loads a normals image from an EXR file.
    Args:
        fname (str): The filename of the EXR file to load.
        fmt (str, optional): The format of the output data. Can be one of:
            - "torch": Returns a PyTorch tensor.
            - "np": Returns a NumPy array.
            - "PIL": Returns a PIL Image object.
            Defaults to "torch".
    Returns:
        The loaded normals image in the specified output format.
    Raises:
        Warning: If the loaded normals image has more than two dimensions.
    Notes:
        This function assumes that the EXR file contains a 3-channel normals image.
    """
    data = _read_exr(fname, fmt)
    if data.ndim != 3:
        raise ValueError(f"Normals image needs to be 3-dim but received: {data.shape}")
    if data.shape[2] != 3:
        raise ValueError(
            f"Normals image needs have 3 channels but received: {data.shape}"
        )
    return data


def _load_readable(
    fname: Path | str, max_retries=5, retry_delay=0.2, load_as_string=False, **kwargs
):
    """
    Loads data from a human-readable file (JSON or YAML) with file locking.

    Args:
        fname (Path or str): The filename to load data from.
        max_retries (int, optional): Maximum number of retries if file is locked.
            Defaults to 5.
        retry_delay (float, optional): Base delay between retries in seconds.
            Defaults to 0.2.
        load_as_string (bool, optional): Whether to return the loaded data as string.
            Defaults to False.

    Returns:
        The loaded data, which can be any type of object that can be represented in JSON or YAML.

    Raises:
        NotImplementedError: If the file suffix is not supported (i.e., not .json, .yaml, or .yml).
        RuntimeError: If unable to acquire a lock on the file after max_retries.
    """
    fname = Path(fname)
    if not fname.exists():
        raise FileExistsError(f"File does not exist: {fname}")

    retries = 0

    while retries < max_retries:
        try:
            if fname.suffix == ".json":
                # Use shared lock for reading
                with portalocker.Lock(
                    fname, mode="rb", flags=portalocker.LOCK_SH, timeout=0
                ) as f:
                    try:
                        if load_as_string:
                            return f.read().decode("utf-8")
                        if ORJSON_AVAILABLE:
                            return orjson.loads(f.read())
                        return json.load(f)
                    finally:
                        pass  # portalocker automatically releases the lock

            elif fname.suffix in [".yaml", ".yml"]:
                with portalocker.Lock(
                    fname,
                    mode="r",
                    encoding="utf-8",
                    flags=portalocker.LOCK_SH,
                    timeout=0,
                ) as f:
                    try:
                        if load_as_string:
                            return f.read()
                        return yaml.load(f, Loader=CLoader)
                    finally:
                        pass  # portalocker automatically releases the lock
            else:
                raise NotImplementedError(
                    f"Readable format not supported: {fname.suffix}"
                )

        except (IOError, BlockingIOError):
            # File is locked by another process, retry after delay
            retries += 1
            # Add jitter to avoid lock contention
            time.sleep(retry_delay + random.uniform(0, 0.1) * retries)

    # If we get here, we've exceeded max retries
    raise RuntimeError(
        f"Failed to read file {fname} after {max_retries} attempts due to file lock contention"
    )


def _store_readable(fname: Path | str, data, max_retries=5, retry_delay=0.2, **kwargs):
    """
    Stores data in a human-readable file (JSON or YAML) with file locking.

    Args:
        fname (Path or str): The filename to store data in.
        data: The data to store, which can be any type of object that can be represented in JSON or YAML.
        max_retries (int, optional): Maximum number of retries if file is locked.
            Defaults to 5.
        retry_delay (float, optional): Base delay between retries in seconds.
            Defaults to 0.2.

    Returns:
        The number of bytes written to the file.

    Raises:
        NotImplementedError: If the file suffix is not supported (i.e., not .json, .yaml, or .yml).
        RuntimeError: If unable to acquire a lock on the file after max_retries.
    """
    fname = Path(fname)
    retries = 0

    # Create parent directory if it doesn't exist
    os.makedirs(fname.parent, exist_ok=True)

    while retries < max_retries:
        try:
            if fname.suffix == ".json":
                if ORJSON_AVAILABLE:
                    # For orjson, we need to write in binary mode
                    with portalocker.Lock(
                        fname, mode="wb", flags=portalocker.LOCK_EX, timeout=0
                    ) as f:
                        try:
                            return f.write(
                                orjson.dumps(data, option=orjson.OPT_INDENT_2)
                            )
                        finally:
                            pass  # portalocker automatically releases the lock
                else:
                    # For standard json, we write in text mode
                    with portalocker.Lock(
                        fname,
                        mode="w",
                        encoding="utf-8",
                        flags=portalocker.LOCK_EX,
                        timeout=0,
                    ) as f:
                        try:
                            json.dump(data, f, indent=2)
                            return f.tell()
                        finally:
                            pass  # portalocker automatically releases the lock

            elif fname.suffix in [".yaml", ".yml"]:
                with portalocker.Lock(
                    fname,
                    mode="w",
                    encoding="utf-8",
                    flags=portalocker.LOCK_EX,
                    timeout=0,
                ) as f:
                    try:
                        yaml.dump(data, f)
                        return f.tell()
                    finally:
                        pass  # portalocker automatically releases the lock
            else:
                raise NotImplementedError(
                    f"Readable format not supported: {fname.suffix}"
                )

        except (IOError, BlockingIOError):
            # File is locked by another process, retry after delay
            retries += 1
            # Add jitter to avoid lock contention
            time.sleep(retry_delay + random.uniform(0, 0.1) * retries)

    # If we get here, we've exceeded max retries
    raise RuntimeError(
        f"Failed to write to file {fname} after {max_retries} attempts due to file lock contention"
    )


def _store_scene_meta(fname, scene_meta, **kwargs):
    """
    Stores scene metadata in a readable file.

    Args:
        fname (str): The filename to store the scene metadata in.
        scene_meta (dict): The scene metadata to store.

    Notes:
        This function updates the "last_modified" field of the scene metadata to the current date and time before storing it.
        It also removes the "frame_names" field from the scene metadata, as it is not necessary to store this information.
        Creates a backup of the existing file before overwriting it.
    """
    # update the modified date
    scene_meta["last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "frame_names" in scene_meta:
        del scene_meta["frame_names"]

    # create/overwrite backup
    fname_path = Path(fname)
    if fname_path.exists():
        backup_fname = fname_path.parent / f"_{fname_path.stem}_backup.json"
        if backup_fname.exists():
            backup_fname.unlink()
        fname_path.rename(backup_fname)

    _store_readable(fname, scene_meta)


def _load_scene_meta(fname: Path | str, **kwargs):
    """
    Loads scene metadata from a readable file.

    Args:
        fname (str): The filename to load the scene metadata from.

    Returns:
        dict: The loaded scene metadata, including an additional "frame_names" field that maps frame names to their indices.

    Notes:
        This function creates the "frame_names" field in the scene metadata for efficient lookup of frame indices by name.
    """
    scene_meta = _load_readable(fname)
    # create the frame_name -> frame_idx for efficiency
    scene_meta["frame_names"] = {
        frame["frame_name"]: frame_idx
        for frame_idx, frame in enumerate(scene_meta["frames"])
    }
    return scene_meta


def _load_image(fname, fmt="torch", resize=None, **kwargs):
    """
    Loads an image from a file.
    Args:
        fname (str): The filename to load the image from.
        fmt (str, optional): The format of the output data. Can be one of:
            - "torch": Returns a PyTorch tensor with shape (C, H, W).
            - "np": Returns a NumPy array with shape (H, W, C).
            - "pil": Returns a PIL Image object.
            Defaults to "torch".
        resize (tuple, optional): A tuple of two integers representing the desired width and height of the image.
            If None, the image is not resized. Defaults to None.
    Returns:
        The loaded image in the specified output format.
    Raises:
        NotImplementedError: If the specified output format is not supported.
    Notes:
        This function loads non-binary images in RGB mode and normalizes pixel values to the range [0, 1].
    """

    # Fastest way to load into torch tensor
    if resize is None and fmt == "torch":
        return decode_image(fname).float() / 255.0

    # Load using PIL
    with open(fname, "rb") as f:
        pil_image = Image.open(f)
        pil_image.load()
        if pil_image.mode not in ["RGB", "RGBA"]:
            raise OSError(
                f"Expected a RGB or RGBA image in {fname}, but instead found an image with mode {pil_image.mode}"
            )
        if resize is not None:
            pil_image = pil_image.resize(resize)
        if fmt == "torch":
            return (
                torch.from_numpy(np.array(pil_image)).permute(2, 0, 1).float() / 255.0
            )
        elif fmt == "np":
            return np.array(pil_image) / 255.0
        elif fmt == "pil":
            return pil_image
        else:
            raise NotImplementedError(f"Image format not supported: {fmt}")


def _store_image(fname, img_data, **kwargs):
    """
    Stores an image in a file.
    Args:
        fname (str): The filename to store the image in.
        img_data (numpy.ndarray, torch.tensor or PIL.Image.Image): The image data to store.
    Notes (for numpy.ndarray or torch.tensor inputs):
        This function assumes that the input image data is in the range [0, 1] and has shape (H, W, C) or (C, H, W).
        It converts the image data to uint8 format and saves it as a compressed image file.
    """
    img_data = to_dtype_device(img_data, device=np.ndarray, dtype=np.float32)
    if not isinstance(img_data, Image.Image):
        img_data = Image.fromarray((255 * img_data).round().astype(np.uint8))
    with open(fname, "wb") as f:
        img_data.save(f, compress_level=1, optimize=False)


def _load_binary_mask(fname, fmt="torch", resize=None, **kwargs):
    """
    Loads a binary image from a file.
    Args:
        fname (str): The filename to load the binary image from.
        fmt (str, optional): The format of the output data. Can be one of:
            - "torch": Returns a PyTorch boolean tensor with shape H x W.
            - "np": Returns a NumPy boolean array with shape H x W.
            - "pil": Returns a PIL Image object.
            Defaults to "torch".
        resize (tuple, optional): A tuple of two integers representing the desired width and height of the binary image.
            If None, the image is not resized. Defaults to None.
    Returns:
        The loaded binary image in the specified output format.
    Raises:
        NotImplementedError: If the specified output format is not supported.
    """
    if fmt not in ["pil", "np", "torch"]:
        raise NotImplementedError(f"Image format not supported: {fmt}")

    with open(fname, "rb") as f:
        pil_image = Image.open(f)
        pil_image.load()

        if pil_image.mode == "L":
            pil_image = pil_image.convert("1")

        elif pil_image.mode != "1":
            raise OSError(
                f"Expected a binary or grayscale image in {fname}, but instead found an image with mode {pil_image.mode}"
            )

        if resize is not None:
            pil_image = pil_image.resize(resize)

        if fmt == "pil":
            return pil_image

        mask = np.array(pil_image, copy=True)
        return mask if fmt == "np" else torch.from_numpy(mask)


def _store_binary_mask(fname, img_data, **kwargs):
    """
    Stores a binary image in a compressed image file.
    Args:
        fname (str): The filename to store the binary image in.
        img_data (numpy.ndarray, torch.tensor or PIL.Image.Image): The binary image data to store.
    """
    if isinstance(img_data, Image.Image):
        if img_data.mode not in ["1", "L"]:
            raise RuntimeError(
                f'Expected a PIL image with mode "1" or "L", but instead got a PIL image with mode {img_data.mode}'
            )
    elif isinstance(img_data, np.ndarray) or isinstance(img_data, torch.Tensor):
        if len(img_data.squeeze().shape) != 2:
            raise RuntimeError(
                f"Expected a PyTorch tensor or NumPy array with shape (H, W, 1), (1, H, W) or (H, W), but the shape is {img_data.shape}"
            )
        img_data = img_data.squeeze()
    else:
        raise NotImplementedError(f"Input format not supported: {type(img_data)}")

    if not isinstance(img_data, Image.Image):
        img_data = to_dtype_device(img_data, device=np.ndarray, dtype=bool)
        img_data = Image.fromarray(img_data)

    img_data = img_data.convert("1")
    with open(fname, "wb") as f:
        img_data.save(f, compress_level=1, optimize=False)


def _load_numpy(fname, allow_pickle=False, **kwargs):
    """
    Loads a NumPy array from a file.

    Args:
        fname (str): The filename to load the NumPy array from.
        allow_pickle (bool, optional): Whether to allow pickled objects in the NumPy file.
            Defaults to False.

    Returns:
        numpy.ndarray: The loaded NumPy array.

    Raises:
        NotImplementedError: If the file suffix is not supported (i.e., not .npy or .npz).

    Notes:
        This function supports loading NumPy arrays from .npy and .npz files.
        For .npz files, it assumes that the array is stored under the key "arr_0".
    """
    fname = Path(fname)
    with open(fname, "rb") as fid:
        if fname.suffix == ".npy":
            return np.load(fid, allow_pickle=allow_pickle)
        elif fname.suffix == ".npz":
            return np.load(fid, allow_pickle=allow_pickle).get("arr_0")
        else:
            raise NotImplementedError(f"Numpy format not supported: {fname.suffix}")


def _store_numpy(fname, data, **kwargs):
    """
    Stores a NumPy array in a file.

    Args:
        fname (str): The filename to store the NumPy array in.
        data (numpy.ndarray): The NumPy array to store.

    Raises:
        NotImplementedError: If the file suffix is not supported (i.e., not .npy or .npz).

    Notes:
        This function supports storing NumPy arrays in .npy and .npz files.
        For .npz files, it uses compression to reduce the file size.
    """
    fname = Path(fname)
    with open(fname, "wb") as fid:
        if fname.suffix == ".npy":
            np.save(fid, data)
        elif fname.suffix == ".npz":
            np.savez_compressed(fid, arr_0=data)
        else:
            raise NotImplementedError(f"Numpy format not supported: {fname.suffix}")


def _store_mmap(fname, data, **kwargs):
    """
    Stores matrix-shaped data in a memory-mapped file.

    Args:
        fname (str): The filename to store the data in.
        data (numpy.ndarray): The matrix-shaped data to store.

    Returns:
        str: The name of the stored memory-mapped file.

    Notes:
        This function stores the data in a .npy file with a modified filename that includes the shape of the data.
        The data is converted to float32 format before storing.
    """
    fname = Path(fname)
    # add dimensions to the file name for loading
    data = to_dtype_device(data, device=np.ndarray, dtype=np.float32)
    shape_string = "x".join([str(dim) for dim in data.shape])
    mmap_name = f"{fname.stem}--{shape_string}.npy"
    with open(fname.parent / mmap_name, "wb") as fid:
        np.save(fid, data)
    return mmap_name


def _load_mmap(fname, **kwargs):
    """
    Loads matrix-shaped data from a memory-mapped file.

    Args:
        fname (str): The filename of the memory-mapped file to load.

    Returns:
        numpy.memmap: A memory-mapped array containing the loaded data.

    Notes:
        This function assumes that the filename contains the shape of the data, separated by 'x' or ','.
        It uses this information to create a memory-mapped array with the correct shape.
    """
    shape_string = Path(Path(fname).name.split("--")[1]).stem
    shape = [int(dim) for dim in shape_string.replace(",", "x").split("x")]
    with open(fname, "rb") as fid:
        return np.memmap(fid, dtype=np.float32, mode="r", shape=shape, offset=128)


def _load_ptz(fname, **kwargs):
    """
    Loads a PyTorch tensor from a PTZ file.

    Args:
        fname (str): The filename to load the tensor from.

    Returns:
        torch.Tensor: The loaded PyTorch tensor.

    Notes:
        This function assumes that the PTZ file contains a PyTorch tensor saved using `torch.save`.
        If the tensor was saved in a different format, this function may fail.
    """
    with open(fname, "rb") as fid:
        data = gzip.decompress(fid.read())
        ## Note: if the following line fails, save PyTorch tensors in PTZ instead of NumPy
        return torch.load(io.BytesIO(data), map_location="cpu", weights_only=True)


def _store_ptz(fname, data, **kwargs):
    """
    Stores a PyTorch tensor in a PTZ file.

    Args:
        fname (str): The filename to store the tensor in.
        data (torch.Tensor): The PyTorch tensor to store.

    Notes:
        This function saves the tensor using `torch.save` and compresses it using gzip.
    """
    with open(fname, "wb") as fid:
        with gzip.open(fid, "wb") as gfid:
            torch.save(data, gfid)


def _load_labeled_image(fname, fmt="torch", resize=None, **kwargs):
    """
    Loads a labeled image from a PNG file.
    Args:
        fname (str): The filename to load the image from.
        fmt (str, optional): The format of the output data. Can be one of:
            - "torch": Returns a PyTorch int32 tensor with shape (H, W).
            - "np": Returns a NumPy int32 array with shape (H, W).
            - "pil": Returns a PIL Image object.
            Defaults to "torch".
        resize (tuple, optional): A tuple of two integers representing the desired width and height of the image.
            If None, the image is not resized. Defaults to None.
    Returns:
        The loaded image in the specified output format.
    Raises:
        NotImplementedError: If the specified output format is not supported.
        RuntimeError: If the 'id_to_color_mapping' is missing in the PNG metadata.
    Notes:
        The function expects the PNG file to contain metadata with a key 'id_to_color_mapping',
        which maps from label ids to tuples of RGB values.
    """
    with open(fname, "rb") as f:
        pil_image = Image.open(f)
        pil_image.load()
        if pil_image.mode != "RGB":
            raise OSError(
                f"Expected a RGB image in {fname}, but instead found an image with mode {pil_image.mode}"
            )

        # Load id to RGB mapping
        color_palette_json = pil_image.info.get("id_to_color_mapping", None)
        if color_palette_json is None:
            raise RuntimeError("'id_to_color_mapping' is missing in the PNG metadata.")
        color_palette = json.loads(color_palette_json)
        color_to_id_mapping = {
            tuple(color): int(id) for id, color in color_palette.items()
        }

        if resize is not None:
            pil_image = pil_image.resize(resize, Image.NEAREST)

    if fmt == "pil":
        return pil_image

    # Reverse the color mapping: map from RGB colors to ids
    img_data = np.array(pil_image)

    # Create a lookup table for fast mapping
    max_color_value = 256  # Assuming 8-bit per channel
    lookup_table = np.full(
        (max_color_value, max_color_value, max_color_value),
        INVALID_ID,
        dtype=np.int32,
    )
    for color, id in color_to_id_mapping.items():
        lookup_table[color] = id
    # Map colors to ids using the lookup table
    img_data = lookup_table[img_data[..., 0], img_data[..., 1], img_data[..., 2]]

    if fmt == "np":
        return img_data
    elif fmt == "torch":
        return torch.from_numpy(img_data)
    else:
        raise NotImplementedError(f"Image format not supported: {fmt}")


def _store_labeled_image(
    fname,
    img_data,
    semantic_color_mapping: np.ndarray | None = None,
    **kwargs,
):
    """
    Stores a labeled image as a uint8 RGB PNG file.
    Args:
        fname (str): The filename to store the image in.
        img_data (numpy.ndarray, torch.Tensor or PIL.Image.Image): The per-pixel label ids to store.
        semantic_color_mapping (np.ndarray): Optional, preloaded NumPy array of semantic colors.
    Raises:
        ValueError: If the file suffix is not supported (i.e., not .png).
        RuntimeError: If the type of the image data is different from uint16, int16 or int32.
    Notes:
        The function takes an image with per-pixel label ids and converts it into an RGB image
        using a specified mapping from label ids to RGB colors. The resulting image is saved as
        a PNG file, with the mapping stored as metadata.
    """
    if Path(fname).suffix != ".png":
        raise ValueError(
            f"Only filenames with suffix .png allowed but received: {fname}"
        )

    if isinstance(img_data, Image.Image) and img_data.mode != "I;16":
        raise RuntimeError(
            f"The provided image does not seem to be a labeled image. The provided PIL image has mode {img_data.mode}."
        )

    if isinstance(img_data, np.ndarray) and img_data.dtype not in [
        np.uint16,
        np.int16,
        np.int32,
    ]:
        raise RuntimeError(
            f"The provided NumPy array has type {img_data.dtype} but the expected type is np.uint16, np.int16 or np.int32."
        )

    if isinstance(img_data, torch.Tensor):
        if img_data.dtype not in [torch.uint16, torch.int16, torch.int32]:
            raise RuntimeError(
                f"The provided PyTorch tensor has type {img_data.dtype} but the expected type is torch.uint16, torch.int16 or torch.int32."
            )
        img_data = img_data.numpy()

    if semantic_color_mapping is None:
        # Mapping from ids to colors not provided, load it now
        semantic_color_mapping = load_semantic_color_mapping()

    img_data, color_palette = apply_id_to_color_mapping(
        img_data, semantic_color_mapping
    )
    pil_image = Image.fromarray(img_data, "RGB")

    # Create a PngInfo object to store metadata
    meta = PngImagePlugin.PngInfo()
    meta.add_text("id_to_color_mapping", json.dumps(color_palette))

    pil_image.save(fname, pnginfo=meta)


def _load_labeled_mesh(file_path, fmt="torch", palette="rgb", **kwargs):
    """
    Loads a mesh from a labeled mesh file (PLY binary format).

    Args:
        file_path (str): The path to the labeled mesh file (.ply).
        fmt (str, optional): Output format of the mesh data. Can be one of:
            - "torch": Returns a dict of PyTorch tensors containing mesh data.
            - "np": Returns a dict of NumPy arrays containing mesh data.
            - "trimesh": Returns a trimesh mesh object.
            Defaults to "torch".
        palette (str, optional): Output color of the trimesh mesh data. Can be one of:
            - "rgb": Colors the mesh with original rgb colors
            - "semantic_class": Colors the mesh with semantic class colors
            - "instance": Colors the mesh with semantic instance colors
            Applied only when fmt is "trimesh".
    Returns:
        The loaded mesh in the specified output format.
    Raises:
        NotImplementedError: If the specified output format is not supported.

    Notes:
        This function reads a binary PLY file with vertex position, color, and optional
        semantic class and instance IDs. The faces are stored as lists of vertex indices.
    """
    # load data (NOTE: define known_list_len to enable faster read)
    ply_data = PlyData.read(file_path, known_list_len={"face": {"vertex_indices": 3}})

    # get vertices
    vertex_data = ply_data["vertex"].data
    vertices = np.column_stack(
        (vertex_data["x"], vertex_data["y"], vertex_data["z"])
    ).astype(np.float32)

    # initialize output data
    mesh_data = {}
    mesh_data["is_labeled_mesh"] = True
    mesh_data["vertices"] = vertices

    # get faces if available
    if "face" in ply_data:
        faces = np.asarray(ply_data["face"].data["vertex_indices"]).astype(np.int32)
        mesh_data["faces"] = faces

    # get rgb colors if available
    if all(color in vertex_data.dtype.names for color in ["red", "green", "blue"]):
        vertices_color = np.column_stack(
            (vertex_data["red"], vertex_data["green"], vertex_data["blue"])
        ).astype(np.uint8)
        mesh_data["vertices_color"] = vertices_color

    # get vertices class and instance if available
    if "semantic_class_id" in vertex_data.dtype.names:
        vertices_class = vertex_data["semantic_class_id"].astype(np.int32)
        mesh_data["vertices_semantic_class_id"] = vertices_class

    if "instance_id" in vertex_data.dtype.names:
        vertices_instance = vertex_data["instance_id"].astype(np.int32)
        mesh_data["vertices_instance_id"] = vertices_instance

    # get class colors if available
    if all(
        color in vertex_data.dtype.names
        for color in [
            "semantic_class_red",
            "semantic_class_green",
            "semantic_class_blue",
        ]
    ):
        vertices_semantic_class_color = np.column_stack(
            (
                vertex_data["semantic_class_red"],
                vertex_data["semantic_class_green"],
                vertex_data["semantic_class_blue"],
            )
        ).astype(np.uint8)
        mesh_data["vertices_semantic_class_color"] = vertices_semantic_class_color

    # get instance colors if available
    if all(
        color in vertex_data.dtype.names
        for color in ["instance_red", "instance_green", "instance_blue"]
    ):
        vertices_instance_color = np.column_stack(
            (
                vertex_data["instance_red"],
                vertex_data["instance_green"],
                vertex_data["instance_blue"],
            )
        ).astype(np.uint8)
        mesh_data["vertices_instance_color"] = vertices_instance_color

    # convert data into output format (if needed)
    if fmt == "np":
        return mesh_data
    elif fmt == "torch":
        return {k: torch.tensor(v) for k, v in mesh_data.items()}
    elif fmt == "trimesh":
        trimesh_mesh = trimesh.Trimesh(
            vertices=mesh_data["vertices"], faces=mesh_data["faces"]
        )
        # color the mesh according to the palette
        if palette == "rgb":
            # original rgb colors
            if "vertices_color" in mesh_data:
                trimesh_mesh.visual.vertex_colors = mesh_data["vertices_color"]
            else:
                raise ValueError(
                    f"Palette {palette} could not be applied. Missing vertices_color in mesh data."
                )
        elif palette == "semantic_class":
            # semantic class colors
            if "vertices_semantic_class_color" in mesh_data:
                trimesh_mesh.visual.vertex_colors = mesh_data[
                    "vertices_semantic_class_color"
                ]
            else:
                raise ValueError(
                    f"Palette {palette} could not be applied. Missing vertices_semantic_class_color in mesh data."
                )
        elif palette == "instance":
            # semantic instance colors
            if "vertices_instance_color" in mesh_data:
                trimesh_mesh.visual.vertex_colors = mesh_data["vertices_instance_color"]
            else:
                raise ValueError(
                    f"Palette {palette} could not be applied. Missing vertices_instance_color in mesh data."
                )
        else:
            raise ValueError(f"Invalid palette: {palette}.")
        return trimesh_mesh
    else:
        raise NotImplementedError(f"Labeled mesh format not supported: {fmt}")


def _store_labeled_mesh(file_path, mesh_data, **kwargs):
    """
    Stores a mesh in WAI format (PLY binary format).

    Args:
        file_path (str): The filename to store the mesh in.
        mesh_data (dict): Dictionary containing mesh data with keys:
            - 'vertices' (numpy.ndarray): Array of vertex coordinates with shape (N, 3).
            - 'faces' (numpy.ndarray, optional): Array of face indices.
            - 'vertices_color' (numpy.ndarray, optional): Array of vertex colors with shape (N, 3).
            - 'vertices_semantic_class_id' (numpy.ndarray, optional): Array of semantic classes for each vertex with shape (N).
            - 'vertices_instance_id' (numpy.ndarray, optional): Array of instance IDs for each vertex with shape (N).
            - 'vertices_semantic_class_color' (numpy.ndarray, optional): Array of vertex semantic class colors with shape (N, 3).
            - 'vertices_instance_color' (numpy.ndarray, optional): Array of vertex instance colors with shape (N, 3).

    Notes:
        This function writes a binary PLY file with vertex position, color, and optional
        semantic class and instance IDs. The faces are stored as lists of vertex indices.
    """
    # Validate input data
    if "vertices" not in mesh_data:
        raise ValueError("Mesh data must contain 'vertices'")

    # create vertex data with properties
    vertex_dtype = [("x", "f4"), ("y", "f4"), ("z", "f4")]
    if "vertices_color" in mesh_data:
        vertex_dtype.extend([("red", "u1"), ("green", "u1"), ("blue", "u1")])
    if "vertices_semantic_class_id" in mesh_data:
        vertex_dtype.append(("semantic_class_id", "i4"))
    if "vertices_instance_id" in mesh_data:
        vertex_dtype.append(("instance_id", "i4"))
    if "vertices_semantic_class_color" in mesh_data:
        vertex_dtype.extend(
            [
                ("semantic_class_red", "u1"),
                ("semantic_class_green", "u1"),
                ("semantic_class_blue", "u1"),
            ]
        )
    if "vertices_instance_color" in mesh_data:
        vertex_dtype.extend(
            [("instance_red", "u1"), ("instance_green", "u1"), ("instance_blue", "u1")]
        )
    vertex_count = len(mesh_data["vertices"])
    vertex_data = np.zeros(vertex_count, dtype=vertex_dtype)

    # vertex positions
    vertex_data["x"] = mesh_data["vertices"][:, 0]
    vertex_data["y"] = mesh_data["vertices"][:, 1]
    vertex_data["z"] = mesh_data["vertices"][:, 2]

    # vertex colors
    if "vertices_color" in mesh_data:
        vertex_data["red"] = mesh_data["vertices_color"][:, 0]
        vertex_data["green"] = mesh_data["vertices_color"][:, 1]
        vertex_data["blue"] = mesh_data["vertices_color"][:, 2]

    # vertex class
    if "vertices_semantic_class_id" in mesh_data:
        vertex_data["semantic_class_id"] = mesh_data["vertices_semantic_class_id"]

    # vertex instance
    if "vertices_instance_id" in mesh_data:
        vertex_data["instance_id"] = mesh_data["vertices_instance_id"]

    # vertex class colors
    if "vertices_semantic_class_color" in mesh_data:
        vertex_data["semantic_class_red"] = mesh_data["vertices_semantic_class_color"][
            :, 0
        ]
        vertex_data["semantic_class_green"] = mesh_data[
            "vertices_semantic_class_color"
        ][:, 1]
        vertex_data["semantic_class_blue"] = mesh_data["vertices_semantic_class_color"][
            :, 2
        ]

    # vertex instance colors
    if "vertices_instance_color" in mesh_data:
        vertex_data["instance_red"] = mesh_data["vertices_instance_color"][:, 0]
        vertex_data["instance_green"] = mesh_data["vertices_instance_color"][:, 1]
        vertex_data["instance_blue"] = mesh_data["vertices_instance_color"][:, 2]

    # initialize data to save
    vertex_element = PlyElement.describe(vertex_data, "vertex")
    data_to_save = [vertex_element]

    # faces data
    if "faces" in mesh_data:
        face_dtype = [("vertex_indices", "i4", (3,))]
        face_data = np.zeros(len(mesh_data["faces"]), dtype=face_dtype)
        face_data["vertex_indices"] = mesh_data["faces"]
        face_element = PlyElement.describe(face_data, "face")
        data_to_save.append(face_element)

    # Create and write a binary PLY file
    ply_data = PlyData(data_to_save, text=False)
    ply_data.write(file_path)


def _load_generic_mesh(mesh_path, **kwargs):
    """Load mesh with the trimesh library.

    Args:
        mesh_path (str): Path to the mesh file

    Returns:
        The trimesh object from trimesh.load().

    Raises:
        ValueError: If the file format is not supported.
    """

    # needed to load big texture files
    Image.MAX_IMAGE_PIXELS = None

    # load mesh with trimesh
    mesh_data = trimesh.load(mesh_path, process=False)

    return mesh_data


def _store_generic_mesh(file_path, mesh_data, **kwargs):
    """
    Dummy function for storing generic mesh data.

    Args:
        file_path (str): The filename to store the mesh in.
        mesh_data (dict): Dictionary containing mesh data.
        **kwargs: Additional keyword arguments.

    Raises:
        NotImplementedError: This function is not implemented yet.
    """
    raise NotImplementedError("Storing generic meshes is not implemented yet.")


def _load_caption(fname: Path | str, **kwargs) -> str:
    """
    Loads a single caption from a file containing multiple captions.
    Args:
        fname (Path or str): The filename to load the caption from.
        **kwargs: Additional keyword arguments. Currently supported:
            - frame_key (int): The key of the caption to load.
    Returns:
        The loaded caption.
    Raises:
        KeyError: If the specified frame_key is not found in the captions.
    """
    captions = _load_readable(fname)
    return captions[kwargs.get("frame_key")]


def _store_caption(
    fname: Path | str, caption: dict, max_retries=5, retry_delay=0.2, **kwargs
):
    """
    Stores a single caption in a file, updating any existing captions.
    Args:
        fname (Path or str): The filename to store the caption in.
        caption (dict): A dictionary containing a single caption, where the key is the frame_key and the value is the caption text.
            Example: {"92425667": "A living room and kitchen area in a home."}
        max_retries (int, optional): The maximum number of retries if the file is locked by another process. Defaults to 5.
        retry_delay (float, optional): The base delay between retries in seconds. Defaults to 0.2.
    Returns:
        The number of bytes written to the file.
    Raises:
        IOError: If an I/O error occurs while writing to the file.
        BlockingIOError: If the file is locked by another process and the maximum number of retries is exceeded.
    """
    fname = Path(fname)
    try:
        data = _load_readable(fname)
    except FileExistsError:
        data = {}

    data.update(caption)

    retries = 0
    # Create parent directory if it doesn't exist
    os.makedirs(fname.parent, exist_ok=True)

    while retries < max_retries:
        try:
            if ORJSON_AVAILABLE:
                # For orjson, we need to write in binary mode
                with portalocker.Lock(
                    fname, mode="wb", flags=portalocker.LOCK_EX, timeout=0
                ) as f:
                    try:
                        return f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
                    finally:
                        pass  # portalocker automatically releases the lock
        except (IOError, BlockingIOError):
            # File is locked by another process, retry after delay
            retries += 1
            # Add jitter to avoid lock contention
            time.sleep(retry_delay + random.uniform(0, 0.1) * retries)


def get_processing_state(scene_root: Path | str, max_retries=5, retry_delay=0.2):
    """
    Retrieves the processing state of a scene with file locking.

    Args:
        scene_root (Path or str): The root directory of the scene.
        max_retries (int, optional): Maximum number of retries if file is locked.
            Defaults to 5.
        retry_delay (float, optional): Base delay between retries in seconds.
            Defaults to 0.2.

    Returns:
        dict: A dictionary containing the processing state of the scene.
            If no processing log exists, an empty dictionary is returned.

    Notes:
        This function uses file locking to safely read the processing log file
        even when multiple processes are accessing it concurrently.
    """
    process_log_path = Path(scene_root) / "_process_log.json"
    if path_exists(process_log_path):
        try:
            # Use _load_readable which already implements file locking
            process_log = _load_readable(
                process_log_path, max_retries=max_retries, retry_delay=retry_delay
            )
        except Exception:
            logger.error(f"Could not parse: {process_log_path}")
            process_log = {}
    else:
        process_log = {}
    return process_log


def _get_method(fname: Path | str, format=None, load=True):
    """
    Returns a method for loading or storing data in a specific format.
    Args:
        fname (Path or str): The filename to load or store data from/to.
        format (str, optional): The format of the data. If None, it will be inferred from the file extension.
            Defaults to None.
        load (bool, optional): Whether to return a method for loading or storing data.
            Defaults to True.
    Returns:
        callable: A method for loading or storing data in the specified format.
    Raises:
        ValueError: If the format cannot be inferred from the file extension.
        NotImplementedError: If the specified format is not supported.
    Notes:
        This function supports various formats, including readable files (JSON, YAML), images, NumPy arrays,
        PyTorch tensors, memory-mapped files, and scene metadata.
    """
    fname = Path(fname)
    if format is None:
        # use default formats
        if fname.suffix in [".json", ".yaml", ".yml"]:
            format = "readable"
        elif fname.suffix in [".png", ".jpg", ".jpeg", ".webp"]:
            format = "image"
        elif fname.suffix in [".npy", ".npz"]:
            format = "numpy"
        elif fname.suffix == ".ptz":
            format = "ptz"
        elif fname.suffix == ".exr":
            format = "scalar"
        elif fname.suffix in [".ply", ".obj", ".glb"]:
            format = "mesh"
        else:
            raise ValueError(f"Cannot infer format for {fname}")
    methods = {
        "readable": (_load_readable, _store_readable),
        "scalar": (_read_exr, _write_exr),
        "image": (_load_image, _store_image),
        "binary": (_load_binary_mask, _store_binary_mask),
        "depth": (_load_depth, _store_depth),
        "normals": (_load_normals, _store_normals),
        "numpy": (_load_numpy, _store_numpy),
        "ptz": (_load_ptz, _store_ptz),
        "mmap": (_load_mmap, _store_mmap),
        "scene_meta": (_load_scene_meta, _store_scene_meta),
        "labeled_image": (_load_labeled_image, _store_labeled_image),
        "mesh": (_load_generic_mesh, _store_generic_mesh),
        "labeled_mesh": (_load_labeled_mesh, _store_labeled_mesh),
        "caption": (_load_caption, _store_caption),
    }
    try:
        return methods[format][0 if load else 1]
    except KeyError:
        raise NotImplementedError(f"Format not supported: {format}")
