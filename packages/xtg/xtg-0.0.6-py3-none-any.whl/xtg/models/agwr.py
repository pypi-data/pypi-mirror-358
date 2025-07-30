"""
有待进一步更新
xtg.models.agwr
===============

各向异性地理加权回归 (AGWR) —— 轻量级实现
-------------------------------------------------
API
---
fit_agwr(X, y, coords, bw, ...)
    · 返回一个 `AGWRResult` 对象，属性：
        - coef_      : (n, p + 1) 每个观测点的局部系数（含截距）
        - bw_        : (bw_x, bw_y) 使用的带宽
        - kernel_    : 核函数名称
        - y_pred_    : 训练样本预测值
        - rmse_, aicc_, pseudo_r2_ : 全局评估指标
    · 方法：
        - predict(X_new, coords_new) : 使用就近样本系数进行预测
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Tuple

import numpy as np
from numpy.linalg import lstsq, inv

from ..core.kernels import (
    gaussian_aniso,
    bisquare_aniso,
)
from ..metrics import rmse, aicc, pseudo_r2

__all__ = [
    "fit_agwr",
    "AGWRResult",
]


# --------------------------------------------------------------------------- #
# 1. 结果数据类                                                               #
# --------------------------------------------------------------------------- #

@dataclass
class AGWRResult:
    coef_: np.ndarray           # (n, p + 1)
    bw_: Tuple[float, float]
    kernel_: str
    coords_: np.ndarray         # (n, 2)
    X_: np.ndarray              # 原始设计矩阵（含截距）
    y_: np.ndarray
    y_pred_: np.ndarray
    rmse_: float
    aicc_: float
    pseudo_r2_: float

    # ------------------ 方法 ------------------

    def predict(
        self,
        X_new: np.ndarray,
        coords_new: np.ndarray | None = None,
    ) -> np.ndarray:
        """
        使用与最近训练观测点相同的局部系数进行外插预测。

        Parameters
        ----------
        X_new : ndarray, shape (m, p)
            不含截距列的自变量。
        coords_new : ndarray, shape (m, 2), optional
            若为空则默认复用训练集坐标（等价于 y_pred_）。

        Returns
        -------
        ndarray, shape (m,)
            预测值。
        """
        if coords_new is None:
            # 直接用训练集的预测
            Xt = np.hstack([np.ones((self.X_.shape[0], 1)), X_new])
            return np.sum(self.coef_ * Xt, axis=1)

        # --------- 用最近邻匹配局部系数 ----------
        coords_new = np.asarray(coords_new, dtype=float)
        dists = np.hypot(
            coords_new[:, None, 0] - self.coords_[None, :, 0],
            coords_new[:, None, 1] - self.coords_[None, :, 1],
        )                                 # (m, n)
        nearest_idx = np.argmin(dists, axis=1)  # 最近训练样本索引 (m,)

        beta_used = self.coef_[nearest_idx]     # (m, p+1)
        Xt = np.hstack([np.ones((coords_new.shape[0], 1)), X_new])
        return np.sum(beta_used * Xt, axis=1)


# --------------------------------------------------------------------------- #
# 2. 核函数 dispatcher                                                        #
# --------------------------------------------------------------------------- #

def _kernel_fn(name: str):
    name = name.lower()
    if name == "gaussian":
        return gaussian_aniso
    elif name == "bisquare":
        return bisquare_aniso
    else:  # pragma: no cover
        raise ValueError("kernel 仅支持 'gaussian' 或 'bisquare'")


# --------------------------------------------------------------------------- #
# 3. 主拟合函数                                                               #
# --------------------------------------------------------------------------- #

def fit_agwr(
    X: np.ndarray,
    y: np.ndarray,
    coords: np.ndarray,
    bw: Tuple[float, float],
    *,
    kernel: Literal["gaussian", "bisquare"] = "gaussian",
    compute_metrics: bool = True,
) -> AGWRResult:
    """
    训练各向异性 GWR。

    Parameters
    ----------
    X : ndarray, shape (n, p)
        自变量（不含截距）。
    y : ndarray, shape (n,)
        因变量。
    coords : ndarray, shape (n, 2)
        每个观测的平面坐标。
    bw : (bw_x, bw_y)
        东西向与南北向的带宽。
    kernel : {"gaussian", "bisquare"}, default="gaussian"
        核函数类型。
    compute_metrics : bool, default=True
        是否计算 RMSE、AICc、Pseudo-R²（耗时 O(n²)）。

    Returns
    -------
    AGWRResult
    """
    # ---------------- 输入检查 -----------------
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float).flatten()
    coords = np.asarray(coords, dtype=float)
    n, p = X.shape
    if coords.shape != (n, 2):  # pragma: no cover
        raise ValueError("coords 形状应为 (n_samples, 2)")
    if y.size != n:  # pragma: no cover
        raise ValueError("y 与 X 样本量应一致")
    bw_x, bw_y = float(bw[0]), float(bw[1])
    if bw_x <= 0 or bw_y <= 0:  # pragma: no cover
        raise ValueError("带宽必须为正数")

    # ------- 预计算坐标差分 (dx, dy) ----------
    x_i = coords[:, 0][:, None]  # (n, 1)
    y_i = coords[:, 1][:, None]
    dx_mat = x_i - x_i.T         # (n, n)
    dy_mat = y_i - y_i.T

    kern = _kernel_fn(kernel)

    # ----------- 构造包含截距的设计矩阵 -------
    X_with_const = np.hstack([np.ones((n, 1)), X])  # (n, p+1)
    coef_loc = np.empty((n, p + 1), dtype=float)

    # ----------- 主循环：逐点拟合 -------------
    for i in range(n):
        w_vec = kern(dx_mat[i], dy_mat[i], bw_x, bw_y)  # (n,)
        w_vec[i] = 0.0                                 # 对角置 0（常见做法）

        # WLS：beta = (XᵀWX)⁻¹ XᵀWy
        W = np.diag(w_vec)
        XtW = X_with_const.T @ W                       # (p+1, n)
        XtWX = XtW @ X_with_const                      # (p+1, p+1)
        XtWy = XtW @ y                                # (p+1,)

        # 用 lstsq 避免奇异
        beta, *_ = lstsq(XtWX, XtWy, rcond=None)
        coef_loc[i] = beta

    # ----------- 训练集预测 & 评估 ------------
    y_pred = np.sum(coef_loc * X_with_const, axis=1)

    if compute_metrics:
        rmse_val = rmse(y, y_pred)
        # AICc 需要参数个数 k；此处采用 (p + 1) 近似
        aicc_val = aicc(y, y_pred, k=p + 1)
        pseudo_r2_val = pseudo_r2(y, y_pred)
    else:
        rmse_val = aicc_val = pseudo_r2_val = np.nan

    return AGWRResult(
        coef_=coef_loc,
        bw_=(bw_x, bw_y),
        kernel_=kernel,
        coords_=coords,
        X_=X_with_const,
        y_=y,
        y_pred_=y_pred,
        rmse_=rmse_val,
        aicc_=aicc_val,
        pseudo_r2_=pseudo_r2_val,
    )

