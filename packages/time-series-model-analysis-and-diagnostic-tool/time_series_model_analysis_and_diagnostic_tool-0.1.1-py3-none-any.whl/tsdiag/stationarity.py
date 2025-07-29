"""
AR模型平稳性检验模块

提供详细的AR模型平稳性检验功能，包括多种输入格式支持和详细的诊断信息。
"""

import numpy as np
from typing import List, Union, Dict, Any
from .core import stationarity_check as _core_stationarity_check, StationarityResult


def check_ar_stationarity(
    ar_coefficients: Union[List[float], np.ndarray, str],
    verbose: bool = True
) -> StationarityResult:
    """
    AR模型平稳性检验的高级接口
    
    支持多种输入格式，提供详细的诊断信息。
    
    Args:
        ar_coefficients: AR系数，支持以下格式：
            - 列表: [0.5, -0.3, 0.1]
            - numpy数组: np.array([0.5, -0.3, 0.1])
            - 字符串: "0.5,-0.3,0.1" 或 "0.5 -0.3 0.1"
        verbose: 是否输出详细信息
        
    Returns:
        StationarityResult: 检验结果
        
    Examples:
        >>> result = check_ar_stationarity([0.5, -0.3])
        >>> print(result.is_stationary)
        True
        
        >>> result = check_ar_stationarity("0.8,0.15")
        >>> print(result.message)
        模型满足平稳性条件：所有特征根都在单位圆外
    """
    # 处理字符串输入
    if isinstance(ar_coefficients, str):
        # 支持逗号或空格分隔
        coeffs_str = ar_coefficients.replace(',', ' ')
        try:
            coeffs = [float(x.strip()) for x in coeffs_str.split() if x.strip()]
        except ValueError as e:
            raise ValueError(f"无法解析AR系数字符串 '{ar_coefficients}': {e}")
    else:
        coeffs = ar_coefficients
    
    # 调用核心检验函数
    result = _core_stationarity_check(coeffs)
    
    if verbose:
        print("=" * 50)
        print("AR模型平稳性检验")
        print("=" * 50)
        print(result)
        print("=" * 50)
    
    return result


def analyze_ar_stability_margin(ar_coefficients: Union[List[float], np.ndarray]) -> Dict[str, Any]:
    """
    分析AR模型的稳定性边际
    
    计算根到单位圆的距离，提供稳定性的量化分析。
    
    Args:
        ar_coefficients: AR系数
        
    Returns:
        Dict: 包含稳定性分析的字典
            - min_distance_to_unit_circle: 最小根模长与1的差值
            - closest_root: 最接近单位圆的根
            - stability_margin: 稳定性边际（最小距离）
            - risk_level: 风险等级 ('low', 'medium', 'high')
    """
    result = _core_stationarity_check(ar_coefficients)
    
    if not result.roots:
        return {
            'min_distance_to_unit_circle': float('inf'),
            'closest_root': None,
            'stability_margin': float('inf'),
            'risk_level': 'low'
        }
    
    # 计算每个根到单位圆的距离
    distances = [root.magnitude - 1.0 for root in result.roots]
    min_distance = min(distances)
    closest_root_idx = distances.index(min_distance)
    closest_root = result.roots[closest_root_idx]
    
    # 确定风险等级
    if min_distance <= 0:
        risk_level = 'high'  # 根在单位圆内或单位圆上
    elif min_distance < 0.1:
        risk_level = 'medium'  # 根接近单位圆
    else:
        risk_level = 'low'  # 根远离单位圆
    
    return {
        'min_distance_to_unit_circle': min_distance,
        'closest_root': closest_root,
        'stability_margin': min_distance,
        'risk_level': risk_level,
        'all_distances': distances
    }


def suggest_ar_modifications(ar_coefficients: Union[List[float], np.ndarray]) -> Dict[str, Any]:
    """
    为非平稳AR模型提供修改建议
    
    Args:
        ar_coefficients: AR系数
        
    Returns:
        Dict: 包含修改建议的字典
    """
    result = _core_stationarity_check(ar_coefficients)
    
    suggestions = {
        'is_modification_needed': not result.is_stationary,
        'original_coefficients': result.ar_coefficients,
        'suggestions': []
    }
    
    if result.is_stationary:
        suggestions['suggestions'].append("模型已经满足平稳性条件，无需修改。")
        return suggestions
    
    # 分析问题根
    problematic_roots = [root for root in result.roots if not root.is_outside_unit_circle]
    
    suggestions['suggestions'].append(f"发现{len(problematic_roots)}个问题根（在单位圆内或单位圆上）")
    
    # 简单的修改建议
    if len(result.ar_coefficients) == 1:
        coeff = result.ar_coefficients[0]
        if abs(coeff) >= 1:
            new_coeff = 0.95 * np.sign(coeff)
            suggestions['suggestions'].append(f"建议将AR(1)系数从{coeff:.3f}调整为{new_coeff:.3f}")
            suggestions['suggested_coefficients'] = [new_coeff]
    else:
        # 对于高阶AR模型，建议缩放所有系数
        scale_factor = 0.9
        scaled_coeffs = [c * scale_factor for c in result.ar_coefficients]
        suggestions['suggestions'].append(f"建议将所有系数乘以{scale_factor}以确保平稳性")
        suggestions['suggested_coefficients'] = scaled_coeffs
    
    return suggestions


def batch_stationarity_check(
    ar_models: List[Union[List[float], np.ndarray]],
    model_names: List[str] = None
) -> List[Dict[str, Any]]:
    """
    批量进行AR模型平稳性检验
    
    Args:
        ar_models: AR模型系数列表
        model_names: 模型名称列表（可选）
        
    Returns:
        List[Dict]: 每个模型的检验结果
    """
    if model_names is None:
        model_names = [f"Model_{i+1}" for i in range(len(ar_models))]
    
    if len(model_names) != len(ar_models):
        raise ValueError("模型名称数量必须与模型数量相同")
    
    results = []
    
    for i, (coeffs, name) in enumerate(zip(ar_models, model_names)):
        try:
            result = _core_stationarity_check(coeffs)
            stability_analysis = analyze_ar_stability_margin(coeffs)
            
            results.append({
                'model_name': name,
                'model_index': i,
                'coefficients': result.ar_coefficients,
                'is_stationary': result.is_stationary,
                'num_roots': len(result.roots),
                'stability_margin': stability_analysis['stability_margin'],
                'risk_level': stability_analysis['risk_level'],
                'result': result
            })
        except Exception as e:
            results.append({
                'model_name': name,
                'model_index': i,
                'coefficients': None,
                'is_stationary': False,
                'error': str(e),
                'result': None
            })
    
    return results
