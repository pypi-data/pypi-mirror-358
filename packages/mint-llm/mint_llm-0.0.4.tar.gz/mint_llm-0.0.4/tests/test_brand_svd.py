import torch
import time

from mint.brand_svd import initialize_isvd, update_isvd3, update_isvd3_check


def test_brand_incremental_svd():
    # === SETTINGS ===
    # m: number of samples, n: dimension of each sample, r: rank of underlying matrix
    num_rows, num_cols, true_rank = 100, 80, 30

    # Create a synthetic low-rank matrix: U = A @ B
    true_matrix = torch.rand(num_rows, true_rank) @ torch.rand(true_rank, num_cols)
    weight_matrix = torch.eye(num_rows)
    first_column = true_matrix[:, 0:1]
    tolerance = 1e-15

    # === INITIALIZATION ===
    # Start timing
    start_time = time.time()

    # Initialize ISVD decomposition with the first column
    Q, S, R = initialize_isvd(first_column, weight_matrix)
    buffered_updates: list[torch.Tensor] = []
    Q_0 = torch.eye(1)
    buffer_count = 0

    # === STREAMING UPDATE ===
    # Incrementally update the ISVD with each additional column
    for col_index in range(1, num_cols):
        next_col = true_matrix[:, col_index : col_index + 1]
        buffer_count, buffered_updates, Q_0, Q, S, R = update_isvd3(
            buffer_count,
            buffered_updates,
            Q_0,
            Q,
            S,
            R,
            next_col,
            weight_matrix,
            tolerance,
        )

    # Final check to apply any buffered updates
    Q, S, R = update_isvd3_check(buffer_count, buffered_updates, Q_0, Q, S, R)
    end_time = time.time()
    print("Streaming ISVD time:", end_time - start_time)

    # === BASELINE SVD FOR COMPARISON ===
    torch.cuda.empty_cache()
    baseline_start = time.time()
    Q_baseline, S_baseline, R_baseline = torch.linalg.svd(
        true_matrix, full_matrices=False
    )
    baseline_end = time.time()
    print("Torch SVD time:", baseline_end - baseline_start)

    # === RECONSTRUCTION ERROR ANALYSIS ===
    # Compare streaming SVD reconstruction vs built-in SVD
    streaming_recon_error = torch.norm(Q @ S @ R.T - true_matrix)
    baseline_recon_error = torch.norm(
        Q_baseline @ torch.diag(S_baseline) @ R_baseline - true_matrix
    )
    # Super verbose line forced by deprecation of x.T ... why??!
    Q_T = Q[:, -1].permute(*torch.arange(Q[:, -1].ndim - 1, -1, -1))
    column_orthogonality = torch.norm((Q_T @ weight_matrix @ Q[:, 0]).abs())

    print("Streaming SVD error:", streaming_recon_error.item())
    print("Torch SVD error:", baseline_recon_error.item())
    print("Q column orthogonality check:", column_orthogonality.item())
