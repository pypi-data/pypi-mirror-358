import numpy as np
import torch
import torch.nn.functional as F
from einops import rearrange, repeat


def dot(
    transform: np.ndarray | torch.Tensor,
    points: list | np.ndarray | torch.Tensor,
    coords: bool = False,
) -> np.ndarray | torch.Tensor:
    """Apply transformation matrix to points.
    Ignores any projective transformation.

    Args:
        transform: 3x3 or 4x4 transformation matrix
        points: Single point or array of points
        coords: If True, preserve coordinates beyond the first 3

    Returns:
        Transformed points
    """
    if isinstance(points, torch.Tensor):
        return dot_torch(transform, points, coords)

    # Convert everything to NumPy
    if isinstance(transform, torch.Tensor):
        transform = transform.detach().cpu().numpy()

    if isinstance(points, list):
        points = np.array(points)

    # A single point
    if len(points.shape) == 1:
        if transform.shape == (3, 3):
            return transform @ points[:3]
        else:
            return (transform @ np.array([*points[:3], 1]))[:3]

    if points.shape[1] == 3 or (coords and points.shape[1] > 3):
        # nx[xyz,...]
        if transform.shape == (4, 4):
            pts = (transform[:3, :3] @ points[:, :3].T).T + transform[:3, 3]
        elif transform.shape == (3, 3):
            pts = (transform[:3, :3] @ points[:, :3].T).T
        else:
            raise ValueError(f"Transform shape {transform.shape} not supported")

        return np.concatenate([pts, points[:, 3:]], 1)
    else:
        raise ValueError(f"Format of points {points.shape} is not supported")

def dot_torch(transform, points, coords=False):
    """Apply transformation matrix to points using PyTorch.
    Ignores any projective transformation.

    Args:
        transform: 3x3 or 4x4 transformation matrix
        points: Single point or array of points
        coords: If True, preserve coordinates beyond the first 3

    Returns:
        Transformed points
    """
    if not isinstance(transform, torch.Tensor):
        transform = torch.from_numpy(transform).float()

    transform = transform.to(points.device).float()
    if type(points) is list:
        points = torch.Tensor(points)
    if len(points.shape) == 1:
        # single point
        if transform.shape == (3, 3):
            return transform @ points[:3]
        else:
            return (transform @ torch.Tensor([*points[:3], 1]))[:3]
    if points.shape[1] == 3 or (coords and points.shape[1] > 3):
        # nx[xyz,...]
        if transform.shape == (4, 4):
            pts = (transform[:3, :3] @ points[:, :3].T).T + transform[:3, 3]
        elif transform.shape == (3, 3):
            pts = (transform[:3, :3] @ points[:, :3].T).T
        else:
            raise RuntimeError("Format of transform not understood")
        return torch.cat([pts, points[:, 3:]], 1)
    else:
        raise RuntimeError(f"Format of points {points.shape} not understood")


def m_dot(transform, points, maintain_shape=False):
    """
    Apply batch matrix multiplication between transform matrices and points.

    Args:
        transform: Batch of transformation matrices [..., 3/4, 3/4]
        points: Batch of points [..., N, 3] or a list of points
        maintain_shape: If True, preserves the original shape of points

    Returns:
        Transformed points with shape [..., N, 3] or a list of transformed points
    """
    if isinstance(points, list):
        return [m_dot(t, p, maintain_shape) for t, p in zip(transform, points)]

    # Store original shape and flatten batch dimensions
    orig_shape = points.shape
    batch_dims = points.shape[:-3]

    # Reshape to standard batch format
    transform_flat = transform.reshape(-1, transform.shape[-2], transform.shape[-1])
    points_flat = points.reshape(transform_flat.shape[0], -1, points.shape[-1])

    # Apply transformation
    pts = torch.bmm(
        transform_flat[:, :3, :3],
        points_flat[..., :3].permute(0, 2, 1).to(transform_flat.dtype),
    ).permute(0, 2, 1)

    if transform.shape[-1] == 4:
        pts = pts + transform_flat[:, :3, 3].unsqueeze(1)

    # Restore original shape
    if maintain_shape:
        return pts.reshape(orig_shape)
    else:
        return pts.reshape(*batch_dims, -1, 3)


