"""
xtg.models.mgwr
===============

多带宽地理加权回归 (MGWR)
----------------------------------------------
• 每个系数 (含截距) 有独立的各向同性带宽
• 列权重实现见文档字符串说明
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.linalg import lstsq
from typing import Literal, Sequence

from ..core.kernels import gaussian_iso, bisquare_iso
from ..metrics import rmse, aicc, pseudo_r2

__all__ = ["fit_mgwr", "MGWRResult"]


# --------------------------------------------------------------------------- #
# 1. 结果数据类                                                               #
# --------------------------------------------------------------------------- #

@dataclass
class MGWRResult:
    coef_: np.ndarray          # (n, p+1)
    bw_vec_: np.ndarray        # (p+1,)
    kernel_: str
    coords_: np.ndarray
    X_: np.ndarray             # 含截距
    y_: np.ndarray
    y_pred_: np.ndarray
    rmse_: float
    aicc_: float
    pseudo_r2_: float

    # ---------------- 预测 (最近邻外推) ---------------- #
    def predict(
        self,
        X_new: np.ndarray,
        coords_new: np.ndarray | None = None,
    ) -> np.ndarray:
        if coords_new is None:
            Xt = np.hstack([np.ones((self.X_.shape[0], 1)), X_new])
            return np.sum(self.coef_ * Xt, axis=1)

        coords_new = np.asarray(coords_new, float)
        dists = np.hypot(
            coords_new[:, None, 0] - self.coords_[:, 0][None, :],
            coords_new[:, None, 1] - self.coords_[:, 1][None, :],
        )                             # (m, n)
        idx = np.argmin(dists, axis=1)
        betas = self.coef_[idx]       # (m, p+1)
        Xt = np.hstack([np.ones((coords_new.shape[0], 1)), X_new])
        return np.sum(betas * Xt, axis=1)


# --------------------------------------------------------------------------- #
# 2. 内部工具                                                                 #
# --------------------------------------------------------------------------- #

def _kernel(name: str):
    if name.lower() == "gaussian":
        return gaussian_iso
    elif name.lower() == "bisquare":
        return bisquare_iso
    raise ValueError("kernel 仅支持 'gaussian' 与 'bisquare'")


def _validate_bw(bw: Sequence[float], p_plus1: int) -> np.ndarray:
    bw_arr = np.asarray(bw, float)
    if bw_arr.size != p_plus1:
        raise ValueError("bw_vec 长度必须等于 p + 1 (截距 + 自变量)")
    if np.any(bw_arr <= 0):
        raise ValueError("所有带宽必须为正数")
    return bw_arr


# --------------------------------------------------------------------------- #
# 3. 主函数                                                                   #
# --------------------------------------------------------------------------- #

def fit_mgwr(
    X: np.ndarray,
    y: np.ndarray,
    coords: np.ndarray,
    bw_vec: Sequence[float],
    *,
    kernel: Literal["gaussian", "bisquare"] = "gaussian",
    compute_metrics: bool = True,
) -> MGWRResult:
    """
    MGWR 拟合函数（单次回归，带宽已给定）

    Parameters
    ----------
    X : (n, p) ndarray
        自变量，不含截距列。
    y : (n,) ndarray
        因变量。
    coords : (n, 2) ndarray
        点坐标（平面）。
    bw_vec : sequence of length p+1
        截距 + 每列自变量的带宽。
    kernel : {"gaussian", "bisquare"}
    """
    # ---------------- 输入校验 ----------------
    X = np.asarray(X, float)
    y = np.asarray(y, float).flatten()
    coords = np.asarray(coords, float)
    n, p = X.shape
    if coords.shape != (n, 2):
        raise ValueError("coords 形状应为 (n, 2)")
    bw_vec = _validate_bw(bw_vec, p + 1)
    kern = _kernel(kernel)

    # ---------------- 距离矩阵 ----------------
    diff = coords[:, None, :] - coords[None, :, :]   # (n, n, 2)
    dist_mat = np.hypot(diff[..., 0], diff[..., 1])  # (n, n)

    # ---------------- 设计矩阵 ----------------
    Xc = np.hstack([np.ones((n, 1)), X])             # (n, p+1)
    coef_loc = np.empty((n, p + 1))

    # ---------------- 主循环 -----------------
    # 对每个观测点 i，构建“列权重”矩阵并做加权回归
    for i in range(n):
        # list 存每个列的 √w_ik
        scale_cols = []
        for k in range(p + 1):
            w_k = kern(dist_mat[i], bw_vec[k])        # (n,)
            w_k[i] = 0.0                              # 自身权重 0
            scale_cols.append(np.sqrt(w_k))

        # 构建加权 X、y
        Xw = Xc * np.column_stack(scale_cols)         # 广播得到 (n, p+1)
        yw = y * scale_cols[0]                        # 截距权重 w_0

        # WLS via OLS on加权数据
        beta, *_ = lstsq(Xw, yw, rcond=None)
        coef_loc[i] = beta

    # ---------------- 预测与指标 --------------
    y_hat = np.sum(coef_loc * Xc, axis=1)
    if compute_metrics:
        rmse_val = rmse(y, y_hat)
        aicc_val = aicc(y, y_hat, k=p + 1)
        pr2_val = pseudo_r2(y, y_hat)
    else:
        rmse_val = aicc_val = pr2_val = np.nan

    return MGWRResult(
        coef_=coef_loc,
        bw_vec_=bw_vec,
        kernel_=kernel,
        coords_=coords,
        X_=Xc,
        y_=y,
        y_pred_=y_hat,
        rmse_=rmse_val,
        aicc_=aicc_val,
        pseudo_r2_=pr2_val,
    )
