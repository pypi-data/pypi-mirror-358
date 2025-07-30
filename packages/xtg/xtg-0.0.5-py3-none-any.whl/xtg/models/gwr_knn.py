import numpy as np
from scipy.spatial.distance import cdist
from xtg.core.kernels import gaussian_iso
from xtg.metrics import rmse, pseudo_r2

def fit_gwr_knn(X, y, coords_std, k=20):
    """KNN 自适应带宽的简单 GWR（各向同性、高斯核）"""
    n, p = X.shape
    Xc = np.hstack([np.ones((n, 1)), X])          # 加截距
    dist_mat = cdist(coords_std, coords_std)
    bw_vec = np.partition(dist_mat, k, axis=1)[:, k] + 1e-12  # 每点第 k 距离

    betas = np.empty((n, p + 1))
    for i in range(n):
        w = gaussian_iso(dist_mat[i], bw_vec[i])
        W = np.diag(np.maximum(w, 1e-12))
        betas[i], *_ = np.linalg.lstsq(Xc.T @ W @ Xc, Xc.T @ W @ y, rcond=1e-10)

    y_hat = (betas * Xc).sum(1)
    return {
        "beta": betas,
        "bw": bw_vec,
        "rmse": rmse(y, y_hat),
        "r2": pseudo_r2(y, y_hat),
    }
