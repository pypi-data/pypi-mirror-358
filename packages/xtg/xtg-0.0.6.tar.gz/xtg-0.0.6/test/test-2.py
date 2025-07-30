"""
xtg_validation_demo.py
----------------------

验证新版 xtg：
• 带帽子矩阵 trace(S) 的 Per-Coefficient Anisotropic AGWR
• 自动 bounded / golden 带宽搜索
"""

import numpy as np
import pandas as pd
from xtg import (
    fit_ols, fit_gwr, fit_agwr, vif, moran,
    select_bw_iso, select_bw_aniso,
)
from xtg.models.agwr_pc import fit_agwr_pc
from xtg.models.gwr_knn import fit_gwr_knn

# ----------------------------------------------------------
# 1. 读数据 & 预处理
# ----------------------------------------------------------
df = pd.read_csv("/Users/jm/Desktop/xtg/house_price_2021.csv", encoding="gb2312")

y = np.log1p(df["AUP"].values)                 # log(1+y)
X_cols = ["RRP", "AVPI"]                       # 低 VIF 两列
X = df[X_cols].values

coords = df[["longitude", "latitude"]].values
coords_std = (coords - coords.mean(0)) / coords.std(0)

print("\n样本量:", len(df))

# ----------------------------------------------------------
# 2. 空间与共线性诊断
# ----------------------------------------------------------
print("\nVIF:\n", vif(X, feature_names=X_cols))
mi = moran(y, coords=coords_std, k=8)
print(f"Moran's I = {mi['I']:.3f}  p_sim = {mi['p_sim']:.3f}")

# ----------------------------------------------------------
# 3. OLS
# ----------------------------------------------------------
ols = fit_ols(X, y)
print(f"\nOLS ▸ RMSE={ols.rmse_:.3f}  R²≈{ols.pseudo_r2_:.3f}")

# ----------------------------------------------------------
# 4. GWR (单带宽)
# ----------------------------------------------------------
best_bw = select_bw_iso(
    lambda bw: fit_gwr(X, y, coords_std, bw=bw).aicc_,
    bounds=(0.5, 3),      # 因为 coords 已标准化
)
gwr = fit_gwr(X, y, coords_std, best_bw)
print(f"GWR ▸ bw={best_bw:.2f}  RMSE={gwr.rmse_:.3f}  R²≈{gwr.pseudo_r2_:.3f}")

# ----------------------------------------------------------
# 5. AGWR (共用双带宽)
# ----------------------------------------------------------
best_bwx, best_bwy = select_bw_aniso(
    lambda b: fit_agwr(X, y, coords_std, bw=tuple(b)).aicc_,
    ndim=2,
    bounds=[(0.5, 3)] * 2,
    bw_init=[1.5, 1.0],
)
agwr = fit_agwr(X, y, coords_std, bw=(best_bwx, best_bwy))
print(f"AGWR ▸ (bwE={best_bwx:.2f}, bwN={best_bwy:.2f})  "
      f"RMSE={agwr.rmse_:.3f}  R²≈{agwr.pseudo_r2_:.3f}")

# ----------------------------------------------------------
# 6. Per-Coefficient Anisotropic AGWR  (PC-AGWR)
# ----------------------------------------------------------
p = X.shape[1]
def obj_pc(bw_flat):
    bw_mat = bw_flat.reshape(p + 1, 2)
    return fit_agwr_pc(X, y, coords_std, bw_mat=bw_mat).aicc_

bw_flat_opt = select_bw_aniso(
    obj_pc,
    ndim=2 * (p + 1),
    bounds=[(0.5, 3)] * (2 * (p + 1)),
    bw_init=np.tile([1.5, 1.0], p + 1),
)
bw_mat_opt = bw_flat_opt.reshape(p + 1, 2)
agwr_pc = fit_agwr_pc(X, y, coords_std, bw_mat_opt)

print(f"PC-AGWR ▸ trace(S)={agwr_pc.trace_s_:.1f}  "
      f"RMSE={agwr_pc.rmse_:.3f}  R²≈{agwr_pc.pseudo_r2_:.3f}")

# ----------------------------------------------------------
# 7. 自适应 KNN-GWR
# ----------------------------------------------------------
gwr_knn = fit_gwr_knn(X, y, coords_std, k=20)
print(f"KNN-GWR ▸ k=20  RMSE={gwr_knn['rmse']:.3f}  "
      f"R²≈{gwr_knn['r2']:.3f}")

# ----------------------------------------------------------
# 8. 对比汇总
# ----------------------------------------------------------
print("\n=== 模型误差对比 (RMSE) ===")
print(f"OLS       : {ols.rmse_:.3f}")
print(f"GWR       : {gwr.rmse_:.3f}")
print(f"AGWR      : {agwr.rmse_:.3f}")
print(f"PC-AGWR   : {agwr_pc.rmse_:.3f}")
print(f"KNN-GWR   : {gwr_knn['rmse']:.3f}")

# ----------------------------------------------------------
# 9. 预测示例
# ----------------------------------------------------------
X_new = np.array([[800_000, 600_000]])         # [RRP, AVPI]
coord_new = np.array([[119.3, 31.8]])
coord_new_std = (coord_new - coords.mean(0)) / coords.std(0)

y_pred_log = agwr_pc.predict(X_new, coord_new_std)
print(f"\n新点房价预测 ≈ {np.expm1(y_pred_log[0]):.0f}")
