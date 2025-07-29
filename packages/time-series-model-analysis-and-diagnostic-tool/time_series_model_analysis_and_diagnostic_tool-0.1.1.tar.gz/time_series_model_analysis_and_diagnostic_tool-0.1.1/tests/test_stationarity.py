"""
平稳性检验模块测试
"""

import pytest
import numpy as np
from tsdiag.stationarity import (
    check_ar_stationarity,
    analyze_ar_stability_margin,
    suggest_ar_modifications,
    batch_stationarity_check
)


class TestCheckArStationarity:
    """测试AR平稳性检验高级接口"""
    
    def test_list_input(self):
        """测试列表输入"""
        result = check_ar_stationarity([0.5, -0.3], verbose=False)
        assert result.is_stationary
        assert result.ar_coefficients == [0.5, -0.3]
    
    def test_numpy_input(self):
        """测试numpy数组输入"""
        result = check_ar_stationarity(np.array([0.5, -0.3]), verbose=False)
        assert result.is_stationary
        assert result.ar_coefficients == [0.5, -0.3]
    
    def test_string_input_comma_separated(self):
        """测试逗号分隔的字符串输入"""
        result = check_ar_stationarity("0.5,-0.3", verbose=False)
        assert result.is_stationary
        assert result.ar_coefficients == [0.5, -0.3]
    
    def test_string_input_space_separated(self):
        """测试空格分隔的字符串输入"""
        result = check_ar_stationarity("0.5 -0.3", verbose=False)
        assert result.is_stationary
        assert result.ar_coefficients == [0.5, -0.3]
    
    def test_string_input_mixed_separators(self):
        """测试混合分隔符的字符串输入"""
        result = check_ar_stationarity("0.5, -0.3 0.1", verbose=False)
        assert result.ar_coefficients == [0.5, -0.3, 0.1]
    
    def test_invalid_string_input(self):
        """测试无效字符串输入"""
        with pytest.raises(ValueError, match="无法解析AR系数字符串"):
            check_ar_stationarity("0.5,invalid,-0.3", verbose=False)
    
    def test_verbose_output(self, capsys):
        """测试详细输出"""
        check_ar_stationarity([0.5], verbose=True)
        captured = capsys.readouterr()
        assert "AR模型平稳性检验" in captured.out
        assert "=" in captured.out


class TestAnalyzeArStabilityMargin:
    """测试AR稳定性边际分析"""
    
    def test_stable_model(self):
        """测试稳定模型"""
        analysis = analyze_ar_stability_margin([0.5])
        assert analysis['min_distance_to_unit_circle'] == 1.0  # |z| = 2, distance = 2-1 = 1
        assert analysis['stability_margin'] == 1.0
        assert analysis['risk_level'] == 'low'
        assert analysis['closest_root'] is not None
    
    def test_unstable_model(self):
        """测试不稳定模型"""
        analysis = analyze_ar_stability_margin([1.1])
        assert analysis['min_distance_to_unit_circle'] < 0
        assert analysis['stability_margin'] < 0
        assert analysis['risk_level'] == 'high'
    
    def test_marginal_model(self):
        """测试边际稳定模型"""
        analysis = analyze_ar_stability_margin([0.95])  # |z| ≈ 1.05, distance ≈ 0.05
        assert 0 < analysis['min_distance_to_unit_circle'] < 0.1
        assert analysis['risk_level'] == 'medium'
    
    def test_no_roots(self):
        """测试无根情况（理论上不会发生，但测试边界情况）"""
        # 这个测试可能需要模拟特殊情况
        pass


