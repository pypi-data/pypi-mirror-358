"""
xtg.models.agwr_pc
==================

Per-Coefficient Anisotropic GWR  (每列独立双带宽)
-------------------------------------------------
• 每个系数 k (含截距) 使用一对带宽 (bw_xk, bw_yk)
• 支持 Gaussian / Bi-square 核
• 计算帽子矩阵对角 trace(S) → 精确 AICc
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Tuple

import numpy as np
from numpy.linalg import inv, lstsq

from xtg.core.kernels import (
    gaussian_aniso,
    bisquare_aniso,
)
from xtg.metrics import rmse, aicc, pseudo_r2


__all__ = ["fit_agwr_pc", "AGWRPCResult"]


# --------------------------------------------------------------------------- #
# 工具函数（与 agwr.py 共用实现，复制过来以避免循环依赖）                    #
# --------------------------------------------------------------------------- #

def _pairwise_deltas(coords: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """返回 dx, dy 差分矩阵 (n, n)。"""
    x = coords[:, 0][:, None]
    y = coords[:, 1][:, None]
    return x - x.T, y - y.T


def _kernel_fn(name: str):
    name = name.lower()
    if name == "gaussian":
        return gaussian_aniso
    elif name == "bisquare":
        return bisquare_aniso
    raise ValueError("kernel 仅支持 'gaussian' 和 'bisquare'")


# --------------------------------------------------------------------------- #
# 结果数据类                                                                  #
# --------------------------------------------------------------------------- #

@dataclass
class AGWRPCResult:
    coef_: np.ndarray                # (n, p+1)
    bw_: np.ndarray                  # (p+1, 2)
    kernel_: str
    coords_: np.ndarray
    X_: np.ndarray                   # 含截距
    y_: np.ndarray
    y_pred_: np.ndarray
    rmse_: float
    aicc_: float
    pseudo_r2_: float
    trace_s_: float                  # 精确 trace(S)

    # ---- 外推预测（最近邻系数） ----
    def predict(
        self,
        X_new: np.ndarray,
        coords_new: np.ndarray | None = None,
    ) -> np.ndarray:
        if coords_new is None:
            X_with_1 = np.hstack([np.ones((self.X_.shape[0], 1)), X_new])
            return np.sum(self.coef_ * X_with_1, axis=1)

        coords_new = np.asarray(coords_new, float)
        dists = np.hypot(
            coords_new[:, None, 0] - self.coords_[None, :, 0],
            coords_new[:, None, 1] - self.coords_[None, :, 1],
        )
        idx = np.argmin(dists, axis=1)
        betas = self.coef_[idx]
        X_with_1 = np.hstack([np.ones((coords_new.shape[0], 1)), X_new])
        return np.sum(betas * X_with_1, axis=1)


# --------------------------------------------------------------------------- #
# 主拟合函数                                                                  #
# --------------------------------------------------------------------------- #

def fit_agwr_pc(
    X: np.ndarray,
    y: np.ndarray,
    coords: np.ndarray,
    bw_mat: np.ndarray,
    *,
    kernel: Literal["gaussian", "bisquare"] = "gaussian",
    compute_metrics: bool = True,
) -> AGWRPCResult:
    """
    Per-Coefficient Anisotropic GWR.

    Parameters
    ----------
    X : (n, p) ndarray
        解释变量（不含截距）。
    y : (n,) ndarray
        响应变量。
    coords : (n, 2) ndarray
        平面坐标（已标准化或投影）。
    bw_mat : (p+1, 2) ndarray
        每个系数的 (bw_x, bw_y)，第 0 行对应截距。
    kernel : {"gaussian", "bisquare"}
    """
    # ---- 输入检查 ----
    X = np.asarray(X, float)
    y = np.asarray(y, float).ravel()
    coords = np.asarray(coords, float)
    n, p = X.shape
    bw_mat = np.asarray(bw_mat, float)
    if bw_mat.shape != (p + 1, 2):
        raise ValueError("bw_mat 形状应为 (p+1, 2)")
    if np.any(bw_mat <= 0):
        raise ValueError("所有带宽必须 > 0")

    # ---- 预计算 ----
    dx_mat, dy_mat = _pairwise_deltas(coords)
    kern = _kernel_fn(kernel)
    Xc = np.hstack([np.ones((n, 1)), X])
    coef_loc = np.empty((n, p + 1))
    trace_s = 0.0

    # ---- 主循环：逐点局部回归 ----
    for i in range(n):
        # 列权重 √w_ik
        scale_cols = []
        for k in range(p + 1):
            bwx, bwy = bw_mat[k]
            w_k = kern(dx_mat[i], dy_mat[i], bwx, bwy)
            w_k[i] = 0.0
            scale_cols.append(np.sqrt(np.maximum(w_k, 1e-12)))

        Xw = Xc * np.column_stack(scale_cols)   # (n, p+1)
        yw = y * scale_cols[0]

        beta_i, *_ = lstsq(Xw, yw, rcond=1e-10)
        coef_loc[i] = beta_i

        # trace(S) 对角元素
        XtX_inv = inv(Xw.T @ Xw + 1e-8 * np.eye(p + 1))
        x_i = Xc[i]
        trace_s += x_i @ XtX_inv @ x_i

    # ---- 预测 & 评估 ----
    y_hat = np.sum(coef_loc * Xc, axis=1)
    rmse_val = rmse(y, y_hat) if compute_metrics else np.nan
    aicc_val = aicc(y, y_hat, k=p + 1, trace_s=trace_s) if compute_metrics else np.nan
    r2_val = pseudo_r2(y, y_hat) if compute_metrics else np.nan

    return AGWRPCResult(
        coef_=coef_loc,
        bw_=bw_mat,
        kernel_=kernel,
        coords_=coords,
        X_=Xc,
        y_=y,
        y_pred_=y_hat,
        rmse_=rmse_val,
        aicc_=aicc_val,
        pseudo_r2_=r2_val,
        trace_s_=trace_s,
    )
