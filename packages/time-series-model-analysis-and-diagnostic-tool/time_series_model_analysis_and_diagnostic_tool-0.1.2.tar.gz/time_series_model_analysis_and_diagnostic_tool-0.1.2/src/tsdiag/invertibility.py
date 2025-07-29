"""
MA模型可逆性检验模块

提供详细的MA模型可逆性检验功能，包括多种输入格式支持和详细的诊断信息。
"""

import numpy as np
from typing import List, Union, Dict, Any
from .core import invertibility_check as _core_invertibility_check, InvertibilityResult


def check_ma_invertibility(
    ma_coefficients: Union[List[float], np.ndarray, str],
    verbose: bool = True
) -> InvertibilityResult:
    """
    MA模型可逆性检验的高级接口
    
    支持多种输入格式，提供详细的诊断信息。
    
    Args:
        ma_coefficients: MA系数，支持以下格式：
            - 列表: [0.5, -0.3, 0.1]
            - numpy数组: np.array([0.5, -0.3, 0.1])
            - 字符串: "0.5,-0.3,0.1" 或 "0.5 -0.3 0.1"
        verbose: 是否输出详细信息
        
    Returns:
        InvertibilityResult: 检验结果
        
    Examples:
        >>> result = check_ma_invertibility([0.5, -0.3])
        >>> print(result.is_invertible)
        True
        
        >>> result = check_ma_invertibility("0.8,0.15")
        >>> print(result.message)
        模型满足可逆性条件：所有特征根都在单位圆外
    """
    # 处理字符串输入
    if isinstance(ma_coefficients, str):
        # 支持逗号或空格分隔
        coeffs_str = ma_coefficients.replace(',', ' ')
        try:
            coeffs = [float(x.strip()) for x in coeffs_str.split() if x.strip()]
        except ValueError as e:
            raise ValueError(f"无法解析MA系数字符串 '{ma_coefficients}': {e}")
    else:
        coeffs = ma_coefficients
    
    # 调用核心检验函数
    result = _core_invertibility_check(coeffs)
    
    if verbose:
        print("=" * 50)
        print("MA模型可逆性检验")
        print("=" * 50)
        print(result)
        print("=" * 50)
    
    return result


def analyze_ma_invertibility_margin(ma_coefficients: Union[List[float], np.ndarray]) -> Dict[str, Any]:
    """
    分析MA模型的可逆性边际
    
    计算根到单位圆的距离，提供可逆性的量化分析。
    
    Args:
        ma_coefficients: MA系数
        
    Returns:
        Dict: 包含可逆性分析的字典
            - min_distance_to_unit_circle: 最小根模长与1的差值
            - closest_root: 最接近单位圆的根
            - invertibility_margin: 可逆性边际（最小距离）
            - risk_level: 风险等级 ('low', 'medium', 'high')
    """
    result = _core_invertibility_check(ma_coefficients)
    
    if not result.roots:
        return {
            'min_distance_to_unit_circle': float('inf'),
            'closest_root': None,
            'invertibility_margin': float('inf'),
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
        'invertibility_margin': min_distance,
        'risk_level': risk_level,
        'all_distances': distances
    }


def suggest_ma_modifications(ma_coefficients: Union[List[float], np.ndarray]) -> Dict[str, Any]:
    """
    为不可逆MA模型提供修改建议
    
    Args:
        ma_coefficients: MA系数
        
    Returns:
        Dict: 包含修改建议的字典
    """
    result = _core_invertibility_check(ma_coefficients)
    
    suggestions = {
        'is_modification_needed': not result.is_invertible,
        'original_coefficients': result.ma_coefficients,
        'suggestions': []
    }
    
    if result.is_invertible:
        suggestions['suggestions'].append("模型已经满足可逆性条件，无需修改。")
        return suggestions
    
    # 分析问题根
    problematic_roots = [root for root in result.roots if not root.is_outside_unit_circle]
    
    suggestions['suggestions'].append(f"发现{len(problematic_roots)}个问题根（在单位圆内或单位圆上）")
    
    # 简单的修改建议
    if len(result.ma_coefficients) == 1:
        coeff = result.ma_coefficients[0]
        if abs(coeff) >= 1:
            new_coeff = 0.95 * np.sign(coeff)
            suggestions['suggestions'].append(f"建议将MA(1)系数从{coeff:.3f}调整为{new_coeff:.3f}")
            suggestions['suggested_coefficients'] = [new_coeff]
    else:
        # 对于高阶MA模型，建议缩放所有系数
        scale_factor = 0.9
        scaled_coeffs = [c * scale_factor for c in result.ma_coefficients]
        suggestions['suggestions'].append(f"建议将所有系数乘以{scale_factor}以确保可逆性")
        suggestions['suggested_coefficients'] = scaled_coeffs
    
    return suggestions


def batch_invertibility_check(
    ma_models: List[Union[List[float], np.ndarray]],
    model_names: List[str] = None
) -> List[Dict[str, Any]]:
    """
    批量进行MA模型可逆性检验
    
    Args:
        ma_models: MA模型系数列表
        model_names: 模型名称列表（可选）
        
    Returns:
        List[Dict]: 每个模型的检验结果
    """
    if model_names is None:
        model_names = [f"Model_{i+1}" for i in range(len(ma_models))]
    
    if len(model_names) != len(ma_models):
        raise ValueError("模型名称数量必须与模型数量相同")
    
    results = []
    
    for i, (coeffs, name) in enumerate(zip(ma_models, model_names)):
        try:
            result = _core_invertibility_check(coeffs)
            invertibility_analysis = analyze_ma_invertibility_margin(coeffs)
            
            results.append({
                'model_name': name,
                'model_index': i,
                'coefficients': result.ma_coefficients,
                'is_invertible': result.is_invertible,
                'num_roots': len(result.roots),
                'invertibility_margin': invertibility_analysis['invertibility_margin'],
                'risk_level': invertibility_analysis['risk_level'],
                'result': result
            })
        except Exception as e:
            results.append({
                'model_name': name,
                'model_index': i,
                'coefficients': None,
                'is_invertible': False,
                'error': str(e),
                'result': None
            })
    
    return results


def compare_ma_models(
    ma_models: List[Union[List[float], np.ndarray]],
    model_names: List[str] = None
) -> Dict[str, Any]:
    """
    比较多个MA模型的可逆性
    
    Args:
        ma_models: MA模型系数列表
        model_names: 模型名称列表（可选）
        
    Returns:
        Dict: 比较结果
    """
    results = batch_invertibility_check(ma_models, model_names)
    
    # 统计信息
    total_models = len(results)
    invertible_models = sum(1 for r in results if r.get('is_invertible', False))
    
    # 按可逆性边际排序
    valid_results = [r for r in results if 'invertibility_margin' in r]
    valid_results.sort(key=lambda x: x['invertibility_margin'], reverse=True)
    
    comparison = {
        'total_models': total_models,
        'invertible_models': invertible_models,
        'non_invertible_models': total_models - invertible_models,
        'invertibility_rate': invertible_models / total_models if total_models > 0 else 0,
        'best_model': valid_results[0] if valid_results else None,
        'worst_model': valid_results[-1] if valid_results else None,
        'all_results': results
    }
    
    return comparison