def _create_image_grid(H: int, W: int, device: torch.device) -> torch.Tensor:
    """
    Create a coordinate grid for image pixels.

    Args:
        H: Image height
        W: Image width
        device: Computation device

    Returns:
        Image grid with shape HxWx3 (last dimension is homogeneous)
    """
    y_coords = torch.arange(H, device=device)
    x_coords = torch.arange(W, device=device)

    # Use meshgrid with indexing="ij" for correct orientation
    y_grid, x_grid = torch.meshgrid(y_coords, x_coords, indexing="ij")

    # Stack coordinates and add homogeneous coordinate
    img_grid = torch.stack([y_grid, x_grid, torch.ones_like(y_grid)], dim=-1)

    return img_grid

def m_inverse_intrinsics(intrinsics: Tensor) -> Tensor:
    """
    Compute the inverse of camera intrinsics matrices analytically.
    This is much faster than using torch.inverse() for intrinsics matrices.

    The intrinsics matrix has the form:
    K = [fx  s  cx]
        [0   fy cy]
        [0   0   1]

    And its inverse is:
    K^-1 = [1/fx  -s/(fx*fy)  (s*cy-cx*fy)/(fx*fy)]
           [0     1/fy        -cy/fy            ]
           [0     0           1                 ]

    Args:
        intrinsics: Camera intrinsics matrices of shape [..., 3, 3]

    Returns:
        Inverse intrinsics matrices of shape [..., 3, 3]
    """
    # Extract the components of the intrinsics matrix
    fx = intrinsics[..., 0, 0]
    s = intrinsics[..., 0, 1]  # skew, usually 0
    cx = intrinsics[..., 0, 2]
    fy = intrinsics[..., 1, 1]
    cy = intrinsics[..., 1, 2]

    # Create output tensor with same shape and device
    inv_intrinsics = torch.zeros_like(intrinsics)

    # Compute the inverse analytically
    inv_intrinsics[..., 0, 0] = 1.0 / fx
    inv_intrinsics[..., 0, 1] = -s / (fx * fy)
    inv_intrinsics[..., 0, 2] = (s * cy - cx * fy) / (fx * fy)
    inv_intrinsics[..., 1, 1] = 1.0 / fy
    inv_intrinsics[..., 1, 2] = -cy / fy
    inv_intrinsics[..., 2, 2] = 1.0

    return inv_intrinsics


