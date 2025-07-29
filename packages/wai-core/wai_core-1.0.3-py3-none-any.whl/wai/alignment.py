import torch

from .camera import create_transformation_matrices
from .m_ops import m_dot


def umeyama_alignment(X, Y, with_scale=True):
    """
    Computes the least squares solution parameters of an Sim(m) transformation
    that minimizes the distance between a set of registered points.

    Parameters:
    X: torch.Tensor (B, N, D) - source points
    Y: torch.Tensor (B, N, D) - target points
    with_scale: bool - whether to calculate scaling factor

    Returns:
    R: torch.Tensor (B, D, D) - rotation matrices
    t: torch.Tensor (B, D) - translation vectors
    s: torch.Tensor (B,) - scaling factors (or None if with_scale=False)
    """
    batch_size, n, dim = X.shape

    # Center the data
    X_mean = X.mean(dim=1, keepdim=True)
    Y_mean = Y.mean(dim=1, keepdim=True)

    X_centered = X - X_mean
    Y_centered = Y - Y_mean

    # Compute covariance matrix
    cov = torch.bmm(X_centered.transpose(1, 2), Y_centered) / n

    # Compute SVD
    U, D, Vh = torch.linalg.svd(cov)

    # Ensure proper rotation (no reflection)
    det_UV = torch.linalg.det(torch.bmm(U, Vh))
    S = torch.eye(dim, device=X.device).unsqueeze(0).repeat(batch_size, 1, 1)
    S[:, -1, -1] = det_UV

    # Calculate rotation
    R = torch.bmm(torch.bmm(U, S), Vh)

    if with_scale:
        # Compute variance of X_centered
        var_X = (X_centered**2).sum(dim=(1, 2)) / n

        # Compute scaling factor
        scale = torch.sum(D * S.diagonal(dim1=1, dim2=2), dim=1) / var_X

        # Apply scaling to rotation
        t = Y_mean.squeeze(1) - scale.unsqueeze(1) * torch.bmm(
            X_mean, R.transpose(1, 2)
        ).squeeze(1)

        return R, t, scale
    else:
        # No scaling
        t = Y_mean.squeeze(1) - torch.bmm(X_mean, R.transpose(1, 2)).squeeze(1)
        return R, t, None


def absolute_trajectory_error(
    pred_trajectory, gt_trajectory, alignment=True, return_transform=True
):
    """
    Compute the Absolute Trajectory Error (ATE) between predicted and ground truth trajectories.

    Parameters:
    pred_trajectory: torch.Tensor (B, N, D) - predicted trajectory
    gt_trajectory: torch.Tensor (B, N, D) - ground truth trajectory
    alignment: bool - whether to align trajectories using Umeyama

    Returns:
    ate: torch.Tensor (B,) - mean ATE for each batch
    aligned_pred: torch.Tensor (B, N, D) - aligned predicted trajectory (if alignment=True)
    """
    if return_transform and not alignment:
        raise RuntimeError(
            "Transform can only be returned if alignment activated. Set alignment to True or "
            "return_transform to False to resolve."
        )
    batch_size, _, _ = pred_trajectory.shape

    if alignment:
        # Align predicted trajectory to ground truth using Umeyama
        R, t, s = umeyama_alignment(pred_trajectory, gt_trajectory)
        pred2gt_transform = create_transformation_matrices(R, t, s)
        aligned_pred = m_dot(pred2gt_transform, pred_trajectory)
        # Compute error
        error = torch.norm(aligned_pred - gt_trajectory, dim=2)
    else:
        # Compute error without alignment
        error = torch.norm(pred_trajectory - gt_trajectory, dim=2)
        aligned_pred = None

    # Mean error per batch
    ate = error.mean(dim=1)

    if return_transform:
        return (
            ate,
            aligned_pred,
            pred2gt_transform,
            {"R": R, "t": t, "s": s},
        )
    else:
        return ate, aligned_pred
