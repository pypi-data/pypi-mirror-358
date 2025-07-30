"""
xtg.models.sgwr
===============

半参数地理加权回归 (SGWR)
--------------------------------------------
• 指定哪些变量为全局 (global) / 局部 (local)
• 共用一条各向同性带宽
• 采用交替迭代 (back-fitting) 同时估计 βg & βl,i
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence, Literal

import numpy as np
from numpy.linalg import lstsq

from ..core.kernels import gaussian_iso, bisquare_iso
from ..metrics import rmse, aicc, pseudo_r2

__all__ = ["fit_sgwr", "SGWRResult"]


# --------------------------------------------------------------------------- #
# 1. 结果数据类                                                               #
# --------------------------------------------------------------------------- #

@dataclass
class SGWRResult:
    coef_global_: np.ndarray        # (p_g,)      全局系数
    coef_local_: np.ndarray         # (n, p_l)    局部系数
    bw_: float
    kernel_: str
    coords_: np.ndarray             # (n, 2)
    Xg_: np.ndarray                 # (n, p_g)
    Xl_: np.ndarray                 # (n, p_l)
    y_: np.ndarray                  # (n,)
    y_pred_: np.ndarray             # (n,)
    rmse_: float
    aicc_: float
    pseudo_r2_: float
    n_iter_: int

    # ---------------- 预测 ---------------- #
    def predict(
        self,
        Xg_new: np.ndarray,
        Xl_new: np.ndarray,
        coords_new: np.ndarray | None = None,
    ) -> np.ndarray:
        """
        若 coords_new=None 则默认自用局部系数组。
        """
        if coords_new is None:
            part_local = np.sum(self.coef_local_ * Xl_new, axis=1)
        else:
            coords_new = np.asarray(coords_new, float)
            dists = np.hypot(
                coords_new[:, None, 0] - self.coords_[None, :, 0],
                coords_new[:, None, 1] - self.coords_[None, :, 1],
            )
            nearest = np.argmin(dists, axis=1)
            betas = self.coef_local_[nearest]
            part_local = np.sum(betas * Xl_new, axis=1)

        return Xg_new @ self.coef_global_ + part_local


# --------------------------------------------------------------------------- #
# 2. 内部工具                                                                 #
# --------------------------------------------------------------------------- #

def _kernel(name: str):
    n = name.lower()
    if n == "gaussian":
        return gaussian_iso
    elif n == "bisquare":
        return bisquare_iso
    raise ValueError("kernel 仅支持 'gaussian' 或 'bisquare'")


# --------------------------------------------------------------------------- #
# 3. 主拟合函数                                                               #
# --------------------------------------------------------------------------- #

def fit_sgwr(
    X: np.ndarray | Iterable,
    y: np.ndarray | Iterable,
    coords: np.ndarray | Iterable,
    *,
    global_idx: Sequence[int],
    bw: float,
    kernel: Literal["gaussian", "bisquare"] = "gaussian",
    max_iter: int = 20,
    tol: float = 1e-6,
    compute_metrics: bool = True,
) -> SGWRResult:
    """
    Parameters
    ----------
    X : (n, p)   —— 全部自变量（不含截距）
    y : (n,)
    coords : (n, 2)
    global_idx : 变量索引序列
        指明哪些列归为全局系数；其余列视为局部系数。
    bw : float   —— 各向同性带宽
    """

    # --------- 输入拆分 ---------
    X = np.asarray(X, float)
    y = np.asarray(y, float).flatten()
    coords = np.asarray(coords, float)
    n, p = X.shape

    if bw <= 0:
        raise ValueError("带宽必须为正数")
    global_mask = np.zeros(p, bool)
    global_mask[list(global_idx)] = True

    Xg = X[:, global_mask]          # (n, p_g)
    Xl = X[:, ~global_mask]         # (n, p_l)
    p_g = Xg.shape[1]
    p_l = Xl.shape[1]
    kern = _kernel(kernel)

    # --------- 距离矩阵 ---------
    diff = coords[:, None, :] - coords[None, :, :]
    dist_mat = np.hypot(diff[..., 0], diff[..., 1])

    # --------- 初始化 βg ---------
    beta_g, *_ = lstsq(Xg, y, rcond=None)   # OLS 初始值

    # --------- 迭代回填 ---------
    for it in range(max_iter):
        # Step-1：基于当前 βg，计算残差
        r = y - Xg @ beta_g                # (n,)

        # Step-2：对残差进行 *普通 GWR* (单带宽) 得到 βl,i
        coef_l = np.empty((n, p_l))
        Xl_with1 = np.hstack([np.ones((n, 1)), Xl])   # (n, p_l+1)
        for i in range(n):
            w_i = kern(dist_mat[i], bw)
            w_i[i] = 0.0
            W = np.diag(w_i)
            XtW = Xl_with1.T @ W
            beta_i, *_ = lstsq(XtW @ Xl_with1, XtW @ r, rcond=None)
            coef_l[i] = beta_i[1:]                    # 去掉局部截距

        # Step-3：基于 βl,i 更新 βg (加权最小二乘)
        y_adj = y - np.sum(coef_l * Xl, axis=1)
        beta_g_new, *_ = lstsq(Xg, y_adj, rcond=None)

        # 收敛判定
        if np.linalg.norm(beta_g_new - beta_g) < tol:
            beta_g = beta_g_new
            break
        beta_g = beta_g_new
    else:
        it += 1  # max_iter 次也算一次

    # --------- 预测与指标 ---------
    y_hat = Xg @ beta_g + np.sum(coef_l * Xl, axis=1)

    if compute_metrics:
        rmse_val = rmse(y, y_hat)
        aicc_val = aicc(y, y_hat, k=p_g + 1)     # 近似
        pr2_val = pseudo_r2(y, y_hat)
    else:
        rmse_val = aicc_val = pr2_val = np.nan

    return SGWRResult(
        coef_global_=beta_g,
        coef_local_=coef_l,
        bw_=float(bw),
        kernel_=kernel,
        coords_=coords,
        Xg_=Xg,
        Xl_=Xl,
        y_=y,
        y_pred_=y_hat,
        rmse_=rmse_val,
        aicc_=aicc_val,
        pseudo_r2_=pr2_val,
        n_iter_=it + 1,
    )
