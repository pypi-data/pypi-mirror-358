"""
xtg.select
==========

带宽搜索工具
-----------------------------------------
• select_bw_iso   —— 单标量带宽（各向同性）
• select_bw_aniso —— 向量/矩阵带宽（各向异性）
"""

from __future__ import annotations

from typing import Callable, Sequence

import numpy as np
from scipy.optimize import minimize, minimize_scalar


# --------------------------------------------------------------------------- #
# 1. 单标量带宽 —— select_bw_iso                                               #
# --------------------------------------------------------------------------- #

def select_bw_iso(
    objective: Callable[[float], float],
    *,
    bounds: tuple[float, float] | None = None,
    method: str | None = None,
    xtol: float = 1e-4,
    maxiter: int = 100,
) -> float:
    """
    搜索最优 *单一* 带宽 (各向同性)。

    Parameters
    ----------
    objective : callable(bw) -> float
        待最小化的目标函数 (AICc、CV、RMSE …)。
    bounds : (low, high), optional
        带宽搜索区间；若提供则自动使用 'bounded' 方法。
    method : {'golden', 'bounded', 'brent'} or None
        优化算法；None → 根据 bounds 自动选择。
    xtol : float
        收敛精度 (golden / brent) 或 xatol (bounded)。
    maxiter : int
        最大迭代次数。
    """
    # ---------------- 方法自动判定 ----------------
    if method is None:
        method = "bounded" if bounds is not None else "golden"
    elif bounds is not None and method != "bounded":
        raise ValueError("仅 method='bounded' 可以与 bounds= 同时使用。")

    # ---------------- SciPy 调用 ------------------
    opt_kwargs = {"maxiter": maxiter}
    if method == "bounded":
        opt_kwargs["xatol"] = xtol
    else:
        opt_kwargs["xtol"] = xtol

    res = minimize_scalar(
        objective,
        bounds=bounds,
        method=method,
        options=opt_kwargs,
    )
    if not res.success:  # pragma: no cover
        raise RuntimeError(f"带宽搜索失败：{res.message}")
    return float(res.x)


# --------------------------------------------------------------------------- #
# 2. 多维带宽 —— select_bw_aniso                                              #
# --------------------------------------------------------------------------- #

def _bounds_to_array(
    bounds: Sequence[tuple[float, float]] | None,
    ndim: int,
) -> np.ndarray:
    if bounds is None:
        return np.tile((1e-4, 10.0), (ndim, 1))
    if len(bounds) != ndim:
        raise ValueError("bounds 长度必须等于 ndim")
    return np.asarray(bounds, float)


def select_bw_aniso(
    objective: Callable[[np.ndarray], float],
    *,
    ndim: int,
    bounds: Sequence[tuple[float, float]] | None = None,
    bw_init: Sequence[float] | None = None,
    method: str = "L-BFGS-B",
    tol: float | None = 1e-5,
    maxiter: int = 200,
) -> np.ndarray:
    """
    搜索最优 *向量/矩阵* 带宽（各向异性），使用 SciPy minimize().

    Parameters
    ----------
    objective : callable(bw_vec) -> float
        输入 1-D ndarray(bw_vec) 长度为 ndim，返回待最小化的损失值。
    ndim : int
        待优化参数维度。
    bounds : sequence[(low, high)], optional
        每个维度的搜索区间。
    bw_init : sequence, optional
        初始猜测；默认取 bounds 中点。
    method : str, default 'L-BFGS-B'
        支持边界的 SciPy 优化器，例如 'Powell', 'TNC'。
    tol : float, optional
        收敛阈；None → SciPy 默认。
    maxiter : int, default 200
        最大迭代次数。
    """
    bounds_arr = _bounds_to_array(bounds, ndim)
    if bw_init is None:
        bw_init = np.mean(bounds_arr, axis=1)
    x0 = np.asarray(bw_init, float)
    if x0.size != ndim:
        raise ValueError("bw_init 长度必须与 ndim 一致")

    res = minimize(
        objective,
        x0=x0,
        method=method,
        bounds=bounds_arr,
        tol=tol,
        options={"maxiter": maxiter},
    )
    if not res.success:  # pragma: no cover
        raise RuntimeError(f"带宽搜索失败：{res.message}")
    return res.x.astype(float)


# --------------------------------------------------------------------------- #
# 导出符号                                                                    #
# --------------------------------------------------------------------------- #

__all__ = [
    "select_bw_iso",
    "select_bw_aniso",
]
