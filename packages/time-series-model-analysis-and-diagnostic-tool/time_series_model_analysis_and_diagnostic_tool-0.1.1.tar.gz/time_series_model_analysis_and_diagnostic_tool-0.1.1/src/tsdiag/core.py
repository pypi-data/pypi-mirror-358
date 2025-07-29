"""
时间序列模型分析与诊断工具的核心计算模块

包含AR模型平稳性检验和MA模型可逆性检验的核心数学计算功能。
"""

import numpy as np
from typing import List, Tuple, Union, NamedTuple
from dataclasses import dataclass


@dataclass
class RootInfo:
    """根的信息"""
    value: complex
    magnitude: float
    is_outside_unit_circle: bool
    
    def __str__(self) -> str:
        real_part = f"{self.value.real:.6f}"
        imag_part = f"{self.value.imag:+.6f}i" if self.value.imag != 0 else ""
        return f"{real_part}{imag_part} (|z|={self.magnitude:.6f})"


@dataclass
class StationarityResult:
    """平稳性检验结果"""
    is_stationary: bool
    roots: List[RootInfo]
    ar_coefficients: List[float]
    characteristic_polynomial: List[float]
    message: str
    
    def __str__(self) -> str:
        result = f"平稳性检验结果: {'平稳' if self.is_stationary else '非平稳'}\n"
        result += f"消息: {self.message}\n"
        result += f"AR系数: {self.ar_coefficients}\n"
        result += "特征多项式的根:\n"
        for i, root in enumerate(self.roots, 1):
            status = "✓" if root.is_outside_unit_circle else "✗"
            result += f"  根{i}: {root} {status}\n"
        return result


@dataclass
class InvertibilityResult:
    """可逆性检验结果"""
    is_invertible: bool
    roots: List[RootInfo]
    ma_coefficients: List[float]
    characteristic_polynomial: List[float]
    message: str
    
    def __str__(self) -> str:
        result = f"可逆性检验结果: {'可逆' if self.is_invertible else '不可逆'}\n"
        result += f"消息: {self.message}\n"
        result += f"MA系数: {self.ma_coefficients}\n"
        result += "特征多项式的根:\n"
        for i, root in enumerate(self.roots, 1):
            status = "✓" if root.is_outside_unit_circle else "✗"
            result += f"  根{i}: {root} {status}\n"
        return result


def _validate_coefficients(coefficients: Union[List[float], np.ndarray], name: str) -> List[float]:
    """验证系数输入"""
    if not isinstance(coefficients, (list, np.ndarray)):
        raise TypeError(f"{name}系数必须是列表或numpy数组")
    
    coeffs = list(coefficients)
    
    if len(coeffs) == 0:
        raise ValueError(f"{name}系数不能为空")
    
    # 检查是否都是数值
    try:
        coeffs = [float(c) for c in coeffs]
    except (ValueError, TypeError):
        raise ValueError(f"{name}系数必须都是数值")
    
    return coeffs


def _build_characteristic_polynomial(coefficients: List[float]) -> List[float]:
    """
    构建特征多项式
    
    对于AR(p)模型: 1 - φ₁z - φ₂z² - ... - φₚzᵖ = 0
    对于MA(q)模型: 1 + θ₁z + θ₂z² + ... + θₑzᵠ = 0
    
    返回多项式系数，从常数项到最高次项
    """
    # 特征多项式: 1 ± c₁z ± c₂z² ± ... ± cₙzⁿ
    poly_coeffs = [1.0]  # 常数项
    
    # 对于AR模型，系数前面是负号；对于MA模型，系数前面是正号
    # 这里统一处理，调用者负责传入正确的符号
    poly_coeffs.extend(coefficients)
    
    return poly_coeffs


def _compute_polynomial_roots(polynomial_coeffs: List[float]) -> List[RootInfo]:
    """计算多项式的根并返回根信息"""
    if len(polynomial_coeffs) <= 1:
        return []
    
    # numpy.roots需要从最高次项到常数项的系数
    # 我们的系数是从常数项到最高次项，所以需要反转
    coeffs_for_numpy = polynomial_coeffs[::-1]
    
    # 计算根
    roots = np.roots(coeffs_for_numpy)
    
    root_infos = []
    for root in roots:
        magnitude = abs(root)
        is_outside = magnitude > 1.0 + 1e-10  # 使用小的容差避免数值误差
        root_infos.append(RootInfo(
            value=complex(root),
            magnitude=magnitude,
            is_outside_unit_circle=is_outside
        ))
    
    return root_infos


