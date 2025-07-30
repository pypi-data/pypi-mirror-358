"""
xtg
===
扩展型地理加权回归工具箱
--------------------------------
- OLS / GWR / SGWR / MGWR / AGWR
- 带宽搜索、空间诊断、评估指标
"""

from importlib import metadata as _metadata

# ------------------------------------------------------------------------------
# 版本号
# ------------------------------------------------------------------------------
try:
    __version__: str = _metadata.version(__name__)
except _metadata.PackageNotFoundError:      # 开发环境
    __version__ = "0.0.0.dev0"

# ------------------------------------------------------------------------------
# ⬇⬇ 必须在顶层显式 import，IDE 才能解析到符号 -------------------------------
# ------------------------------------------------------------------------------
# 1) 评估指标
from .metrics import rmse, aicc, pseudo_r2

# 2) 空间诊断
from .diagnostics import vif, moran

# 3) 带宽搜索
from .select import select_bw_iso, select_bw_aniso

# 4) 模型接口
from .models.ols import fit_ols, OLSResult
from .models.gwr import fit_gwr, GWRResult
from .models.sgwr import fit_sgwr, SGWRResult
from .models.mgwr import fit_mgwr, MGWRResult
from .models.agwr import fit_agwr, AGWRResult
from .models.agwr_pc import fit_agwr_pc, AGWRPCResult

# ------------------------------------------------------------------------------
# 公共符号
# ------------------------------------------------------------------------------
__all__ = [
    "__version__",
    # 模型 & 结果
    "fit_ols", "OLSResult",
    "fit_gwr", "GWRResult",
    "fit_sgwr", "SGWRResult",
    "fit_mgwr", "MGWRResult",
    "fit_agwr", "AGWRResult",
    # 带宽搜索
    "select_bw_iso", "select_bw_aniso",
    # 诊断 & 评估
    "vif", "moran",
    "rmse", "aicc", "pseudo_r2",
    "fit_agwr_pc", "AGWRPCResult",
]
