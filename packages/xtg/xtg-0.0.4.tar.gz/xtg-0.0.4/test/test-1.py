"""
示例：xtg 包完整评估流程
----------------------
目标：
• 读取 518fc768-b4bb-4578-b07c-3329e1c01e4a.csv
• 标准化坐标、检查空间自相关 / 共线性
• 对比 OLS ↔ GWR ↔ AGWR（坐标已标准化、log-变换后）
"""

import numpy as np
import pandas as pd
from xtg import (
    fit_ols, fit_gwr, fit_agwr,
    vif, moran,
    select_bw_iso, select_bw_aniso,
)

# ------------------------------------------------------------------ #
# 1. 读入数据
# ------------------------------------------------------------------ #
df = pd.read_csv("/Users/jm/Desktop/xtg/house_price_2021.csv", encoding="gb2312")

# ① 目标变量（房价）
y = df["AUP"].values
y_log = np.log1p(y)                 # log(1+y) 变换

# ② 解释变量（挑 4 列；可自行替换）
X_cols = ["RRP", "GDP(10K)", "AVPI", "PG"]
X = df[X_cols].values

# ③ 坐标并做标准化
coords = df[["longitude", "latitude"]].values
coords_std = (coords - coords.mean(0)) / coords.std(0)

print("\n>>> 样本规模:", X.shape[0])

# ------------------------------------------------------------------ #
# 2. 基础诊断
# ------------------------------------------------------------------ #
print("\n=== 共线性诊断（VIF）===")
print(vif(X, feature_names=X_cols))

mi = moran(y_log, coords=coords_std, k=8)
print(f"\n=== 空间自相关 (Moran's I) ===\nI = {mi['I']:.3f} "
      f"  p_sim = {mi['p_sim']:.3f}")

# ------------------------------------------------------------------ #
# 3. OLS（基准）
# ------------------------------------------------------------------ #
ols = fit_ols(X, y_log)
print(f"\nOLS  ▸ RMSE={ols.rmse_:.2f}  R²≈{ols.pseudo_r2_:.3f}")

# ------------------------------------------------------------------ #
# 4. GWR：单带宽
# ------------------------------------------------------------------ #
def obj_gwr(bw):
    res = fit_gwr(X, y_log, coords_std, bw=bw)
    return np.inf if np.isnan(res.aicc_) else res.aicc_

best_bw = select_bw_iso(
    obj_gwr,
    bounds=(0.5, 5),          # 坐标已标准化 → 小范围
)                             # 自动 method='bounded'

gwr = fit_gwr(X, y_log, coords_std, bw=best_bw)
print(f"\nGWR  ▸ bw={best_bw:.2f}  RMSE={gwr.rmse_:.2f} "
      f" R²≈{gwr.pseudo_r2_:.3f}")

# ------------------------------------------------------------------ #
# 5. AGWR：双向带宽
# ------------------------------------------------------------------ #
def obj_agwr(bw_vec):
    res = fit_agwr(X, y_log, coords_std, bw=tuple(bw_vec))
    return np.inf if np.isnan(res.aicc_) else res.aicc_

best_bwx, best_bwy = select_bw_aniso(
    obj_agwr,
    ndim=2,
    bounds=[(0.5, 5), (0.5, 5)],
    bw_init=[2.0, 1.5],
)   # 默认 L-BFGS-B

agwr = fit_agwr(X, y_log, coords_std, bw=(best_bwx, best_bwy))
print(f"\nAGWR ▸ bw(E-W)={best_bwx:.2f}, bw(N-S)={best_bwy:.2f}  "
      f"RMSE={agwr.rmse_:.2f}  R²≈{agwr.pseudo_r2_:.3f}")

# ------------------------------------------------------------------ #
# 6. 汇总
# ------------------------------------------------------------------ #
print("\n=== 误差对比 ===")
print(f"OLS  : RMSE={ols.rmse_:.2f}  R²≈{ols.pseudo_r2_:.3f}")
print(f"GWR  : RMSE={gwr.rmse_:.2f}  R²≈{gwr.pseudo_r2_:.3f}")
print(f"AGWR : RMSE={agwr.rmse_:.2f}  R²≈{agwr.pseudo_r2_:.3f}")

# ------------------------------------------------------------------ #
# 7. 新点预测示例
# ------------------------------------------------------------------ #
X_new = np.array([[800_000, 12_500_000, 600_000, 18.0]])
coord_new = np.array([[119.3, 31.8]])
coord_new_std = (coord_new - coords.mean(0)) / coords.std(0)
yhat = agwr.predict(X_new, coord_new_std)
print(f"\n预测房价（log）≈ {yhat[0]:.2f} → 还原 ≈ {np.expm1(yhat[0]):.0f}")




# 仅保留低 VIF 列
X_reduced = df[["RRP", "AVPI"]].values

# 自适应带宽示例：把 coords 按距离排序，取第 k=20 个距离作为每点 bw
from scipy.spatial.distance import cdist
dist_mat = cdist(coords_std, coords_std)
bw_knn = np.partition(dist_mat, kth=20, axis=1)[:, 20]

# 改写 fit_gwr 调用：每点单独 bw
from xtg.models.gwr import gaussian_iso
def gwr_knn(X, y, coords, bw_vec):
    n, p = X.shape
    Xc = np.hstack([np.ones((n, 1)), X])
    beta = np.empty((n, p + 1))
    for i in range(n):
        w = gaussian_iso(dist_mat[i], bw_vec[i])
        W = np.diag(w)
        beta[i], *_ = np.linalg.lstsq(Xc.T @ W @ Xc, Xc.T @ W @ y, rcond=None)
    y_hat = (beta * Xc).sum(1)
    print("RMSE-KNN:", np.sqrt(((y - y_hat) ** 2).mean()))
gwr_knn(X_reduced, y_log, coords_std, bw_knn)
