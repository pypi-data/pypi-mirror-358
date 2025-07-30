# 0) 安装依赖（仅首次）
# pip install xtg pandas

import pandas as pd
import numpy as np

import inspect, xtg.select, os, importlib

print("XTG select.py 路径 →", xtg.select.__file__)
print("select_bw_iso 源码片段 →")
print(inspect.getsource(xtg.select.select_bw_iso).splitlines()[:10])


# -------- 1. 读入数据 --------
df = pd.read_csv("/Users/jm/Desktop/xtg/house_price_2021.csv", encoding="gb2312")

# -------- 2. 选定响应变量 y、自变量 X、坐标 coords --------
#   y：平均房价（AUP）       —— 待预测
#   X：挑 4 个经济/人口指标  —— 自行替换/增删即可
#   coords：经纬度           —— 必需
y = df["AUP"].values
X = df[["RRP", "GDP(10K)", "AVPI", "PG"]].values
coords = df[["longitude", "latitude"]].values


coords_std = (coords - coords.mean(0)) / coords.std(0)


# -------- 3. OLS 基准 --------
from xtg import fit_ols

ols = fit_ols(X, y)
print("OLS  ▸ RMSE =", ols.rmse_, "Pseudo-R² =", ols.pseudo_r2_)

# -------- 4. 单带宽 GWR --------
from xtg import fit_gwr, select_bw_iso

# (4-1) 先用 AICc 选最优带宽
def aicc_gwr(bw):
    return fit_gwr(X, y, coords, bw=bw).aicc_
best_bw = select_bw_iso(aicc_gwr,
                        bounds=(0.5, 5),   # 以前是 5–40
                        method="bounded")

print("GWR  ▸ 最优带宽 =", best_bw)

# (4-2) 用最优带宽重新拟合
gwr = fit_gwr(X, y, coords, bw=best_bw)
print("GWR  ▸ RMSE =", gwr.rmse_, "Pseudo-R² =", gwr.pseudo_r2_)

# -------- 5. 各向异性 AGWR --------
from xtg import fit_agwr, select_bw_aniso

# (5-1) 搜索东西向 / 南北向两个带宽（仍以 AICc 为目标）
def aicc_agwr(bw_vec):
    bwx, bwy = bw_vec
    res = fit_agwr(X, y, coords_std, bw=(bwx, bwy))
    return np.inf if np.isnan(res.aicc_) else res.aicc_

best_bwx, best_bwy = select_bw_aniso(
    aicc_agwr,
    ndim=2,
    bounds=[(0.5, 5), (0.5, 5)],
    bw_init=[2, 1.5],            # 初值也小一点
)

print("AGWR ▸ 最优带宽 (E-W, N-S) =", (best_bwx, best_bwy))

# (5-2) 拟合 AGWR
agwr = fit_agwr(X, y, coords, bw=(best_bwx, best_bwy))
print("AGWR ▸ RMSE =", agwr.rmse_, "Pseudo-R² =", agwr.pseudo_r2_)

# -------- 6. 对比结果 --------
from xtg import rmse, pseudo_r2  # 其实上面模型对象里已自带

print("\n=== 误差对比 ===")
print(f"OLS  : RMSE={ols.rmse_:.1f}  R²≈{ols.pseudo_r2_: .3f}")
print(f"GWR  : RMSE={gwr.rmse_:.1f}  R²≈{gwr.pseudo_r2_: .3f}")
print(f"AGWR : RMSE={agwr.rmse_:.1f}  R²≈{agwr.pseudo_r2_: .3f}")

# -------- 7. (可选) 新样本预测 --------
# 假设想预测某新区 (lon, lat)=(119.3, 31.8)，并有对应 4 个指标
X_new = np.array([[800_000, 12_500_000, 600_000, 18.0]])   # 形状 (1, 4)
coord_new = np.array([[119.3, 31.8]])

y_hat = agwr.predict(X_new, coord_new)
print("\n新点预测房价 ≈", y_hat[0])

