"""
核心功能测试
"""

import pytest
import numpy as np
from tsdiag.core import (
    stationarity_check,
    invertibility_check,
    StationarityResult,
    InvertibilityResult,
    RootInfo,
    _validate_coefficients,
    _build_characteristic_polynomial,
    _compute_polynomial_roots
)


class TestValidateCoefficients:
    """测试系数验证函数"""
    
    def test_valid_list(self):
        """测试有效的列表输入"""
        result = _validate_coefficients([0.5, -0.3, 0.1], "AR")
        assert result == [0.5, -0.3, 0.1]
    
    def test_valid_numpy_array(self):
        """测试有效的numpy数组输入"""
        result = _validate_coefficients(np.array([0.5, -0.3, 0.1]), "AR")
        assert result == [0.5, -0.3, 0.1]
    
    def test_empty_coefficients(self):
        """测试空系数"""
        with pytest.raises(ValueError, match="AR系数不能为空"):
            _validate_coefficients([], "AR")
    
    def test_invalid_type(self):
        """测试无效类型"""
        with pytest.raises(TypeError, match="AR系数必须是列表或numpy数组"):
            _validate_coefficients("invalid", "AR")
    
    def test_non_numeric_values(self):
        """测试非数值"""
        with pytest.raises(ValueError, match="AR系数必须都是数值"):
            _validate_coefficients([0.5, "invalid", 0.1], "AR")
    
    def test_string_numbers(self):
        """测试字符串数字"""
        result = _validate_coefficients(["0.5", "-0.3", "0.1"], "AR")
        assert result == [0.5, -0.3, 0.1]


class TestBuildCharacteristicPolynomial:
    """测试特征多项式构建"""
    
    def test_single_coefficient(self):
        """测试单个系数"""
        result = _build_characteristic_polynomial([0.5])
        assert result == [1.0, 0.5]
    
    def test_multiple_coefficients(self):
        """测试多个系数"""
        result = _build_characteristic_polynomial([0.5, -0.3, 0.1])
        assert result == [1.0, 0.5, -0.3, 0.1]
    
    def test_empty_coefficients(self):
        """测试空系数"""
        result = _build_characteristic_polynomial([])
        assert result == [1.0]


class TestComputePolynomialRoots:
    """测试多项式根计算"""
    
    def test_linear_polynomial(self):
        """测试一次多项式"""
        # 1 + 0.5z = 0 => z = -2
        roots = _compute_polynomial_roots([1.0, 0.5])
        assert len(roots) == 1
        assert abs(roots[0].value + 2.0) < 1e-10
        assert abs(roots[0].magnitude - 2.0) < 1e-10
        assert roots[0].is_outside_unit_circle
    
    def test_quadratic_polynomial(self):
        """测试二次多项式"""
        # 1 - 0.5z + 0.06z^2 = 0
        roots = _compute_polynomial_roots([1.0, -0.5, 0.06])
        assert len(roots) == 2
        # 验证所有根都在单位圆外
        for root in roots:
            assert root.magnitude > 1.0
            assert root.is_outside_unit_circle
    
    def test_constant_polynomial(self):
        """测试常数多项式"""
        roots = _compute_polynomial_roots([1.0])
        assert len(roots) == 0


class TestStationarityCheck:
    """测试AR模型平稳性检验"""
    
    def test_stationary_ar1(self):
        """测试平稳的AR(1)模型"""
        result = stationarity_check([0.5])
        assert isinstance(result, StationarityResult)
        assert result.is_stationary
        assert result.ar_coefficients == [0.5]
        assert len(result.roots) == 1
        assert result.roots[0].magnitude == 2.0
        assert result.roots[0].is_outside_unit_circle
        assert "平稳" in result.message
    
    def test_non_stationary_ar1(self):
        """测试非平稳的AR(1)模型"""
        result = stationarity_check([1.1])
        assert isinstance(result, StationarityResult)
        assert not result.is_stationary
        assert result.ar_coefficients == [1.1]
        assert len(result.roots) == 1
        assert result.roots[0].magnitude < 1.0
        assert not result.roots[0].is_outside_unit_circle
        assert "不满足平稳性条件" in result.message
    
    def test_unit_root_ar1(self):
        """测试单位根AR(1)模型"""
        result = stationarity_check([1.0])
        assert not result.is_stationary
        assert len(result.roots) == 1
        assert abs(result.roots[0].magnitude - 1.0) < 1e-10
    
    def test_stationary_ar2(self):
        """测试平稳的AR(2)模型"""
        # AR(2): X_t = 0.5*X_{t-1} - 0.06*X_{t-2} + e_t
        # 特征方程: 1 - 0.5z + 0.06z^2 = 0
        result = stationarity_check([0.5, -0.06])
        assert result.is_stationary
        assert len(result.roots) == 2
        for root in result.roots:
            assert root.is_outside_unit_circle
    
    def test_non_stationary_ar2(self):
        """测试非平稳的AR(2)模型"""
        result = stationarity_check([1.2, -0.1])
        assert not result.is_stationary
    
    def test_invalid_input(self):
        """测试无效输入"""
        with pytest.raises(ValueError):
            stationarity_check([])
        
        with pytest.raises(TypeError):
            stationarity_check("invalid")


