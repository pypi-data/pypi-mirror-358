[English](README_EN.md) | [中文](README.md)

# 时间序列模型分析与诊断工具

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

一个专业的时间序列模型分析与诊断工具，提供AR模型平稳性检验和MA模型可逆性检验功能。

## 🚀 功能特性

### 核心功能

- **AR模型平稳性检验**: 检验自回归模型的平稳性条件
- **MA模型可逆性检验**: 检验移动平均模型的可逆性条件
- **特征根分析**: 计算特征多项式的根并判断其位置
- **稳定性边际分析**: 量化分析模型的稳定性程度
- **修改建议**: 为不满足条件的模型提供调整建议

### 使用方式

- **Python库**: 可作为Python包导入使用
- **命令行工具**: 提供友好的命令行接口
- **批量处理**: 支持批量模型分析和比较

## 📦 安装

### 使用uv（推荐）

```bash
uv add time-series-model-analysis-and-diagnostic-tool
```

### 使用pip

```bash
pip install time-series-model-analysis-and-diagnostic-tool
```

### 从源码安装

```bash
git clone https://github.com/zym9863/time-series-model-analysis-and-diagnostic-tool.git
cd time-series-model-analysis-and-diagnostic-tool
uv sync
```

## 🔧 快速开始

### 命令行使用

#### AR模型平稳性检验

```bash
# 基本检验
tsdiag stationarity -c "0.5,-0.3"

# 带分析和建议
tsdiag stationarity -c "0.8,0.15" --analysis --suggest

# 检验非平稳模型
tsdiag stationarity -c "1.1" --suggest
```

#### MA模型可逆性检验

```bash
# 基本检验
tsdiag invertibility -c "0.5,-0.3"

# 带分析和建议
tsdiag invertibility -c "0.8,0.15" --analysis --suggest
```

#### ARMA模型综合检验

```bash
# 同时检验AR和MA部分
tsdiag check --ar "0.5,-0.3" --ma "0.4,0.2"
```

#### 查看使用示例

```bash
tsdiag examples
```

### Python库使用

#### 基本使用

```python
import tsdiag

# AR模型平稳性检验
ar_result = tsdiag.stationarity_check([0.5, -0.3])
print(f"模型是否平稳: {ar_result.is_stationary}")
print(f"特征根: {[root.magnitude for root in ar_result.roots]}")

# MA模型可逆性检验
ma_result = tsdiag.invertibility_check([0.5, -0.3])
print(f"模型是否可逆: {ma_result.is_invertible}")
```

#### 高级功能

```python
import tsdiag

# 使用高级API
diagnostic = tsdiag.TSModelDiagnostic()

# 检验ARMA模型
ar_result, ma_result = diagnostic.check_arma_model(
    ar_coefficients=[0.5, -0.3],
    ma_coefficients=[0.4, 0.2]
)

# 获取摘要
summary = diagnostic.get_summary()
print(summary)

# 快速检验（只返回布尔值）
is_stationary = tsdiag.quick_ar_check([0.5, -0.3])
is_invertible = tsdiag.quick_ma_check([0.4, 0.2])
```

#### 批量分析

```python
import tsdiag

# 批量AR模型分析
ar_models = [
    [0.5],
    [1.1],
    [0.5, -0.3]
]
results = tsdiag.batch_stationarity_check(ar_models)

for result in results:
    print(f"{result['model_name']}: {result['is_stationary']}")

# 模型比较
ma_models = [[0.5], [1.1], [0.3]]
comparison = tsdiag.compare_ma_models(ma_models)
print(f"可逆性比率: {comparison['invertibility_rate']}")
```

## 📊 理论背景

### AR模型平稳性

AR(p)模型: $X_t = \phi_1 X_{t-1} + \phi_2 X_{t-2} + \cdots + \phi_p X_{t-p} + \varepsilon_t$

**平稳性条件**: 特征方程 $1 - \phi_1 z - \phi_2 z^2 - \cdots - \phi_p z^p = 0$ 的所有根都在单位圆外。

### MA模型可逆性

MA(q)模型: $X_t = \varepsilon_t + \theta_1 \varepsilon_{t-1} + \theta_2 \varepsilon_{t-2} + \cdots + \theta_q \varepsilon_{t-q}$

**可逆性条件**: 特征方程 $1 + \theta_1 z + \theta_2 z^2 + \cdots + \theta_q z^q = 0$ 的所有根都在单位圆外。

## 📖 详细文档

### 输入格式

系数可以使用多种格式输入：

- **列表**: `[0.5, -0.3, 0.1]`
- **numpy数组**: `np.array([0.5, -0.3, 0.1])`
- **字符串**: `"0.5,-0.3,0.1"` 或 `"0.5 -0.3 0.1"`

### 输出结果

#### StationarityResult

```python
@dataclass
class StationarityResult:
    is_stationary: bool              # 是否平稳
    roots: List[RootInfo]           # 特征根信息
    ar_coefficients: List[float]    # AR系数
    characteristic_polynomial: List[float]  # 特征多项式系数
    message: str                    # 结果消息
```

#### InvertibilityResult

```python
@dataclass
class InvertibilityResult:
    is_invertible: bool             # 是否可逆
    roots: List[RootInfo]          # 特征根信息
    ma_coefficients: List[float]   # MA系数
    characteristic_polynomial: List[float]  # 特征多项式系数
    message: str                   # 结果消息
```

### 风险等级

- **low**: 所有根远离单位圆（距离 > 0.1）
- **medium**: 有根接近单位圆（0 < 距离 ≤ 0.1）
- **high**: 有根在单位圆内或单位圆上（距离 ≤ 0）

## 🧪 测试

运行测试套件：

```bash
# 运行所有测试
uv run pytest

# 运行测试并显示覆盖率
uv run pytest --cov=tsdiag

# 运行特定测试文件
uv run pytest tests/test_core.py -v
```

## 📝 示例

### 常见AR模型

```python
import tsdiag

# AR(1)模型示例
models = {
    "平稳": [0.5],
    "非平稳": [1.1],
    "单位根": [1.0],
    "边界情况": [0.99]
}

for name, coeffs in models.items():
    result = tsdiag.stationarity_check(coeffs)
    print(f"{name}: {result.is_stationary}")
```

### 常见MA模型

```python
import tsdiag

# MA(1)模型示例
models = {
    "可逆": [0.5],
    "不可逆": [1.1],
    "单位根": [1.0],
    "边界情况": [0.99]
}

for name, coeffs in models.items():
    result = tsdiag.invertibility_check(coeffs)
    print(f"{name}: {result.is_invertible}")
```

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢所有贡献者
- 基于经典时间序列分析理论
- 使用 NumPy 进行数值计算
- 使用 Click 构建命令行界面