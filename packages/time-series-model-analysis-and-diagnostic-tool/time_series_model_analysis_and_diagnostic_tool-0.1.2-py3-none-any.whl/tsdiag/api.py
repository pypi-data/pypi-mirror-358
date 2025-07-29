"""
时间序列模型分析与诊断工具的高级API

提供简洁易用的Python库接口。
"""

import numpy as np
from typing import List, Union, Dict, Any, Tuple, Optional
from .core import stationarity_check, invertibility_check, StationarityResult, InvertibilityResult
from .stationarity import (
    check_ar_stationarity, 
    analyze_ar_stability_margin, 
    suggest_ar_modifications,
    batch_stationarity_check
)
from .invertibility import (
    check_ma_invertibility,
    analyze_ma_invertibility_margin,
    suggest_ma_modifications,
    batch_invertibility_check,
    compare_ma_models
)


class TSModelDiagnostic:
    """
    时间序列模型诊断类
    
    提供面向对象的接口来进行时间序列模型分析。
    """
    
    def __init__(self):
        self.ar_result: Optional[StationarityResult] = None
        self.ma_result: Optional[InvertibilityResult] = None
    
    def check_ar_model(
        self, 
        coefficients: Union[List[float], np.ndarray],
        verbose: bool = False
    ) -> StationarityResult:
        """
        检验AR模型的平稳性
        
        Args:
            coefficients: AR系数
            verbose: 是否显示详细信息
            
        Returns:
            StationarityResult: 检验结果
        """
        self.ar_result = check_ar_stationarity(coefficients, verbose=verbose)
        return self.ar_result
    
    def check_ma_model(
        self,
        coefficients: Union[List[float], np.ndarray],
        verbose: bool = False
    ) -> InvertibilityResult:
        """
        检验MA模型的可逆性
        
        Args:
            coefficients: MA系数
            verbose: 是否显示详细信息
            
        Returns:
            InvertibilityResult: 检验结果
        """
        self.ma_result = check_ma_invertibility(coefficients, verbose=verbose)
        return self.ma_result
    
    def check_arma_model(
        self,
        ar_coefficients: Union[List[float], np.ndarray],
        ma_coefficients: Union[List[float], np.ndarray],
        verbose: bool = False
    ) -> Tuple[StationarityResult, InvertibilityResult]:
        """
        检验ARMA模型的平稳性和可逆性
        
        Args:
            ar_coefficients: AR系数
            ma_coefficients: MA系数
            verbose: 是否显示详细信息
            
        Returns:
            Tuple: (平稳性检验结果, 可逆性检验结果)
        """
        ar_result = self.check_ar_model(ar_coefficients, verbose=verbose)
        ma_result = self.check_ma_model(ma_coefficients, verbose=verbose)
        return ar_result, ma_result
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取检验结果摘要
        
        Returns:
            Dict: 包含检验结果摘要的字典
        """
        summary = {
            'ar_checked': self.ar_result is not None,
            'ma_checked': self.ma_result is not None,
        }
        
        if self.ar_result:
            summary.update({
                'ar_stationary': self.ar_result.is_stationary,
                'ar_coefficients': self.ar_result.ar_coefficients,
                'ar_num_roots': len(self.ar_result.roots),
            })
        
        if self.ma_result:
            summary.update({
                'ma_invertible': self.ma_result.is_invertible,
                'ma_coefficients': self.ma_result.ma_coefficients,
                'ma_num_roots': len(self.ma_result.roots),
            })
        
        # 如果两个都检验了，提供综合评估
        if self.ar_result and self.ma_result:
            summary['arma_valid'] = self.ar_result.is_stationary and self.ma_result.is_invertible
        
        return summary


def quick_ar_check(coefficients: Union[List[float], np.ndarray]) -> bool:
    """
    快速AR平稳性检验，只返回布尔结果
    
    Args:
        coefficients: AR系数
        
    Returns:
        bool: 是否平稳
    """
    result = stationarity_check(coefficients)
    return result.is_stationary


def quick_ma_check(coefficients: Union[List[float], np.ndarray]) -> bool:
    """
    快速MA可逆性检验，只返回布尔结果
    
    Args:
        coefficients: MA系数
        
    Returns:
        bool: 是否可逆
    """
    result = invertibility_check(coefficients)
    return result.is_invertible


def quick_arma_check(
    ar_coefficients: Union[List[float], np.ndarray],
    ma_coefficients: Union[List[float], np.ndarray]
) -> Tuple[bool, bool]:
    """
    快速ARMA模型检验，只返回布尔结果
    
    Args:
        ar_coefficients: AR系数
        ma_coefficients: MA系数
        
    Returns:
        Tuple[bool, bool]: (是否平稳, 是否可逆)
    """
    ar_stationary = quick_ar_check(ar_coefficients)
    ma_invertible = quick_ma_check(ma_coefficients)
    return ar_stationary, ma_invertible


def _convert_numpy_types(obj):
    """递归转换字典中的Numpy类型为原生Python类型"""
    if isinstance(obj, dict):
        return {k: _convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_numpy_types(i) for i in obj]
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    return obj

def analyze_model_stability(
    ar_coefficients: Union[List[float], np.ndarray] = None,
    ma_coefficients: Union[List[float], np.ndarray] = None
) -> Dict[str, Any]:
    """
    全面分析模型稳定性
    
    Args:
        ar_coefficients: AR系数（可选）
        ma_coefficients: MA系数（可选）
        
    Returns:
        Dict: 包含详细分析结果的字典
    """
    analysis = {}
    
    if ar_coefficients is not None:
        ar_result = check_ar_stationarity(ar_coefficients, verbose=False)
        ar_stability = analyze_ar_stability_margin(ar_coefficients)
        ar_suggestions = suggest_ar_modifications(ar_coefficients)
        
        analysis['ar'] = {
            'is_stationary': ar_result.is_stationary,
            'coefficients': ar_result.ar_coefficients,
            'roots': [{'value': str(root.value), 'magnitude': root.magnitude, 
                      'outside_unit_circle': root.is_outside_unit_circle} 
                     for root in ar_result.roots],
            'stability_margin': ar_stability['stability_margin'],
            'risk_level': ar_stability['risk_level'],
            'suggestions': ar_suggestions['suggestions'],
            'suggested_coefficients': ar_suggestions.get('suggested_coefficients')
        }
    
    if ma_coefficients is not None:
        ma_result = check_ma_invertibility(ma_coefficients, verbose=False)
        ma_invertibility = analyze_ma_invertibility_margin(ma_coefficients)
        ma_suggestions = suggest_ma_modifications(ma_coefficients)
        
        analysis['ma'] = {
            'is_invertible': ma_result.is_invertible,
            'coefficients': ma_result.ma_coefficients,
            'roots': [{'value': str(root.value), 'magnitude': root.magnitude,
                      'outside_unit_circle': root.is_outside_unit_circle}
                     for root in ma_result.roots],
            'invertibility_margin': ma_invertibility['invertibility_margin'],
            'risk_level': ma_invertibility['risk_level'],
            'suggestions': ma_suggestions['suggestions'],
            'suggested_coefficients': ma_suggestions.get('suggested_coefficients')
        }
    
    # 综合评估
    if 'ar' in analysis and 'ma' in analysis:
        analysis['overall'] = {
            'model_valid': analysis['ar']['is_stationary'] and analysis['ma']['is_invertible'],
            'min_stability_margin': min(
                analysis['ar']['stability_margin'],
                analysis['ma']['invertibility_margin']
            ),
            'max_risk_level': max(
                ['low', 'medium', 'high'].index(analysis['ar']['risk_level']),
                ['low', 'medium', 'high'].index(analysis['ma']['risk_level'])
            )
        }
        analysis['overall']['max_risk_level'] = ['low', 'medium', 'high'][analysis['overall']['max_risk_level']]
    
    return _convert_numpy_types(analysis)


def batch_model_analysis(
    models: List[Dict[str, Union[List[float], np.ndarray]]],
    model_names: List[str] = None
) -> List[Dict[str, Any]]:
    """
    批量模型分析
    
    Args:
        models: 模型列表，每个模型是包含'ar'和/或'ma'键的字典
        model_names: 模型名称列表（可选）
        
    Returns:
        List[Dict]: 每个模型的分析结果
    """
    if model_names is None:
        model_names = [f"Model_{i+1}" for i in range(len(models))]
    
    if len(model_names) != len(models):
        raise ValueError("模型名称数量必须与模型数量相同")
    
    results = []
    
    for i, (model, name) in enumerate(zip(models, model_names)):
        try:
            ar_coeffs = model.get('ar')
            ma_coeffs = model.get('ma')
            
            analysis = analyze_model_stability(ar_coeffs, ma_coeffs)
            analysis['model_name'] = name
            analysis['model_index'] = i
            
            results.append(analysis)
            
        except Exception as e:
            results.append({
                'model_name': name,
                'model_index': i,
                'error': str(e)
            })
    
    return results
