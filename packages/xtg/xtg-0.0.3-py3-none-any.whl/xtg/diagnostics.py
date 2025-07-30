"""
xtg.diagnostics
===============

✧ 变量共线性与空间自相关诊断工具 ✧
-------------------------------------------------
- vif   : 方差膨胀因子（Variance Inflation Factor）
- moran : 全局 Moran's I 空间自相关检验
"""

from __future__ import annotations

import warnings
from typing import Iterable, Optional, Sequence

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

try:
    # PySAL >= 23.1
    from libpysal.weights import DistanceBand, KNN, W
    from esda.moran import Moran
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "diagnostics.moran 需要安装 PySAL，"
        "请运行 `pip install pysal` 或在 pyproject.toml 中加入该依赖。"
    ) from _e


# ------------------------------------------------------------------------------
# 1. VIF（方差膨胀因子）
# ------------------------------------------------------------------------------

def vif(
    X: np.ndarray | pd.DataFrame,
    *,
    feature_names: Optional[Sequence[str]] = None,
    intercept: bool = True,
) -> pd.Series:
    """
    计算给定自变量矩阵的 VIF。

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        自变量矩阵。
    feature_names : list-like, optional
        每一列对应的名称；若为 ``None`` 且 X 是 DataFrame，
        则自动取其 ``columns``。
    intercept : bool, default=True
        计算 R² 时是否包含截距项。

    Returns
    -------
    pd.Series
        index 为特征名，value 为对应的 VIF 值。
    """
    # ---- 输入处理 ------------------------------------------------------------
    if isinstance(X, pd.DataFrame):
        X_mat = X.values
        names = X.columns.to_list()
    else:
        X_mat = np.asarray(X)
        if feature_names is None:
            names = [f"x{i}" for i in range(X_mat.shape[1])]
        else:
            names = list(feature_names)

    if X_mat.ndim != 2:
        raise ValueError("X 必须是二维矩阵 (n_samples, n_features)")

    n_samples, n_features = X_mat.shape
    if len(names) != n_features:  # pragma: no cover
        raise ValueError("feature_names 长度必须与 X 列数一致")

    # ---- 逐列回归 ------------------------------------------------------------
    vif_values: list[float] = []
    lr = LinearRegression(fit_intercept=intercept)
    for i in range(n_features):
        y_i = X_mat[:, i]
        X_rest = np.delete(X_mat, i, axis=1)
        lr.fit(X_rest, y_i)
        r2_i = lr.score(X_rest, y_i)  # R²
        vif_i = np.inf if r2_i >= 1.0 else 1.0 / (1.0 - r2_i)
        vif_values.append(vif_i)

    return pd.Series(vif_values, index=names, name="VIF")


# ------------------------------------------------------------------------------
# 2. Moran's I
# ------------------------------------------------------------------------------

def moran(
    y: Iterable[float] | np.ndarray | pd.Series,
    *,
    coords: Optional[np.ndarray] = None,
    W_matrix: Optional["W"] = None,
    k: int = 8,
    threshold: Optional[float] = None,
    permutations: int = 999,
    binary: bool = True,
    transformation: str = "r",
) -> dict[str, float]:
    """
    计算全局 Moran's I。

    Parameters
    ----------
    y : array-like, shape (n_samples,)
        待检验的变量。
    coords : ndarray of shape (n_samples, 2), optional
        点的经纬度或笛卡尔坐标；若 ``W_matrix`` 已给，则可省略。
    W_matrix : libpysal.weights.W, optional
        预构建的权重矩阵。若提供，则忽略 ``coords``、``k``、``threshold``。
    k : int, default=8
        KNN 权重的 k 值；当 ``threshold`` 为 ``None`` 时生效。
    threshold : float, optional
        距离阈值；若给定则构建 DistanceBand（建议用与数据同量纲的阈值）。
    permutations : int, default=999
        随机化检验的置换次数。
    binary : bool, default=True
        权重矩阵是否二值化（DistanceBand 有效）。
    transformation : str {"r", "B", "D", ...}, default="r"
        PySAL 提供的权重标准化方式。参见 libpysal 文档。

    Returns
    -------
    dict
        - ``I``      : Moran's I 统计量
        - ``z_norm`` : 正态近似 Z 值
        - ``p_norm`` : 正态近似 p 值
        - ``p_sim``  : 置换检验 p 值
    """
    y = np.asarray(y, dtype=float).flatten()
    if W_matrix is None:
        if coords is None:
            raise ValueError("未提供 coords 或 W_matrix，无法构建空间权重。")
        coords = np.asarray(coords, dtype=float)
        if coords.shape[0] != y.size:  # pragma: no cover
            raise ValueError("coords 与 y 的样本数不一致")

        if threshold is not None:
            W_matrix = DistanceBand(
                coords, threshold=threshold, binary=binary, silence_warnings=True
            )
        else:
            W_matrix = KNN.from_array(coords, k=k)

        if transformation:
            W_matrix.transform = transformation
    else:
        # 用已有权重矩阵，确保 transform
        if transformation and W_matrix.transform != transformation:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                W_matrix.transform = transformation

    mi = Moran(y, W_matrix, permutations=permutations)
    return {
        "I": float(mi.I),
        "z_norm": float(mi.z_norm),
        "p_norm": float(mi.p_norm),
        "p_sim": float(mi.p_sim),
    }