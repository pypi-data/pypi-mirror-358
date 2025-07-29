"""
时间序列模型分析与诊断工具

提供AR模型平稳性检验和MA模型可逆性检验功能。
"""

from .core import (
    stationarity_check,
    invertibility_check,
    StationarityResult,
    InvertibilityResult,
    RootInfo,
)

from .stationarity import (
    check_ar_stationarity,
    analyze_ar_stability_margin,
    suggest_ar_modifications,
    batch_stationarity_check,
)

from .invertibility import (
    check_ma_invertibility,
    analyze_ma_invertibility_margin,
    suggest_ma_modifications,
    batch_invertibility_check,
    compare_ma_models,
)

from .api import (
    TSModelDiagnostic,
    quick_ar_check,
    quick_ma_check,
    quick_arma_check,
    analyze_model_stability,
    batch_model_analysis,
)

__version__ = "0.1.0"
__all__ = [
    # 核心功能
    "stationarity_check",
    "invertibility_check",
    "StationarityResult",
    "InvertibilityResult",
    "RootInfo",

    # 平稳性检验
    "check_ar_stationarity",
    "analyze_ar_stability_margin",
    "suggest_ar_modifications",
    "batch_stationarity_check",

    # 可逆性检验
    "check_ma_invertibility",
    "analyze_ma_invertibility_margin",
    "suggest_ma_modifications",
    "batch_invertibility_check",
    "compare_ma_models",

    # 高级API
    "TSModelDiagnostic",
    "quick_ar_check",
    "quick_ma_check",
    "quick_arma_check",
    "analyze_model_stability",
    "batch_model_analysis",
]