class TestInvertibilityCheck:
    """测试MA模型可逆性检验"""
    
    def test_invertible_ma1(self):
        """测试可逆的MA(1)模型"""
        result = invertibility_check([0.5])
        assert isinstance(result, InvertibilityResult)
        assert result.is_invertible
        assert result.ma_coefficients == [0.5]
        assert len(result.roots) == 1
        assert result.roots[0].magnitude == 2.0
        assert result.roots[0].is_outside_unit_circle
        assert "可逆" in result.message
    
    def test_non_invertible_ma1(self):
        """测试不可逆的MA(1)模型"""
        result = invertibility_check([1.1])
        assert isinstance(result, InvertibilityResult)
        assert not result.is_invertible
        assert result.ma_coefficients == [1.1]
        assert len(result.roots) == 1
        assert result.roots[0].magnitude < 1.0
        assert not result.roots[0].is_outside_unit_circle
        assert "不满足可逆性条件" in result.message
    
    def test_unit_root_ma1(self):
        """测试单位根MA(1)模型"""
        result = invertibility_check([1.0])
        assert not result.is_invertible
        assert len(result.roots) == 1
        assert abs(result.roots[0].magnitude - 1.0) < 1e-10
    
    def test_invertible_ma2(self):
        """测试可逆的MA(2)模型"""
        # MA(2): X_t = e_t + 0.5*e_{t-1} + 0.06*e_{t-2}
        # 特征方程: 1 + 0.5z + 0.06z^2 = 0
        result = invertibility_check([0.5, 0.06])
        assert result.is_invertible
        assert len(result.roots) == 2
        for root in result.roots:
            assert root.is_outside_unit_circle
    
    def test_non_invertible_ma2(self):
        """测试不可逆的MA(2)模型"""
        result = invertibility_check([1.2, 0.1])
        assert not result.is_invertible
    
    def test_invalid_input(self):
        """测试无效输入"""
        with pytest.raises(ValueError):
            invertibility_check([])
        
        with pytest.raises(TypeError):
            invertibility_check("invalid")


class TestRootInfo:
    """测试根信息类"""
    
    def test_real_root(self):
        """测试实根"""
        root = RootInfo(value=2.0, magnitude=2.0, is_outside_unit_circle=True)
        assert "2.000000" in str(root)
        assert "|z|=2.000000" in str(root)
    
    def test_complex_root(self):
        """测试复根"""
        root = RootInfo(value=1+1j, magnitude=np.sqrt(2), is_outside_unit_circle=True)
        root_str = str(root)
        assert "1.000000" in root_str
        assert "+1.000000i" in root_str
        assert f"|z|={np.sqrt(2):.6f}" in root_str
    
    def test_negative_imaginary(self):
        """测试负虚部"""
        root = RootInfo(value=1-1j, magnitude=np.sqrt(2), is_outside_unit_circle=True)
        root_str = str(root)
        assert "1.000000" in root_str
        assert "-1.000000i" in root_str


class TestResultClasses:
    """测试结果类"""
    
    def test_stationarity_result_str(self):
        """测试平稳性结果字符串表示"""
        roots = [RootInfo(value=2.0, magnitude=2.0, is_outside_unit_circle=True)]
        result = StationarityResult(
            is_stationary=True,
            roots=roots,
            ar_coefficients=[0.5],
            characteristic_polynomial=[1.0, -0.5],
            message="测试消息"
        )
        result_str = str(result)
        assert "平稳性检验结果: 平稳" in result_str
        assert "测试消息" in result_str
        assert "[0.5]" in result_str
        assert "✓" in result_str
    
    def test_invertibility_result_str(self):
        """测试可逆性结果字符串表示"""
        roots = [RootInfo(value=2.0, magnitude=2.0, is_outside_unit_circle=True)]
        result = InvertibilityResult(
            is_invertible=True,
            roots=roots,
            ma_coefficients=[0.5],
            characteristic_polynomial=[1.0, 0.5],
            message="测试消息"
        )
        result_str = str(result)
        assert "可逆性检验结果: 可逆" in result_str
        assert "测试消息" in result_str
        assert "[0.5]" in result_str
        assert "✓" in result_str