def m_unproject(
    depth: torch.Tensor,
    intrinsic: torch.Tensor,
    cam2world: torch.Tensor = None,
    img_grid: torch.Tensor = None,
    valid: torch.Tensor = None,
    H: int = None,
    W: int = None,
    img_feats: torch.Tensor = None,
    maintain_shape: bool = False,
) -> torch.Tensor:
    """
    Unproject 2D image points with depth values to 3D points in camera or world space.

    Args:
        depth: Depth values, either a tensor of shape ...xHxW or a float value
        intrinsic: Camera intrinsic matrix of shape ...x3x3
        cam2world: Optional camera-to-world transformation matrix of shape ...x4x4
        img_grid: Optional pre-computed image grid. If None, will be created
        valid: Optional mask for valid depth values or minimum depth threshold
        H: Image height (required if depth is a scalar)
        W: Image width (required if depth is a scalar)
        img_feats: Optional image features to append to 3D points
        maintain_shape: If True, preserves the original shape of points

    Returns:
        3D points in camera or world space, with optional features appended
    """
    # Get device and shape information from intrinsic matrix
    device = intrinsic.device
    pre_shape = intrinsic.shape[:-2]  # Batch dimensions

    # Validate inputs
    assert not isinstance(depth, (int, float)) or H is not None, (
        "H must be provided if depth is a scalar"
    )

    # Determine image dimensions from depth if not provided
    if isinstance(depth, torch.Tensor) and H is None:
        H, W = depth.shape[-2:]

    # Create image grid if not provided
    if img_grid is None:
        # Create coordinate grid with shape HxWx3 (last dimension is homogeneous)
        img_grid = _create_image_grid(H, W, device)
        # Add homogeneous coordinate
        img_grid = torch.cat([img_grid, torch.ones_like(img_grid[..., :1])], -1)

    # Expand img_grid to match batch dimensions of intrinsic
    if img_grid.dim() <= intrinsic.dim():
        img_grid = img_grid.unsqueeze(0)
        img_grid = img_grid.expand(*pre_shape, *img_grid.shape[-3:])

    # Handle valid mask or minimum depth threshold
    depth_mask = None
    if valid is not None:
        if isinstance(valid, float):
            # Create mask for minimum depth value
            depth_mask = depth > valid
        elif isinstance(valid, torch.Tensor):
            depth_mask = valid

        # Apply mask to image grid and other inputs
        img_grid = masking(img_grid, depth_mask, dim=intrinsic.dim())
        if not isinstance(depth, (int, float)):
            depth = masking(depth, depth_mask, dim=intrinsic.dim() - 1)
        if img_feats is not None:
            img_feats = masking(img_feats, depth_mask, dim=intrinsic.dim() - 1)

    # Unproject 2D points to 3D camera space
    cam_pts = m_dot(
        m_inverse_intrinsics(intrinsic),
        img_grid[..., [1, 0, 2]],
        maintain_shape=True,
    )
    # Scale by depth values
    cam_pts = mult(cam_pts, depth.unsqueeze(-1))

    # Transform to world space if cam2world is provided
    if cam2world is not None:
        cam_pts = m_dot(cam2world, cam_pts, maintain_shape=True)

    # Append image features if provided
    if img_feats is not None:
        if isinstance(cam_pts, list):
            if isinstance(cam_pts[0], list):
                # Handle nested list case
                result = []
                for batch_idx, batch in enumerate(cam_pts):
                    batch_result = []
                    for view_idx, view in enumerate(batch):
                        batch_result.append(
                            torch.cat([view, img_feats[batch_idx][view_idx]], -1)
                        )
                    result.append(batch_result)
                cam_pts = result
            else:
                # Handle single list case
                cam_pts = [
                    torch.cat([pts, feats], -1)
                    for pts, feats in zip(cam_pts, img_feats)
                ]
        else:
            # Handle tensor case
            cam_pts = torch.cat([cam_pts, img_feats], -1)
    if maintain_shape:
        return cam_pts

    # Flatten last dimension
    return cam_pts.reshape(*pre_shape, -1, 3)


def m_project(world_pts, intrinsic, world2cam=None, maintain_shape=False):
    """
    Project 3D world points to 2D image coordinates.

    Args:
        world_pts: 3D points in world coordinates
        intrinsic: Camera intrinsic matrix
        world2cam: Optional transformation from world to camera coordinates
        maintain_shape: If True, preserves the original shape of points

    Returns:
        Image points with coordinates in img_y,img_x,z order
    """
    # Transform points from world to camera space if world2cam is provided
    if world2cam is not None:
        cam_pts = m_dot(world2cam, world_pts, maintain_shape=maintain_shape)
    else:
        cam_pts = world_pts
    # Get shapes to properly expand intrinsics
    shared_dims = intrinsic.shape[:-2]
    extra_dims = cam_pts.shape[len(shared_dims) : -1]

    # Expand intrinsics to match cam_pts shape
    expanded_intrinsic = intrinsic.view(*shared_dims, *([1] * len(extra_dims)), 3, 3)
    expanded_intrinsic = expanded_intrinsic.expand(*shared_dims, *extra_dims, 3, 3)

    # Project points from camera space to image space
    depth_abs = cam_pts[..., 2].abs().clamp(min=1e-5)
    return torch.stack(
        [
            expanded_intrinsic[..., 1, 1] * cam_pts[..., 1] / depth_abs
            + expanded_intrinsic[..., 1, 2],
            expanded_intrinsic[..., 0, 0] * cam_pts[..., 0] / depth_abs
            + expanded_intrinsic[..., 0, 2],
            cam_pts[..., 2],
        ],
        -1,
    )