class TestSuggestArModifications:
    """测试AR模型修改建议"""
    
    def test_stationary_model_no_suggestions(self):
        """测试平稳模型无需修改"""
        suggestions = suggest_ar_modifications([0.5])
        assert not suggestions['is_modification_needed']
        assert "无需修改" in suggestions['suggestions'][0]
    
    def test_non_stationary_ar1_suggestions(self):
        """测试非平稳AR(1)模型建议"""
        suggestions = suggest_ar_modifications([1.1])
        assert suggestions['is_modification_needed']
        assert 'suggested_coefficients' in suggestions
        assert abs(suggestions['suggested_coefficients'][0]) < 1.0
    
    def test_non_stationary_ar2_suggestions(self):
        """测试非平稳AR(2)模型建议"""
        suggestions = suggest_ar_modifications([1.2, -0.1])
        assert suggestions['is_modification_needed']
        assert 'suggested_coefficients' in suggestions
        assert len(suggestions['suggested_coefficients']) == 2
        # 建议的系数应该是原系数的缩放版本
        original = [1.2, -0.1]
        suggested = suggestions['suggested_coefficients']
        scale_factor = suggested[0] / original[0]
        assert abs(scale_factor - 0.9) < 1e-10
    
    def test_unit_root_suggestions(self):
        """测试单位根模型建议"""
        suggestions = suggest_ar_modifications([1.0])
        assert suggestions['is_modification_needed']
        assert 'suggested_coefficients' in suggestions


class TestBatchStationarityCheck:
    """测试批量平稳性检验"""
    
    def test_multiple_models(self):
        """测试多个模型"""
        models = [
            [0.5],      # 平稳
            [1.1],      # 非平稳
            [0.5, -0.3] # 平稳
        ]
        results = batch_stationarity_check(models)
        
        assert len(results) == 3
        assert results[0]['is_stationary'] == True
        assert results[1]['is_stationary'] == False
        assert results[2]['is_stationary'] == True
        
        # 检查模型名称
        assert results[0]['model_name'] == 'Model_1'
        assert results[1]['model_name'] == 'Model_2'
        assert results[2]['model_name'] == 'Model_3'
    
    def test_custom_model_names(self):
        """测试自定义模型名称"""
        models = [[0.5], [1.1]]
        names = ['Stable_Model', 'Unstable_Model']
        results = batch_stationarity_check(models, names)
        
        assert results[0]['model_name'] == 'Stable_Model'
        assert results[1]['model_name'] == 'Unstable_Model'
    
    def test_mismatched_names_length(self):
        """测试名称数量不匹配"""
        models = [[0.5], [1.1]]
        names = ['Only_One_Name']
        
        with pytest.raises(ValueError, match="模型名称数量必须与模型数量相同"):
            batch_stationarity_check(models, names)
    
    def test_invalid_model_in_batch(self):
        """测试批量中包含无效模型"""
        models = [
            [0.5],      # 有效
            [],         # 无效：空列表
            [0.5, -0.3] # 有效
        ]
        results = batch_stationarity_check(models)
        
        assert len(results) == 3
        assert results[0]['is_stationary'] == True
        assert 'error' in results[1]  # 第二个模型应该有错误
        assert results[2]['is_stationary'] == True
    
    def test_stability_analysis_in_batch(self):
        """测试批量结果中的稳定性分析"""
        models = [[0.5], [0.95]]  # 一个低风险，一个中等风险
        results = batch_stationarity_check(models)
        
        assert results[0]['risk_level'] == 'low'
        assert results[1]['risk_level'] == 'medium'
        assert results[0]['stability_margin'] > results[1]['stability_margin']


class TestEdgeCases:
    """测试边界情况"""
    
    def test_very_small_coefficients(self):
        """测试非常小的系数"""
        result = check_ar_stationarity([1e-10], verbose=False)
        assert result.is_stationary
    
    def test_very_large_coefficients(self):
        """测试非常大的系数"""
        result = check_ar_stationarity([100.0], verbose=False)
        assert not result.is_stationary
    
    def test_negative_coefficients(self):
        """测试负系数"""
        result = check_ar_stationarity([-0.5], verbose=False)
        assert result.is_stationary
        assert result.roots[0].magnitude == 2.0
    
    def test_complex_roots_case(self):
        """测试产生复根的情况"""
        # AR(2)模型可能产生复根
        result = check_ar_stationarity([0.1, 0.2], verbose=False)
        # 验证根的计算是否正确
        assert len(result.roots) == 2
        for root in result.roots:
            assert isinstance(root.value, complex)
    
    def test_precision_near_unit_circle(self):
        """测试接近单位圆的精度"""
        # 测试根非常接近单位圆的情况
        result = check_ar_stationarity([0.999], verbose=False)
        assert result.is_stationary
        assert result.roots[0].magnitude > 1.0
