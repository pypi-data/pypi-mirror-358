
import numpy as np
import torch

# constants regarding camera models
PINHOLE_CAM_KEYS = ["fl_x", "fl_y", "cx", "cy", "h", "w"]
DISTORTION_PARAM_KEYS = [
    "k1",
    "k2",
    "k3",
    "k4",
    "p1",
    "p2",
]  # order corresponds to the OpenCV convention
CAMERA_KEYS = PINHOLE_CAM_KEYS + DISTORTION_PARAM_KEYS

def convert_camera_coeffs_to_pinhole_matrix(scene_meta, frame):
    """
    Convert camera intrinsics from NeRFStudio format to a 3x3 intrinsics matrix.

    Args:
        scene_meta (dict): Scene metadata containing camera parameters
        frame (dict): Frame-specific camera parameters that override scene_meta

    Returns:
        torch.Tensor: 3x3 camera intrinsics matrix

    Raises:
        ValueError: If camera model is not PINHOLE or if distortion coefficients are present
    """
    # Check if camera model is supported
    camera_model = frame.get("camera_model", scene_meta.get("camera_model"))
    if camera_model != "PINHOLE":
        raise ValueError("Only PINHOLE camera model supported")

    # Check for unsupported distortion coefficients
    distortion_coeffs = ["k1", "k2", "k3", "k4", "p1", "p2"]
    if any(
        (frame.get(coeff, 0) != 0) or (scene_meta.get(coeff, 0) != 0)
        for coeff in distortion_coeffs
    ):
        raise ValueError(
            "Pinhole camera does not support radial/tangential distortion -> Undistort first"
        )

    # Extract camera intrinsic parameters
    camera_coeffs = {}
    for coeff in ["fl_x", "fl_y", "cx", "cy"]:
        camera_coeffs[coeff] = frame.get(coeff, scene_meta.get(coeff))
        if camera_coeffs[coeff] is None:
            raise ValueError(f"Missing required camera parameter: {coeff}")

    # Create intrinsics matrix
    intrinsics = torch.tensor(
        [
            [camera_coeffs["fl_x"], 0.0, camera_coeffs["cx"]],
            [0.0, camera_coeffs["fl_y"], camera_coeffs["cy"]],
            [0.0, 0.0, 1.0],
        ],
    )
    return intrinsics


def convert_pinhole_matrix_to_camera_coeffs(intrinsics):
    """
    Convert a 3x3 intrinsics matrix to camera coefficients.

    Args:
        intrinsics (torch.Tensor or np.ndarray): 3x3 camera intrinsics matrix

    Returns:
        dict: Camera coefficients with keys 'fl_x', 'fl_y', 'cx', 'cy'
    """
    if isinstance(intrinsics, torch.Tensor):
        intrinsics = intrinsics.detach().cpu().numpy()

    camera_coeffs = {
        "fl_x": float(intrinsics[0, 0]),
        "fl_y": float(intrinsics[1, 1]),
        "cx": float(intrinsics[0, 2]),
        "cy": float(intrinsics[1, 2]),
        "camera_model": "PINHOLE",
    }

    return camera_coeffs


def _apply_transformation(c2ws, cmat):
    """
    Convert camera poses using a provided conversion matrix.
    Args:
        c2ws (torch.Tensor or np.ndarray): Camera poses (batch_size, 4, 4) or (4, 4)
        cmat (torch.Tensor or np.ndarray): Conversion matrix (4, 4)
    Returns:
        torch.Tensor or np.ndarray: Transformed camera poses (batch_size, 4, 4) or (4, 4)
    """
    if isinstance(c2ws, torch.Tensor):
        # Clone the input tensor to avoid modifying it in-place
        c2ws_transformed = c2ws.clone()
        # Apply the conversion matrix to the rotation part of the camera poses
        if len(c2ws.shape) == 3:
            c2ws_transformed[:, :3, :3] = c2ws_transformed[
                :, :3, :3
            ] @ torch.from_numpy(cmat[:3, :3]).to(c2ws).unsqueeze(0)
        else:
            c2ws_transformed[:3, :3] = c2ws_transformed[:3, :3] @ torch.from_numpy(
                cmat[:3, :3]
            ).to(c2ws)
    elif isinstance(c2ws, np.ndarray):
        # Clone the input array to avoid modifying it in-place
        c2ws_transformed = c2ws.copy()
        if len(c2ws.shape) == 3:  # batched
            # Apply the conversion matrix to the rotation part of the camera poses
            c2ws_transformed[:, :3, :3] = np.einsum(
                "ijk,lk->ijl", c2ws_transformed[:, :3, :3], cmat[:3, :3]
            )
        else:  # single 4x4 matrix
            # Apply the conversion matrix to the rotation part of the camera pose
            c2ws_transformed[:3, :3] = np.dot(c2ws_transformed[:3, :3], cmat[:3, :3])
    else:
        raise ValueError("Input data type not supported.")
    return c2ws_transformed


