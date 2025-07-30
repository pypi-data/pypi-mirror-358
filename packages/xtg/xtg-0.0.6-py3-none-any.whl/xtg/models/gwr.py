"""
xtg.models.gwr
==============

各向同性地理加权回归 (GWR)
---------------------------------------------
• fit_gwr(X, y, coords, bw, ...)
      → 返回 GWRResult，属性和方法与 AGWRResult 对齐
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.linalg import lstsq,inv

from ..core.kernels import gaussian_iso, bisquare_iso
from ..metrics import rmse, aicc, pseudo_r2

__all__ = ["fit_gwr", "GWRResult"]


# --------------------------------------------------------------------------- #
# 1. 结果数据类                                                               #
# --------------------------------------------------------------------------- #

@dataclass
class GWRResult:
    coef_: np.ndarray           # (n, p + 1)
    bw_: float
    kernel_: str
    coords_: np.ndarray
    X_: np.ndarray              # 含截距
    y_: np.ndarray
    y_pred_: np.ndarray
    rmse_: float
    aicc_: float
    pseudo_r2_: float

    # ----------- 预测：最近邻系数外推 ----------- #
    def predict(
        self,
        X_new: np.ndarray,
        coords_new: np.ndarray | None = None,
    ) -> np.ndarray:
        if coords_new is None:
            Xt = np.hstack([np.ones((self.X_.shape[0], 1)), X_new])
            return np.sum(self.coef_ * Xt, axis=1)

        coords_new = np.asarray(coords_new, dtype=float)
        dists = np.hypot(
            coords_new[:, None, 0] - self.coords_[None, :, 0],
            coords_new[:, None, 1] - self.coords_[None, :, 1],
        )                               # (m, n)
        nearest = np.argmin(dists, axis=1)
        beta = self.coef_[nearest]
        Xt = np.hstack([np.ones((coords_new.shape[0], 1)), X_new])
        return np.sum(beta * Xt, axis=1)


# --------------------------------------------------------------------------- #
# 2. 核函数分发                                                               #
# --------------------------------------------------------------------------- #

def _kern(name: str):
    n = name.lower()
    if n == "gaussian":
        return gaussian_iso
    elif n == "bisquare":
        return bisquare_iso
    raise ValueError("kernel 仅支持 'gaussian' 或 'bisquare'")


# --------------------------------------------------------------------------- #
# 3. 主拟合函数                                                               #
# --------------------------------------------------------------------------- #

def fit_gwr(
    X: np.ndarray,
    y: np.ndarray,
    coords: np.ndarray,
    bw: float,
    *,
    kernel: Literal["gaussian", "bisquare"] = "gaussian",
    compute_metrics: bool = True,
) -> GWRResult:
    """
    Parameters
    ----------
    X : (n, p)
        自变量（不含截距）。
    y : (n,)
        因变量。
    coords : (n, 2)
        平面坐标。
    bw : float
        单一各向同性带宽 > 0。
    kernel : {"gaussian", "bisquare"}
    """
    # ---------- 输入处理 ----------
    X = np.asarray(X, float)
    y = np.asarray(y, float).flatten()
    coords = np.asarray(coords, float)
    n, p = X.shape
    if coords.shape != (n, 2):
        raise ValueError("coords 形状应为 (n, 2)")
    if bw <= 0:
        raise ValueError("带宽必须为正数")

    # ---------- 距离矩阵 ----------
    diff = coords[:, None, :] - coords[None, :, :]   # (n, n, 2)
    dist_mat = np.hypot(diff[..., 0], diff[..., 1])  # (n, n)

    kernel_fn = _kern(kernel)

    Xc = np.hstack([np.ones((n, 1)), X])             # (n, p+1)
    coef_loc = np.empty((n, p + 1))

    # ---------- 逐点加权回归 ----------
    for i in range(n):
        w_vec = kernel_fn(dist_mat[i], bw)           # (n,)
        w_vec[i] = 0.0
        W = np.diag(w_vec)
        XtW = Xc.T @ W
        beta, *_ = lstsq(XtW @ Xc, XtW @ y, rcond=None)
        coef_loc[i] = beta

    # ---------- 预测 & 评估 ----------
    y_pred = np.sum(coef_loc * Xc, axis=1)
    if compute_metrics:
        rmse_val = rmse(y, y_pred)
        aicc_val = aicc(y, y_pred, k=p + 1)
        pr2_val = pseudo_r2(y, y_pred)
    else:
        rmse_val = aicc_val = pr2_val = np.nan

    return GWRResult(
        coef_=coef_loc,
        bw_=float(bw),
        kernel_=kernel,
        coords_=coords,
        X_=Xc,
        y_=y,
        y_pred_=y_pred,
        rmse_=rmse_val,
        aicc_=aicc_val,
        pseudo_r2_=pr2_val,
    )

def fit_gwr_hat(
    X, y, coords, bw,
    *, kernel="gaussian", return_hat=True
):
    """
    spgwr 等价版：保留自身权重，构造帽子矩阵 S 的对角元素。
    """
    X = np.asarray(X, float)
    y = np.asarray(y, float).ravel()
    n, p = X.shape
    Xc = np.hstack([np.ones((n, 1)), X])         # (n, p+1)

    diff = coords[:, None, :] - coords[None, :, :]
    dist = np.hypot(diff[..., 0], diff[..., 1])

    kern = gaussian_iso if kernel == "gaussian" else bisquare_iso
    betas = np.empty((n, p + 1))
    S_diag = np.empty(n)

    for i in range(n):
        w = kern(dist[i], bw)                    # 自权重保留
        W = np.diag(np.maximum(w, 1e-8))
        XtWX = Xc.T @ W @ Xc
        XtWy = Xc.T @ W @ y
        beta = lstsq(XtWX, XtWy, rcond=1e-10)[0]
        betas[i] = beta

        if return_hat:
            XtWX_inv = inv(XtWX)
            S_diag[i] = Xc[i] @ XtWX_inv @ Xc[i]

    y_hat = (betas * Xc).sum(1)
    s_trace = S_diag.sum() if return_hat else p + 1

    return {
        "beta": betas,
        "y_hat": y_hat,
        "rmse": rmse(y, y_hat),
        "S_diag": S_diag if return_hat else None,
        "trace_s": s_trace,
    }

def spgwr_cv_rmse(X, y, coords, bw, kernel="gaussian"):
    res = fit_gwr_hat(X, y, coords, bw, kernel=kernel, return_hat=True)
    e = y - res["y_hat"]
    adj = e / (1.0 - res["S_diag"])
    return np.sqrt(np.mean(adj ** 2))