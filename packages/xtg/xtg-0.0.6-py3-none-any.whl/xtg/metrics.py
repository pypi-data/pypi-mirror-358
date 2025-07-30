"""
xtg.metrics
===========

· 评估指标 ·
-------------------------------
- rmse       : 均方根误差
- aicc       : 校正的 Akaike 信息准则
- pseudo_r2  : 拟似 R²（1 − SSR/SST）
"""

from __future__ import annotations

import math
import warnings
from typing import Iterable

import numpy as np


# ------------------------------------------------------------------------------
# 基础计算
# ------------------------------------------------------------------------------

def rss(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """残差平方和 (Residual Sum of Squares)."""
    return float(np.sum((y_true - y_pred) ** 2))


def mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """均方误差 (Mean Squared Error)."""
    return float(np.mean((y_true - y_pred) ** 2))


def rmse(
    y_true: Iterable[float] | np.ndarray,
    y_pred: Iterable[float] | np.ndarray,
) -> float:
    """
    均方根误差 (Root Mean Squared Error).

    Parameters
    ----------
    y_true, y_pred : array-like
        真实值与预测值，长度必须一致。

    Returns
    -------
    float
        RMSE 值，越小越好。
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    if y_true.shape != y_pred.shape:  # pragma: no cover
        raise ValueError("y_true 与 y_pred 维度不一致")
    return float(math.sqrt(mse(y_true, y_pred)))


# ------------------------------------------------------------------------------
# AICc：校正的 Akaike 信息准则
# ------------------------------------------------------------------------------

def aicc(y_true, y_pred, k, trace_s: float | None = None):
    """
    计算基于最小二乘残差的 AICc（小样本校正型 AIC）。

    公式：
        AIC  = n * ln(RSS / n) + 2k
        AICc = AIC + 2k(k + 1) / (n - k - 1)

    其中
        n : 样本量
        k : 可自由估计的参数个数（不含误差方差 σ²）

    **注意**：当 `n - k - 1 <= 0` 时，AICc 不再适用，
    本函数会触发警告并退回普通 AIC。

    Parameters
    ----------
    y_true, y_pred : array-like
        真实值与预测值。
    k : int
        参数个数。对 OLS 而言 = X 列数 (+ 截距)。

    Returns
    -------
    float
        AICc 值，越小越好。
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    n = y_true.size
    if n != y_pred.size:  # pragma: no cover
        raise ValueError("y_true 与 y_pred 长度应相同")

    rss_val = rss(y_true, y_pred)
    if rss_val <= 0:  # pragma: no cover
        raise ValueError("RSS 必须为正。")

    k_eff = trace_s if trace_s is not None else k
    aic = n * math.log(rss_val / n) + 2 * k_eff
    denom = n - k_eff - 1
    if denom <= 0:
        warnings.warn(
            "n - k - 1 <= 0，AICc 不适用，已返回普通 AIC。",
            RuntimeWarning,
            stacklevel=2,
        )
        return float(aic)
    return float(aic + (2 * k * (k + 1)) / denom)


# ------------------------------------------------------------------------------
# Pseudo-R²
# ------------------------------------------------------------------------------

def pseudo_r2(
    y_true: Iterable[float] | np.ndarray,
    y_pred: Iterable[float] | np.ndarray,
) -> float:
    """
    拟似 R²：1 - SSR / SST

    - SSR = Σ (y_true - y_pred)²
    - SST = Σ (y_true - ȳ)²

    介于 (-∞, 1]；越接近 1 说明拟合越好。

    Parameters
    ----------
    y_true, y_pred : array-like

    Returns
    -------
    float
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    if y_true.shape != y_pred.shape:  # pragma: no cover
        raise ValueError("y_true 与 y_pred 维度不一致")

    ssr = np.sum((y_true - y_pred) ** 2)
    sst = np.sum((y_true - np.mean(y_true)) ** 2)
    if sst == 0:  # pragma: no cover
        raise ValueError("SST = 0，无法计算 R²")

    return 1.0 - float(ssr / sst)


# ------------------------------------------------------------------------------
# 导出
# ------------------------------------------------------------------------------

__all__ = [
    "rmse",
    "aicc",
    "pseudo_r2",
    # 下面两个通常内部用，但一起导出也无妨
    "rss",
    "mse",
]