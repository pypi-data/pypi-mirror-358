"""
xtg.models.ols
==============

普通最小二乘回归 (OLS)
---------------------------------------------
• fit_ols(X, y, add_intercept=True, ...)
      → 返回 OLSResult
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.linalg import lstsq
from typing import Iterable

from ..metrics import rmse, aicc, pseudo_r2

__all__ = ["fit_ols", "OLSResult"]


# --------------------------------------------------------------------------- #
# 1. 结果数据类                                                               #
# --------------------------------------------------------------------------- #

@dataclass
class OLSResult:
    coef_: np.ndarray            # (p,)                   —— 不含截距
    intercept_: float
    params_: np.ndarray          # (p+1,)                 —— 含截距
    X_: np.ndarray               # (n, p+1) or (n, p)     —— 设计矩阵
    y_: np.ndarray               # (n,)
    y_pred_: np.ndarray          # (n,)
    rmse_: float
    aicc_: float
    r2_: float
    pseudo_r2_: float

    # ---------------- 预测 ---------------- #
    def predict(self, X_new: np.ndarray) -> np.ndarray:
        X_new = np.asarray(X_new, float)
        if self.intercept_ is not None:
            return self.intercept_ + X_new @ self.coef_
        return X_new @ self.coef_


# --------------------------------------------------------------------------- #
# 2. 主拟合函数                                                               #
# --------------------------------------------------------------------------- #

def fit_ols(
    X: np.ndarray | Iterable,
    y: np.ndarray | Iterable,
    *,
    add_intercept: bool = True,
    compute_metrics: bool = True,
) -> OLSResult:
    """
    拟合普通最小二乘线性回归。

    Parameters
    ----------
    X : array-like, shape (n, p)
        自变量（若 `add_intercept=True` 则不含截距列）。
    y : array-like, shape (n,)
        因变量。
    add_intercept : bool, default=True
        是否自动在设计矩阵左侧添加常数 1。
    compute_metrics : bool, default=True
        是否计算 RMSE / AICc / R² / Pseudo-R²。

    Returns
    -------
    OLSResult
    """
    # ---------- 输入整理 ----------
    X = np.asarray(X, float)
    y = np.asarray(y, float).flatten()
    n, p = X.shape
    if y.size != n:
        raise ValueError("X 与 y 的样本数不一致。")

    if add_intercept:
        X_design = np.hstack([np.ones((n, 1)), X])   # (n, p+1)
    else:
        X_design = X
    k_params = X_design.shape[1]

    # ---------- 最小二乘 ----------
    params, *_ = lstsq(X_design, y, rcond=None)
    if add_intercept:
        intercept = float(params[0])
        coef = params[1:]
    else:
        intercept = None
        coef = params

    # ---------- 预测 ----------
    y_hat = X_design @ params

    # ---------- 指标 ----------
    if compute_metrics:
        rmse_val = rmse(y, y_hat)
        aicc_val = aicc(y, y_hat, k=k_params)
        r2_val = pseudo_r2(y, y_hat)           # 对 OLS 等价于 R²
        pr2_val = r2_val
    else:
        rmse_val = aicc_val = r2_val = pr2_val = np.nan

    return OLSResult(
        coef_=coef,
        intercept_=intercept,
        params_=params,
        X_=X_design,
        y_=y,
        y_pred_=y_hat,
        rmse_=rmse_val,
        aicc_=aicc_val,
        r2_=r2_val,
        pseudo_r2_=pr2_val,
    )
