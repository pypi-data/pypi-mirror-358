"""
可逆性检验模块测试
"""

import pytest
import numpy as np
from tsdiag.invertibility import (
    check_ma_invertibility,
    analyze_ma_invertibility_margin,
    suggest_ma_modifications,
    batch_invertibility_check,
    compare_ma_models
)


class TestCheckMaInvertibility:
    """测试MA可逆性检验高级接口"""
    
    def test_list_input(self):
        """测试列表输入"""
        result = check_ma_invertibility([0.5, -0.3], verbose=False)
        assert result.is_invertible
        assert result.ma_coefficients == [0.5, -0.3]
    
    def test_numpy_input(self):
        """测试numpy数组输入"""
        result = check_ma_invertibility(np.array([0.5, -0.3]), verbose=False)
        assert result.is_invertible
        assert result.ma_coefficients == [0.5, -0.3]
    
    def test_string_input_comma_separated(self):
        """测试逗号分隔的字符串输入"""
        result = check_ma_invertibility("0.5,-0.3", verbose=False)
        assert result.is_invertible
        assert result.ma_coefficients == [0.5, -0.3]
    
    def test_string_input_space_separated(self):
        """测试空格分隔的字符串输入"""
        result = check_ma_invertibility("0.5 -0.3", verbose=False)
        assert result.is_invertible
        assert result.ma_coefficients == [0.5, -0.3]
    
    def test_string_input_mixed_separators(self):
        """测试混合分隔符的字符串输入"""
        result = check_ma_invertibility("0.5, -0.3 0.1", verbose=False)
        assert result.ma_coefficients == [0.5, -0.3, 0.1]
    
    def test_invalid_string_input(self):
        """测试无效字符串输入"""
        with pytest.raises(ValueError, match="无法解析MA系数字符串"):
            check_ma_invertibility("0.5,invalid,-0.3", verbose=False)
    
    def test_verbose_output(self, capsys):
        """测试详细输出"""
        check_ma_invertibility([0.5], verbose=True)
        captured = capsys.readouterr()
        assert "MA模型可逆性检验" in captured.out
        assert "=" in captured.out


class TestAnalyzeMaInvertibilityMargin:
    """测试MA可逆性边际分析"""
    
    def test_invertible_model(self):
        """测试可逆模型"""
        analysis = analyze_ma_invertibility_margin([0.5])
        assert analysis['min_distance_to_unit_circle'] == 1.0  # |z| = 2, distance = 2-1 = 1
        assert analysis['invertibility_margin'] == 1.0
        assert analysis['risk_level'] == 'low'
        assert analysis['closest_root'] is not None
    
    def test_non_invertible_model(self):
        """测试不可逆模型"""
        analysis = analyze_ma_invertibility_margin([1.1])
        assert analysis['min_distance_to_unit_circle'] < 0
        assert analysis['invertibility_margin'] < 0
        assert analysis['risk_level'] == 'high'
    
    def test_marginal_model(self):
        """测试边际可逆模型"""
        analysis = analyze_ma_invertibility_margin([0.95])  # |z| ≈ 1.05, distance ≈ 0.05
        assert 0 < analysis['min_distance_to_unit_circle'] < 0.1
        assert analysis['risk_level'] == 'medium'
    
    def test_all_distances(self):
        """测试所有距离计算"""
        analysis = analyze_ma_invertibility_margin([0.5, 0.3])
        assert 'all_distances' in analysis
        assert len(analysis['all_distances']) == 2
        assert all(d > 0 for d in analysis['all_distances'])  # 所有距离都应该为正


class TestSuggestMaModifications:
    """测试MA模型修改建议"""
    
    def test_invertible_model_no_suggestions(self):
        """测试可逆模型无需修改"""
        suggestions = suggest_ma_modifications([0.5])
        assert not suggestions['is_modification_needed']
        assert "无需修改" in suggestions['suggestions'][0]
    
    def test_non_invertible_ma1_suggestions(self):
        """测试不可逆MA(1)模型建议"""
        suggestions = suggest_ma_modifications([1.1])
        assert suggestions['is_modification_needed']
        assert 'suggested_coefficients' in suggestions
        assert abs(suggestions['suggested_coefficients'][0]) < 1.0
    
    def test_non_invertible_ma2_suggestions(self):
        """测试不可逆MA(2)模型建议"""
        suggestions = suggest_ma_modifications([1.2, 0.1])
        assert suggestions['is_modification_needed']
        assert 'suggested_coefficients' in suggestions
        assert len(suggestions['suggested_coefficients']) == 2
        # 建议的系数应该是原系数的缩放版本
        original = [1.2, 0.1]
        suggested = suggestions['suggested_coefficients']
        scale_factor = suggested[0] / original[0]
        assert abs(scale_factor - 0.9) < 1e-10
    
    def test_unit_root_suggestions(self):
        """测试单位根模型建议"""
        suggestions = suggest_ma_modifications([1.0])
        assert suggestions['is_modification_needed']
        assert 'suggested_coefficients' in suggestions


