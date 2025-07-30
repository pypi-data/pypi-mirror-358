"""
xtg.select
==========

· 带宽搜索工具 ·
---------------------------------
- select_bw_iso  : 单标量带宽优化
- select_bw_aniso: 多维带宽向量 / 矩阵优化
"""

from __future__ import annotations

import math
from typing import Callable, Iterable, Sequence

import numpy as np

try:
    from scipy.optimize import minimize, minimize_scalar
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "xtg.select 依赖 SciPy 的优化器，请先运行 "
        "`pip install scipy`。"
    ) from _e


# ------------------------------------------------------------------------------
# 1. 单一带宽：select_bw_iso
# ------------------------------------------------------------------------------

def select_bw_iso(
    objective: Callable[[float], float],
    *,
    bounds: tuple[float, float] | None = None,
    method: str = "golden",
    xtol: float = 1e-4,
    maxiter: int = 100,
) -> float:
    """
    搜索最优 *标量* 带宽（各向同性）。

    Parameters
    ----------
    objective : callable
        接收 **单个标量** bw，返回待最小化的损失值
        （如 CV-score、AICc、RMSE 等）。
    bounds : 2-tuple, optional
        (lower, upper)。若为 None，则自动尝试 (ε, 5×ε)，其中
        ε = 10⁻⁴ * max(abs(bw_init), 1)；但更推荐明确给定。
    method : {"golden", "brent"}, default="golden"
        Minimize-scalar 的搜索策略。
    xtol : float, default=1e-4
        收敛精度（参考 SciPy 文档）。
    maxiter : int, default=100
        迭代上限。

    Returns
    -------
    float
        令 objective 最小的带宽值。
    """
    if bounds is None:
        # 粗略猜一个范围 (1e-4 ~ 10)；更建议用户显式指定
        bounds = (1e-4, 10.0)

    res = minimize_scalar(
        objective,
        bracket=None,
        bounds=bounds,
        method="golden" if method == "golden" else "brent",
        options={"maxiter": maxiter, "xtol": xtol},
    )
    if not res.success:  # pragma: no cover
        raise RuntimeError(
            f"带宽搜索失败：{res.message}；"
            "考虑扩大 bounds 或检查 objective 的可导性/稳定性。"
        )
    return float(res.x)


# ------------------------------------------------------------------------------
# 2. 多维带宽：select_bw_aniso
# ------------------------------------------------------------------------------

def _to_bounds_arr(
    bounds: Sequence[tuple[float, float]] | None,
    ndim: int,
) -> np.ndarray:
    """
    将 Python 列表/元组的 bounds 转成 (ndim, 2) 的 ndarray。
    """
    if bounds is None:
        # 默认在 (1e-4, 10) 区间内搜索
        b = np.tile((1e-4, 10.0), (ndim, 1))
    else:
        if len(bounds) != ndim:  # pragma: no cover
            raise ValueError("bounds 长度必须等于带宽维度 ndim")
        b = np.asarray(bounds, dtype=float)
    return b


def select_bw_aniso(
    objective: Callable[[np.ndarray], float],
    *,
    ndim: int,
    bounds: Sequence[tuple[float, float]] | None = None,
    bw_init: Iterable[float] | None = None,
    method: str = "L-BFGS-B",
    tol: float | None = 1e-5,
    maxiter: int = 200,
) -> np.ndarray:
    """
    搜索最优 *向量或矩阵* 带宽（各向异性）。

    Parameters
    ----------
    objective : callable
        接收 **一维 ndarray (ndim,)**，返回待最小化的损失值。
        如果带宽本身需要矩阵形式（如 p × 2），可自行在闭包中 reshape。
    ndim : int
        待优化参数维度（= 带宽元素个数）。
    bounds : sequence[(low, high)], optional
        每个维度的 (lower, upper)；若为 None 则默认 (1e-4, 10)。
    bw_init : 1-D iterable, optional
        初始猜测值；若 None 则用每维中点 `(low + high) / 2`。
    method : str, default="L-BFGS-B"
        传递给 SciPy `minimize` 的方法；L-BFGS-B 支持 box-bound。
    tol : float, optional
        收敛阈值；传 None 使用 SciPy 默认。
    maxiter : int, default=200
        最大迭代次数。

    Returns
    -------
    ndarray, shape (ndim,)
        令 objective 最小的带宽向量。
    """
    bounds_arr = _to_bounds_arr(bounds, ndim)
    if bw_init is None:
        bw_init = np.mean(bounds_arr, axis=1)
    x0 = np.asarray(bw_init, dtype=float)
    if x0.size != ndim:  # pragma: no cover
        raise ValueError("bw_init 长度必须等于 ndim")

    res = minimize(
        objective,
        x0=x0,
        method=method,
        bounds=bounds_arr,
        tol=tol,
        options={"maxiter": maxiter},
    )
    if not res.success:  # pragma: no cover
        raise RuntimeError(
            f"带宽搜索失败：{res.message}；"
            "可尝试不同初始值或更宽的 bounds。"
        )
    return res.x.astype(float)


# ------------------------------------------------------------------------------
# 导出
# ------------------------------------------------------------------------------

__all__ = [
    "select_bw_iso",
    "select_bw_aniso",
]