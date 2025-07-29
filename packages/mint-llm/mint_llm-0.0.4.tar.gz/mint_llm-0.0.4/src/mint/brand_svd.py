from __future__ import annotations

import torch


def initialize_isvd(initial_vector, W, device=None):
    """
    Initializes the ISVD decomposition using the first column of data.

    Args:
        initial_vector (Tensor): First column of the data matrix (shape [m, 1]).
        W (Tensor): Weighting matrix for the generalized inner product (shape [m, m]).
        device (torch.device, optional): Target device (CPU or CUDA). Defaults to initial_vector.device.

    Returns:
        Q (Tensor): Initial orthonormal basis (shape [m, 1]).
        S (Tensor): Initial singular value (shape [1, 1]).
        R (Tensor): Initial right singular vector placeholder (1x1 identity matrix).
    """
    device = device if device is not None else initial_vector.device
    scale = torch.sqrt(initial_vector.T @ W @ initial_vector).to(device)
    Q = initial_vector.to(device) / scale
    R = torch.eye(1, device=device)
    return Q, scale, R


def update_isvd3(
    buffer_count, buffered_vectors, Q_0, Q, S, R, new_col, W, tol, device=None
):
    """
    Performs an incremental update step for ISVD with buffering of low-residual components.

    Args:
        buffer_count (int): Number of buffered updates currently stored.
        buffered_vectors (list[Tensor]): List of low-residual vectors to accumulate and flush later.
        Q_0 (Tensor): Augmented orthogonalization basis used to compact buffered projections.
        Q (Tensor): Current left singular vectors (shape [m, r]).
        S (Tensor): Current singular values (shape [r, r] or [r, r + b]).
        R (Tensor): Current right singular vectors (shape [r, n]).
        new_col (Tensor): New column vector (shape [m, 1]) to incorporate.
        W (Tensor): Weighting matrix (shape [m, m]).
        tol (float): Tolerance threshold for accepting new orthogonal directions.
        device (torch.device, optional): Target device for operations.

    Returns:
        buffer_count (int): Updated buffer count after potential flush.
        buffered_vectors (list[Tensor]): Updated buffer list.
        Q_0 (Tensor): Possibly expanded orthogonalization basis.
        Q (Tensor): Updated left singular vectors.
        S (Tensor): Updated singular values.
        R (Tensor): Updated right singular vectors.
    """
    device = device if device is not None else Q.device

    projection = Q.T @ (W @ new_col)
    residual = new_col - Q @ projection
    residual_norm = torch.sqrt(residual.T @ W @ residual)

    if residual_norm < tol:
        buffer_count += 1
        buffered_vectors.append(Q_0.T @ projection)
    else:
        if buffer_count > 0:
            # Flush buffered updates via compact SVD
            k = S.shape[0]
            stacked = torch.cat([S, torch.stack(buffered_vectors, dim=1)], dim=1)
            Qy, Sy, Ry = torch.linalg.svd(stacked, full_matrices=False)
            # Convert Sy to diag from vector to match matlab's return type and fix downstream errors.
            Sy = torch.diag(Sy)
            Q = Q @ (Q_0 @ Qy)
            S = Sy
            R1 = Ry[:k, :]
            R2 = Ry[k:, :]
            R = torch.cat([R @ R1, R2], dim=0)
            projection = Qy.T @ projection

        # Reset buffer
        buffered_vectors = []
        buffer_count = 0

        # Orthonormalize residual and optionally reproject
        residual = residual / residual_norm
        if torch.sqrt(residual.T @ W @ Q[:, 0]) > tol:
            residual = residual - Q @ (Q.T @ (W @ residual))
            residual = residual / torch.sqrt(residual.T @ W @ residual)

        # Augment compact SVD system
        k = S.shape[0]
        Y = torch.cat(
            [
                torch.cat([S, Q_0.T @ projection], dim=1),
                torch.cat(
                    [torch.zeros(1, k, device=device), residual_norm.view(1, 1)], dim=1
                ),
            ],
            dim=0,
        )

        Qy, Sy, Ry = torch.linalg.svd(Y, full_matrices=False)
        Sy = torch.diag(Sy)

        # Expand Q_0 and reproject
        Q_0 = torch.cat(
            [
                torch.cat([Q_0, torch.zeros(Q_0.shape[0], 1, device=device)], dim=1),
                torch.zeros(1, Q_0.shape[1] + 1, device=device),
            ],
            dim=0,
        )
        Q_0[-1, -1] = 1
        Q_0 = Q_0 @ Qy

        Q = torch.cat([Q, residual], dim=1)
        S = Sy
        R = (
            torch.cat(
                [
                    torch.cat([R, torch.zeros(R.shape[0], 1, device=device)], dim=1),
                    torch.zeros(1, R.shape[1] + 1, device=device),
                ],
                dim=0,
            )
            @ Ry
        )

    return buffer_count, buffered_vectors, Q_0, Q, S, R


def update_isvd3_check(buffer_count, buffered_vectors, Q_0, Q, S, R):
    """
    Final cleanup step to flush any remaining buffered projections after streaming.

    Args:
        buffer_count (int): Number of vectors still buffered.
        buffered_vectors (list[Tensor]): List of accumulated buffered vectors.
        Q_0 (Tensor): Orthogonal basis for buffered projections.
        Q (Tensor): Current left singular vectors.
        S (Tensor): Current singular values.
        R (Tensor): Current right singular vectors.

    Returns:
        Q (Tensor): Finalized left singular vectors after flushing.
        S (Tensor): Finalized singular values.
        R (Tensor): Finalized right singular vectors.
    """
    k = S.shape[0]
    if buffer_count > 0:
        stacked = torch.cat([S, torch.stack(buffered_vectors, dim=1)], dim=1)
        Qy, Sy, Ry = torch.linalg.svd(stacked, full_matrices=False)
        Sy = torch.diag(Sy)
        Q = Q @ (Q_0 @ Qy)
        S = Sy
        R1 = Ry[:k, :]
        R2 = Ry[k:, :]
        R = torch.cat([R @ R1, R2], dim=0)
    else:
        Q = Q @ Q_0
    return Q, S, R
