"""
xtg.core.kernels
================

· 核函数工具箱 ·
-----------------------------------
提供 GWR / AGWR 常用的 **高斯核** 与 **双二次核 (bi-square)**，
支持：
  ① 各向同性（单带宽）
  ② 各向异性（东西向 bw_x，南北向 bw_y，轴对齐）
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

__all__ = [
    # 公共接口
    "gaussian_iso",
    "gaussian_aniso",
    "bisquare_iso",
    "bisquare_aniso",
    "get_kernel",
]


# --------------------------------------------------------------------------- #
# 1. Gaussian Kernel                                                          #
# --------------------------------------------------------------------------- #

def _guard_bw(*bws: float) -> None:  # pragma: no cover
    """带宽合法性检查：> 0 且不能全为 0。"""
    if any(b <= 0 for b in bws):
        raise ValueError("带宽必须为正数 (bw > 0)")


def gaussian_iso(
    dist: npt.ArrayLike,
    bw: float,
) -> np.ndarray:
    """
    各向同性高斯核
    w = exp(-(d / bw)²)

    Parameters
    ----------
    dist : array-like
        距离 (可为矩阵或向量)。
    bw : float
        带宽 > 0。

    Returns
    -------
    ndarray
        权重矩阵或向量，shape 与 `dist` 相同。
    """
    _guard_bw(bw)
    d = np.asarray(dist, dtype=float)
    w = np.exp(-(d / bw) ** 2)
    # 非负保证，防御浮点下溢
    w[w < 0.0] = 0.0
    return w


def gaussian_aniso(
    dx: npt.ArrayLike,
    dy: npt.ArrayLike,
    bw_x: float,
    bw_y: float,
) -> np.ndarray:
    """
    各向异性高斯核（轴对齐，不含旋转）
    w = exp(-(dx / bw_x)² - (dy / bw_y)²)

    Parameters
    ----------
    dx, dy : array-like
        与参考点在 x / y 方向的差值，shape 应一致。
    bw_x, bw_y : float
        在东西向 (x) 与南北向 (y) 的带宽。

    Returns
    -------
    ndarray
        权重矩阵或向量，shape 与 `dx` / `dy` 相同。
    """
    _guard_bw(bw_x, bw_y)
    dx = np.asarray(dx, dtype=float)
    dy = np.asarray(dy, dtype=float)
    w = np.exp(-(dx / bw_x) ** 2 - (dy / bw_y) ** 2)
    w[w < 0.0] = 0.0
    return w


# --------------------------------------------------------------------------- #
# 2. Bi-square Kernel                                                         #
# --------------------------------------------------------------------------- #

def _clip01(arr: np.ndarray) -> np.ndarray:
    """把输入裁剪到 [0, 1] 区间，返回裁剪结果。"""
    return np.clip(arr, 0.0, 1.0)


def bisquare_iso(
    dist: npt.ArrayLike,
    bw: float,
) -> np.ndarray:
    """
    各向同性双二次核
    w = (1 - (d / bw)²)²  for d < bw；否则 w = 0

    Returns
    -------
    ndarray
    """
    _guard_bw(bw)
    d = np.asarray(dist, dtype=float)
    r = _clip01(1.0 - (d / bw) ** 2)
    return r ** 2


def bisquare_aniso(
    dx: npt.ArrayLike,
    dy: npt.ArrayLike,
    bw_x: float,
    bw_y: float,
) -> np.ndarray:
    """
    各向异性双二次核
    w = (1 - (dx / bw_x)² - (dy / bw_y)²)²  若括号内 > 0，否则 w = 0
    """
    _guard_bw(bw_x, bw_y)
    dx = np.asarray(dx, dtype=float)
    dy = np.asarray(dy, dtype=float)
    r = _clip01(1.0 - (dx / bw_x) ** 2 - (dy / bw_y) ** 2)
    return r ** 2


# --------------------------------------------------------------------------- #
# 3. 灵活获取核函数                                                           #
# --------------------------------------------------------------------------- #

def get_kernel(
    name: str = "gaussian",
    anisotropic: bool = False,
):
    """
    根据名称返回对应核函数句柄。

    Parameters
    ----------
    name : {"gaussian", "bisquare"}
    anisotropic : bool, default=False
        - False → 返回各向同性版本 (dist, bw)
        - True  → 返回各向异性版本   (dx, dy, bw_x, bw_y)

    Returns
    -------
    callable
        使用方式见示例。

    Examples
    --------
    >>> fn = get_kernel("gaussian", anisotropic=False)
    >>> w = fn(dist_matrix, bw=1.5)
    """
    name = name.lower()
    if name not in {"gaussian", "bisquare"}:
        raise ValueError("暂只支持 'gaussian' 与 'bisquare' 两类核")

    if anisotropic:
        if name == "gaussian":
            return gaussian_aniso
        return bisquare_aniso
    else:
        if name == "gaussian":
            return gaussian_iso
        return bisquare_iso