def stationarity_check(ar_coefficients: Union[List[float], np.ndarray]) -> StationarityResult:
    """
    AR模型平稳性检验
    
    检验AR(p)模型: Xₜ = φ₁Xₜ₋₁ + φ₂Xₜ₋₂ + ... + φₚXₜ₋ₚ + εₜ
    的平稳性。
    
    平稳性条件：特征方程 1 - φ₁z - φ₂z² - ... - φₚzᵖ = 0 的所有根
    都在单位圆外（即所有根的模长都大于1）。
    
    Args:
        ar_coefficients: AR模型的系数 [φ₁, φ₂, ..., φₚ]
        
    Returns:
        StationarityResult: 包含检验结果的对象
        
    Raises:
        TypeError: 如果系数不是列表或numpy数组
        ValueError: 如果系数为空或包含非数值
    """
    # 验证输入
    coeffs = _validate_coefficients(ar_coefficients, "AR")
    
    # 构建特征多项式: 1 - φ₁z - φ₂z² - ... - φₚzᵖ
    # 对于AR模型，系数前面是负号
    negative_coeffs = [-c for c in coeffs]
    poly_coeffs = _build_characteristic_polynomial(negative_coeffs)
    
    # 计算根
    roots = _compute_polynomial_roots(poly_coeffs)
    
    # 判断平稳性：所有根都在单位圆外
    is_stationary = all(root.is_outside_unit_circle for root in roots)
    
    # 生成消息
    if is_stationary:
        message = "模型满足平稳性条件：所有特征根都在单位圆外"
    else:
        inside_count = sum(1 for root in roots if not root.is_outside_unit_circle)
        message = f"模型不满足平稳性条件：有{inside_count}个根在单位圆内或单位圆上"
    
    return StationarityResult(
        is_stationary=is_stationary,
        roots=roots,
        ar_coefficients=coeffs,
        characteristic_polynomial=poly_coeffs,
        message=message
    )


def invertibility_check(ma_coefficients: Union[List[float], np.ndarray]) -> InvertibilityResult:
    """
    MA模型可逆性检验
    
    检验MA(q)模型: Xₜ = εₜ + θ₁εₜ₋₁ + θ₂εₜ₋₂ + ... + θₑεₜ₋ₑ
    的可逆性。
    
    可逆性条件：特征方程 1 + θ₁z + θ₂z² + ... + θₑzᵠ = 0 的所有根
    都在单位圆外（即所有根的模长都大于1）。
    
    Args:
        ma_coefficients: MA模型的系数 [θ₁, θ₂, ..., θₑ]
        
    Returns:
        InvertibilityResult: 包含检验结果的对象
        
    Raises:
        TypeError: 如果系数不是列表或numpy数组
        ValueError: 如果系数为空或包含非数值
    """
    # 验证输入
    coeffs = _validate_coefficients(ma_coefficients, "MA")
    
    # 构建特征多项式: 1 + θ₁z + θ₂z² + ... + θₑzᵠ
    # 对于MA模型，系数前面是正号
    poly_coeffs = _build_characteristic_polynomial(coeffs)
    
    # 计算根
    roots = _compute_polynomial_roots(poly_coeffs)
    
    # 判断可逆性：所有根都在单位圆外
    is_invertible = all(root.is_outside_unit_circle for root in roots)
    
    # 生成消息
    if is_invertible:
        message = "模型满足可逆性条件：所有特征根都在单位圆外"
    else:
        inside_count = sum(1 for root in roots if not root.is_outside_unit_circle)
        message = f"模型不满足可逆性条件：有{inside_count}个根在单位圆内或单位圆上"
    
    return InvertibilityResult(
        is_invertible=is_invertible,
        roots=roots,
        ma_coefficients=coeffs,
        characteristic_polynomial=poly_coeffs,
        message=message
    )
