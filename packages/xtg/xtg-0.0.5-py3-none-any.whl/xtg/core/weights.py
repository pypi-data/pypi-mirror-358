"""
xtg.core.weights
================

· 空间权重矩阵生成器 ·
--------------------------------------------
compute_weights(coords, bw, ...)
    - 支持各向同性 / 各向异性带宽
    - 支持高斯核 / 双二次核
    - 返回 SciPy CSR 稀疏矩阵（默认零对角）
"""

from __future__ import annotations

from typing import Literal, Tuple

import numpy as np
import numpy.typing as npt
from scipy.sparse import csr_matrix

from .kernels import (
    gaussian_iso,
    gaussian_aniso,
    bisquare_iso,
    bisquare_aniso,
)

__all__ = [
    "compute_weights",
]


# --------------------------------------------------------------------------- #
# 1. 内部工具                                                                 #
# --------------------------------------------------------------------------- #

def _pairwise_deltas(coords: npt.ArrayLike) -> Tuple[np.ndarray, np.ndarray]:
    """
    计算 dx、dy 的差分矩阵。
    """
    coords = np.asarray(coords, dtype=float)
    x = coords[:, 0][:, None]  # (n, 1)
    y = coords[:, 1][:, None]
    dx = x - x.T  # Broadcasting → (n, n)
    dy = y - y.T
    return dx, dy


def _to_sparse_dense(mat: np.ndarray, sparse: bool) -> "csr_matrix | np.ndarray":
    """
    根据 `sparse` 标志把矩阵转成 CSR 或保持 dense。
    """
    if sparse:
        return csr_matrix(mat)
    return mat


# --------------------------------------------------------------------------- #
# 2. 公开接口                                                                 #
# --------------------------------------------------------------------------- #

def compute_weights(
    coords: npt.ArrayLike,
    bw: float | Tuple[float, float],
    *,
    kernel: Literal["gaussian", "bisquare"] = "gaussian",
    anisotropic: bool | None = None,
    zero_diagonal: bool = True,
    sparse: bool = True,
) -> "csr_matrix | np.ndarray":
    """
    生成 **n × n** 的空间权重矩阵。

    Parameters
    ----------
    coords : array-like, shape (n_samples, 2)
        二维平面坐标（经纬度也可，但需先做球面 → 平面近似投影）。
    bw : float 或 (bw_x, bw_y)
        - float           → 各向同性带宽
        - tuple (x, y)    → 各向异性带宽
    kernel : {"gaussian", "bisquare"}
        核函数类型。
    anisotropic : bool, optional
        - True            → 强制各向异性 (bw_x, bw_y)
        - False           → 强制各向同性 bw
        - None (默认)     → 自动根据 `bw` 的类型判断
    zero_diagonal : bool, default=True
        是否把对角权重设为 0（常用于回归、Moran's I）。
    sparse : bool, default=True
        True → 返回 `scipy.sparse.csr_matrix`；False → 返回 dense `ndarray`.

    Returns
    -------
    csr_matrix | ndarray, shape (n_samples, n_samples)
        权重矩阵 W。
    """
    coords = np.asarray(coords, dtype=float)
    n = coords.shape[0]
    if coords.ndim != 2 or coords.shape[1] != 2:  # pragma: no cover
        raise ValueError("coords 应为 (n_samples, 2) 的二维数组")

    # ---------------- 判断带宽类型 ----------------
    if anisotropic is None:
        anisotropic = isinstance(bw, (tuple, list, np.ndarray))
    if anisotropic:
        try:
            bw_x, bw_y = float(bw[0]), float(bw[1])
        except Exception as _:
            raise ValueError("anisotropic=True 时，bw 应为长度为 2 的序列") from _
    else:
        try:
            bw_iso = float(bw)
        except Exception as _:
            raise ValueError("anisotropic=False 时，bw 应为单一正标量") from _

    # ---------------- 计算权重 --------------------
    if anisotropic:
        dx, dy = _pairwise_deltas(coords)
        if kernel == "gaussian":
            W = gaussian_aniso(dx, dy, bw_x, bw_y)
        elif kernel == "bisquare":
            W = bisquare_aniso(dx, dy, bw_x, bw_y)
        else:  # pragma: no cover
            raise ValueError("kernel 仅支持 'gaussian' 或 'bisquare'")
    else:
        # pairwise Euclidean distance
        diff = coords[:, None, :] - coords[None, :, :]  # (n, n, 2)
        dist = np.hypot(diff[..., 0], diff[..., 1])     # √(dx² + dy²)
        if kernel == "gaussian":
            W = gaussian_iso(dist, bw_iso)
        elif kernel == "bisquare":
            W = bisquare_iso(dist, bw_iso)
        else:  # pragma: no cover
            raise ValueError("kernel 仅支持 'gaussian' 或 'bisquare'")

    # ---------------- 对角置零 --------------------
    if zero_diagonal:
        np.fill_diagonal(W, 0.0)

    return _to_sparse_dense(W, sparse)