class TestBatchInvertibilityCheck:
    """测试批量可逆性检验"""
    
    def test_multiple_models(self):
        """测试多个模型"""
        models = [
            [0.5],      # 可逆
            [1.1],      # 不可逆
            [0.5, 0.3]  # 可逆
        ]
        results = batch_invertibility_check(models)
        
        assert len(results) == 3
        assert results[0]['is_invertible'] == True
        assert results[1]['is_invertible'] == False
        assert results[2]['is_invertible'] == True
        
        # 检查模型名称
        assert results[0]['model_name'] == 'Model_1'
        assert results[1]['model_name'] == 'Model_2'
        assert results[2]['model_name'] == 'Model_3'
    
    def test_custom_model_names(self):
        """测试自定义模型名称"""
        models = [[0.5], [1.1]]
        names = ['Invertible_Model', 'Non_Invertible_Model']
        results = batch_invertibility_check(models, names)
        
        assert results[0]['model_name'] == 'Invertible_Model'
        assert results[1]['model_name'] == 'Non_Invertible_Model'
    
    def test_mismatched_names_length(self):
        """测试名称数量不匹配"""
        models = [[0.5], [1.1]]
        names = ['Only_One_Name']
        
        with pytest.raises(ValueError, match="模型名称数量必须与模型数量相同"):
            batch_invertibility_check(models, names)
    
    def test_invalid_model_in_batch(self):
        """测试批量中包含无效模型"""
        models = [
            [0.5],      # 有效
            [],         # 无效：空列表
            [0.5, 0.3]  # 有效
        ]
        results = batch_invertibility_check(models)
        
        assert len(results) == 3
        assert results[0]['is_invertible'] == True
        assert 'error' in results[1]  # 第二个模型应该有错误
        assert results[2]['is_invertible'] == True
    
    def test_invertibility_analysis_in_batch(self):
        """测试批量结果中的可逆性分析"""
        models = [[0.5], [0.95]]  # 一个低风险，一个中等风险
        results = batch_invertibility_check(models)
        
        assert results[0]['risk_level'] == 'low'
        assert results[1]['risk_level'] == 'medium'
        assert results[0]['invertibility_margin'] > results[1]['invertibility_margin']


class TestCompareMaModels:
    """测试MA模型比较"""
    
    def test_compare_multiple_models(self):
        """测试比较多个模型"""
        models = [
            [0.5],      # 可逆
            [1.1],      # 不可逆
            [0.3],      # 可逆
            [1.5]       # 不可逆
        ]
        comparison = compare_ma_models(models)
        
        assert comparison['total_models'] == 4
        assert comparison['invertible_models'] == 2
        assert comparison['non_invertible_models'] == 2
        assert comparison['invertibility_rate'] == 0.5
        
        # 最佳模型应该是可逆性边际最大的
        assert comparison['best_model']['is_invertible'] == True
        assert comparison['worst_model']['is_invertible'] == False
    
    def test_compare_with_custom_names(self):
        """测试使用自定义名称比较"""
        models = [[0.5], [1.1]]
        names = ['Good_Model', 'Bad_Model']
        comparison = compare_ma_models(models, names)
        
        assert comparison['best_model']['model_name'] == 'Good_Model'
        assert comparison['worst_model']['model_name'] == 'Bad_Model'
    
    def test_compare_all_invertible(self):
        """测试所有模型都可逆的情况"""
        models = [[0.5], [0.3], [0.7]]
        comparison = compare_ma_models(models)
        
        assert comparison['invertibility_rate'] == 1.0
        assert comparison['non_invertible_models'] == 0
        assert comparison['best_model']['is_invertible'] == True
        assert comparison['worst_model']['is_invertible'] == True
    
    def test_compare_all_non_invertible(self):
        """测试所有模型都不可逆的情况"""
        models = [[1.1], [1.5], [2.0]]
        comparison = compare_ma_models(models)
        
        assert comparison['invertibility_rate'] == 0.0
        assert comparison['invertible_models'] == 0
        assert comparison['best_model']['is_invertible'] == False
        assert comparison['worst_model']['is_invertible'] == False
    
    def test_compare_empty_list(self):
        """测试空模型列表"""
        comparison = compare_ma_models([])
        
        assert comparison['total_models'] == 0
        assert comparison['invertibility_rate'] == 0
        assert comparison['best_model'] is None
        assert comparison['worst_model'] is None


class TestEdgeCases:
    """测试边界情况"""
    
    def test_very_small_coefficients(self):
        """测试非常小的系数"""
        result = check_ma_invertibility([1e-10], verbose=False)
        assert result.is_invertible
    
    def test_very_large_coefficients(self):
        """测试非常大的系数"""
        result = check_ma_invertibility([100.0], verbose=False)
        assert not result.is_invertible
    
    def test_negative_coefficients(self):
        """测试负系数"""
        result = check_ma_invertibility([-0.5], verbose=False)
        assert result.is_invertible
        assert result.roots[0].magnitude == 2.0
    
    def test_complex_roots_case(self):
        """测试产生复根的情况"""
        # MA(2)模型可能产生复根
        result = check_ma_invertibility([0.1, 0.2], verbose=False)
        # 验证根的计算是否正确
        assert len(result.roots) == 2
        for root in result.roots:
            assert isinstance(root.value, complex)
    
    def test_precision_near_unit_circle(self):
        """测试接近单位圆的精度"""
        # 测试根非常接近单位圆的情况
        result = check_ma_invertibility([0.999], verbose=False)
        assert result.is_invertible
        assert result.roots[0].magnitude > 1.0
    
    def test_zero_coefficient(self):
        """测试零系数"""
        result = check_ma_invertibility([0.0], verbose=False)
        assert result.is_invertible
        # 零系数对应的根在无穷远处，应该满足可逆性条件