def _gl_cv_cmat():
    cmat = np.array([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
    return cmat

def gl2cv(c2ws, return_cmat=False):
    """
    Convert camera poses from OpenGL to OpenCV coordinate system.

    Args:
        c2ws (torch.Tensor or np.ndarray): Camera poses (batch_size, 4, 4) or (4, 4)
        return_cmat (bool): If True, return the conversion matrix along with the transformed poses

    Returns:
        torch.Tensor or np.ndarray: Transformed camera poses (batch_size, 4, 4) or (4, 4)
        np.ndarray (optional): Conversion matrix if return_cmat is True
    """
    cmat = _gl_cv_cmat()
    if return_cmat:
        return _apply_transformation(c2ws, cmat), cmat
    return _apply_transformation(c2ws, cmat)


def cv2gl(c2ws, return_cmat=False):
    """
    Convert camera poses from OpenCV to OpenGL coordinate system.

    Args:
        c2ws (torch.Tensor or np.ndarray): Camera poses (batch_size, 4, 4) or (4, 4)
        return_cmat (bool): If True, return the conversion matrix along with the transformed poses

    Returns:
        torch.Tensor or np.ndarray: Transformed camera poses (batch_size, 4, 4) or (4, 4)
        np.ndarray (optional): Conversion matrix if return_cmat is True
    """
    cmat = _gl_cv_cmat()
    if return_cmat:
        return _apply_transformation(c2ws, cmat), cmat
    return _apply_transformation(c2ws, cmat)


def rotate_pinhole_90degcw(W, H, fx, fy, cx, cy):
    """Rotates the intrinsics of a pinhole camera model by 90 degrees clockwise."""
    W_new = H
    H_new = W
    fx_new = fy
    fy_new = fx
    cy_new = cx
    cx_new = H - 1 - cy
    return W_new, H_new, fx_new, fy_new, cx_new, cy_new


def create_transformation_matrices(R=None, t=None, s=None):
    """
    Convert rotation, translation, and scale to 4x4 transformation matrices.
    Supports arbitrary batch dimensions.

    Args:
        R: torch.Tensor (..., 3, 3) or None - Rotation matrices
        t: torch.Tensor (..., 3) or None - Translation vectors
        s: torch.Tensor (...) or scalar or None - Scale factors

    Returns:
        torch.Tensor (..., 4, 4) - Transformation matrices
    """
    # Determine batch dimensions and device
    if R is not None:
        batch_dims = R.shape[:-2]
        device = R.device
    elif t is not None:
        batch_dims = t.shape[:-1]
        device = t.device
    elif s is not None:
        batch_dims = s.shape
        device = s.device
    else:
        raise ValueError("At least one of R, t, or s must be provided")

    # Initialize transformation matrices as identity
    T = torch.eye(4, device=device).expand(*batch_dims, 4, 4).clone()

    # Set rotation part if provided
    if R is not None:
        if s is not None:
            # Broadcast s to match batch dimensions
            s_expanded = s.view(*s.shape, 1, 1)
            T[..., :3, :3] = s_expanded * R
        else:
            T[..., :3, :3] = R
    elif s is not None:
        # Apply scaling to identity rotation
        s_expanded = s.view(*s.shape, 1, 1)
        T[..., :3, :3] = s_expanded * T[..., :3, :3]

    # Set translation part if provided
    if t is not None:
        T[..., :3, 3] = t

    return T


def to_Rt(transformation):
    """
    Extract rotation and translation from transformation matrix by removing scale.

    Args:
        transformation: [..., 4, 4] transformation matrix

    Returns:
        unscaled_transformation: [..., 4, 4] transformation with normalized rotation
    """
    # Calculate scale from rotation matrix column
    scale = torch.sqrt((transformation[..., :3, :3] ** 2).sum(dim=-2)).unsqueeze(-1)

    unscaled_transformation = transformation.clone()

    # Normalize rotation part by dividing by scale (broadcasting handles dimensions)
    unscaled_transformation[..., :3, :3] = transformation[..., :3, :3] / scale

    return unscaled_transformation