def in_image(image_pts, H, W, min_depth=0.0):
    """
    Check if image points are within the image boundaries.

    Args:
        image_pts: Image points in pixel coordinates
        H: Image height
        W: Image width
        min_depth: Minimum valid depth

    Returns:
        Boolean mask indicating which points are within the image
    """
    is_list = isinstance(image_pts, list)
    if is_list:
        return [in_image(pts, H, W, min_depth=min_depth) for pts in image_pts]
    in_image_mask = (
        torch.all(image_pts >= 0, -1)
        & (image_pts[..., 0] < H)
        & (image_pts[..., 1] < W)
    )
    if (min_depth is not None) and image_pts.shape[-1] == 3:
        in_image_mask &= image_pts[..., 2] > min_depth
    return in_image_mask


def m_image_sampling(
    images,
    ij_coords,
    mode="bilinear",
    padding_mode="zeros",
    align_corners=True,
    min_depth=0.0,
):
    """
    Sample features from images at specified coordinates.

    Args:
        images: Tensor of images [..., C, H, W] or list of images
        ij_coords: Coordinates in pixel space [..., 2] (x, y) or [..., 3] (x,y,d)
        mode: Interpolation mode ('nearest', 'bilinear', 'bicubic')
        padding_mode: Padding mode ('zeros', 'border', 'reflection')
        align_corners: Whether to align corners in grid sampling
        min_depth: Minimum valid depth used for masking if depth is provided in coords

    Returns:
        Sampled features at the specified coordinates
    """
    if isinstance(images, list):
        return [
            m_image_sampling(img, c, mode, padding_mode, align_corners, min_depth)
            for img, c in zip(images, ij_coords)
        ]

    # Get shapes
    img_shape = images.shape
    coord_shape = ij_coords.shape

    # Extract image dimensions
    C, H, W = img_shape[-3:]

    # Reshape inputs for grid_sample
    # Flatten all batch dimensions for both images and coordinates
    batch_dims_img = img_shape[:-3]
    batch_dims_coords = coord_shape[:-1]

    # Ensure batch dimensions are compatible
    if len(batch_dims_img) > len(batch_dims_coords):
        # Expand coords if images have more batch dimensions
        for _ in range(len(batch_dims_img) - len(batch_dims_coords)):
            ij_coords = ij_coords.unsqueeze(0)
        batch_dims_coords = ij_coords.shape[:-1]
    elif len(batch_dims_coords) > len(batch_dims_img):
        # Expand images if coords have more batch dimensions
        for _ in range(len(batch_dims_coords) - len(batch_dims_img)):
            images = images.unsqueeze(0)
        batch_dims_img = images.shape[:-3]

    # Reshape to standard batch format
    flat_batch_size = np.prod(batch_dims_img)
    images = images.reshape(flat_batch_size, C, H, W)
    ij_coords = ij_coords.reshape(flat_batch_size, -1, ij_coords.shape[-1])

    # Convert pixel coordinates to normalized coordinates [-1, 1]
    norm_coords = torch.zeros_like(ij_coords[..., :2])
    norm_coords[..., 0] = 2.0 * ij_coords[..., 1] / (W - 1) - 1.0  # x -> normalized x
    norm_coords[..., 1] = 2.0 * ij_coords[..., 0] / (H - 1) - 1.0  # y -> normalized y

    # Reshape coordinates for grid_sample
    grid = norm_coords.reshape(flat_batch_size, -1, 1, 2)

    # Sample from images
    sampled = F.grid_sample(
        images, grid, mode=mode, padding_mode=padding_mode, align_corners=align_corners
    )

    # Reshape output to match input dimensions
    sampled = sampled.reshape(flat_batch_size, C, -1)
    sampled = sampled.permute(0, 2, 1)  # B N C

    # Calculate valid mask
    valid_mask = in_image(ij_coords, H, W, min_depth)

    # Reshape back to original batch dimensions
    if batch_dims_img == batch_dims_coords:
        sampled = sampled.reshape(*batch_dims_img, C)
        valid_mask = valid_mask.reshape(*batch_dims_img)
    else:
        # Handle broadcasting case
        sampled = sampled.reshape(*batch_dims_coords, C)
        valid_mask = valid_mask.reshape(*batch_dims_coords)

    return sampled, valid_mask


def get_shape(x):
    """
    Recursively determine the shape of nested lists, numpy arrays, or PyTorch tensors.

    Args:
        x: Input data structure (list, numpy array, or PyTorch tensor)

    Returns:
        List representing the shape of the input
    """
    if isinstance(x, list):
        if not x:  # Handle empty list case
            return [0]
        return [len(x)] + get_shape(x[0])
    elif isinstance(x, (np.ndarray, torch.Tensor)):
        return list(x.shape)
    return []



def mult(A, B):
    if isinstance(A, list) and isinstance(B, (int, float)):
        return [mult(a, B) for a in A]
    if isinstance(B, list) and isinstance(A, (int, float)):
        return [mult(A, b) for b in B]
    if isinstance(A, list) and isinstance(B, list):
        return [mult(a, b) for a, b in zip(A, B)]
    return A * B


def masking(X, mask, dim=3):
    if isinstance(X, list) or (isinstance(X, torch.Tensor) and X.dim() >= dim):
        return [masking(x, m, dim) for x, m in zip(X, mask)]
    return X[mask]

def hmg(X):
    last_row = torch.zeros(*X.shape[:-2], 1, 4, device=X.device)
    last_row[..., 0, -1] = 1
    return torch.cat(
        [torch.cat([X, torch.zeros(*X.shape[:-1], 1, device=X.device)], -1), last_row],
        -2,
    )

def depth2raydist(
    intrinsics,  # [B x V x 3 x 3]
    depth_samples,  # [B x V x H x W x S]
):
    device = depth_samples.device
    B, V, H, W, S = depth_samples.shape
    uv = torch.stack(
        torch.meshgrid(
            torch.arange(0, W).to(device), torch.arange(0, H).to(device), indexing="xy"
        ),
        -1,
    )  # use indexing="xy" because intrinsics are wh, then flip output
    uvh = torch.cat([uv, torch.ones_like(uv[..., :1])], -1)
    uvh = repeat(uvh, "W H C -> B V (W H) C", B=B, V=V)
    pts = m_dot(torch.inverse(intrinsics.float()), uvh)
    pts = rearrange(
        pts, "B V (W H) C -> B V H W C", W=W, H=H
    )  # note that we swap W H -> H W here

    ray_dist = depth_samples * pts.norm(dim=-1, keepdim=True)  # B x V x H x W x S
    return ray_dist


def raydist2depth(
    intrinsics,  # [B x V x 3 x 3]
    dist_samples,  # [B x V x H x W x S]
):
    device = dist_samples.device
    B, V, H, W, S = dist_samples.shape
    uv = torch.stack(
        torch.meshgrid(
            torch.arange(0, W).to(device), torch.arange(0, H).to(device), indexing="xy"
        ),
        -1,
    )  # use indexing="xy" because intrinsics are wh, then flip output
    uvh = torch.cat([uv, torch.ones_like(uv[..., :1])], -1)
    uvh = repeat(uvh, "W H C -> B V (W H) C", B=B, V=V)
    pts = m_dot(torch.inverse(intrinsics.float()), uvh)
    pts = rearrange(
        pts, "B V (W H) C -> B V H W C", W=W, H=H
    )  # note that we swap W H -> H W here

    depth_samples = dist_samples / pts.norm(dim=-1, keepdim=True)  # B x V x H x W x S
    return depth_samples
