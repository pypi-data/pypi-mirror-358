"""
时间序列模型分析与诊断工具的命令行接口

提供用户友好的命令行交互方式。
"""

import click
import sys
from typing import List
from .stationarity import check_ar_stationarity, analyze_ar_stability_margin, suggest_ar_modifications
from .invertibility import check_ma_invertibility, analyze_ma_invertibility_margin, suggest_ma_modifications


@click.group()
@click.version_option(version="0.1.0")
def main():
    """
    时间序列模型分析与诊断工具
    
    提供AR模型平稳性检验和MA模型可逆性检验功能。
    """
    pass


@main.command()
@click.option(
    '--coefficients', '-c',
    required=True,
    help='AR模型系数，用逗号或空格分隔，例如: "0.5,-0.3,0.1" 或 "0.5 -0.3 0.1"'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    default=True,
    help='显示详细输出'
)
@click.option(
    '--analysis', '-a',
    is_flag=True,
    help='显示稳定性边际分析'
)
@click.option(
    '--suggest', '-s',
    is_flag=True,
    help='为非平稳模型提供修改建议'
)
def stationarity(coefficients: str, verbose: bool, analysis: bool, suggest: bool):
    """
    AR模型平稳性检验
    
    检验AR(p)模型的平稳性条件。
    
    示例:
        tsdiag stationarity -c "0.5,-0.3"
        tsdiag stationarity -c "0.8,0.15" --analysis --suggest
    """
    try:
        # 执行平稳性检验
        result = check_ar_stationarity(coefficients, verbose=verbose)
        
        # 显示稳定性分析
        if analysis:
            click.echo("\n" + "=" * 50)
            click.echo("稳定性边际分析")
            click.echo("=" * 50)
            
            stability_analysis = analyze_ar_stability_margin(result.ar_coefficients)
            
            click.echo(f"稳定性边际: {stability_analysis['stability_margin']:.6f}")
            click.echo(f"风险等级: {stability_analysis['risk_level']}")
            
            if stability_analysis['closest_root']:
                click.echo(f"最接近单位圆的根: {stability_analysis['closest_root']}")
        
        # 显示修改建议
        if suggest:
            click.echo("\n" + "=" * 50)
            click.echo("修改建议")
            click.echo("=" * 50)
            
            suggestions = suggest_ar_modifications(result.ar_coefficients)
            
            for suggestion in suggestions['suggestions']:
                click.echo(f"• {suggestion}")
            
            if 'suggested_coefficients' in suggestions:
                click.echo(f"建议系数: {suggestions['suggested_coefficients']}")
        
        # 设置退出码
        sys.exit(0 if result.is_stationary else 1)
        
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(2)


@main.command()
@click.option(
    '--coefficients', '-c',
    required=True,
    help='MA模型系数，用逗号或空格分隔，例如: "0.5,-0.3,0.1" 或 "0.5 -0.3 0.1"'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    default=True,
    help='显示详细输出'
)
@click.option(
    '--analysis', '-a',
    is_flag=True,
    help='显示可逆性边际分析'
)
@click.option(
    '--suggest', '-s',
    is_flag=True,
    help='为不可逆模型提供修改建议'
)
def invertibility(coefficients: str, verbose: bool, analysis: bool, suggest: bool):
    """
    MA模型可逆性检验
    
    检验MA(q)模型的可逆性条件。
    
    示例:
        tsdiag invertibility -c "0.5,-0.3"
        tsdiag invertibility -c "0.8,0.15" --analysis --suggest
    """
    try:
        # 执行可逆性检验
        result = check_ma_invertibility(coefficients, verbose=verbose)
        
        # 显示可逆性分析
        if analysis:
            click.echo("\n" + "=" * 50)
            click.echo("可逆性边际分析")
            click.echo("=" * 50)
            
            invertibility_analysis = analyze_ma_invertibility_margin(result.ma_coefficients)
            
            click.echo(f"可逆性边际: {invertibility_analysis['invertibility_margin']:.6f}")
            click.echo(f"风险等级: {invertibility_analysis['risk_level']}")
            
            if invertibility_analysis['closest_root']:
                click.echo(f"最接近单位圆的根: {invertibility_analysis['closest_root']}")
        
        # 显示修改建议
        if suggest:
            click.echo("\n" + "=" * 50)
            click.echo("修改建议")
            click.echo("=" * 50)
            
            suggestions = suggest_ma_modifications(result.ma_coefficients)
            
            for suggestion in suggestions['suggestions']:
                click.echo(f"• {suggestion}")
            
            if 'suggested_coefficients' in suggestions:
                click.echo(f"建议系数: {suggestions['suggested_coefficients']}")
        
        # 设置退出码
        sys.exit(0 if result.is_invertible else 1)
        
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(2)


@main.command()
@click.option(
    '--ar-coefficients', '--ar', '-a',
    help='AR模型系数，用逗号或空格分隔'
)
@click.option(
    '--ma-coefficients', '--ma', '-m',
    help='MA模型系数，用逗号或空格分隔'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    default=True,
    help='显示详细输出'
)
def check(ar_coefficients: str, ma_coefficients: str, verbose: bool):
    """
    同时检验AR和MA模型
    
    可以同时检验ARMA模型的平稳性和可逆性。
    
    示例:
        tsdiag check --ar "0.5,-0.3" --ma "0.4,0.2"
        tsdiag check -a "0.8" -m "0.6"
    """
    if not ar_coefficients and not ma_coefficients:
        click.echo("错误: 必须提供AR系数或MA系数（或两者都提供）", err=True)
        sys.exit(2)
    
    all_passed = True
    
    try:
        # 检验AR部分
        if ar_coefficients:
            click.echo("检验AR模型平稳性...")
            ar_result = check_ar_stationarity(ar_coefficients, verbose=verbose)
            if not ar_result.is_stationary:
                all_passed = False
        
        # 检验MA部分
        if ma_coefficients:
            if ar_coefficients:
                click.echo("\n" + "=" * 60 + "\n")
            click.echo("检验MA模型可逆性...")
            ma_result = check_ma_invertibility(ma_coefficients, verbose=verbose)
            if not ma_result.is_invertible:
                all_passed = False
        
        # 总结
        if ar_coefficients and ma_coefficients:
            click.echo("\n" + "=" * 60)
            click.echo("ARMA模型检验总结")
            click.echo("=" * 60)
            
            ar_status = "✓ 平稳" if ar_result.is_stationary else "✗ 非平稳"
            ma_status = "✓ 可逆" if ma_result.is_invertible else "✗ 不可逆"
            
            click.echo(f"AR部分: {ar_status}")
            click.echo(f"MA部分: {ma_status}")
            
            if all_passed:
                click.echo("✓ ARMA模型满足所有条件")
            else:
                click.echo("✗ ARMA模型存在问题，需要调整")
        
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(2)


@main.command()
def examples():
    """
    显示使用示例
    """
    examples_text = """
时间序列模型分析与诊断工具 - 使用示例

1. AR模型平稳性检验:
   tsdiag stationarity -c "0.5,-0.3"
   tsdiag stationarity -c "0.8,0.15" --analysis --suggest

2. MA模型可逆性检验:
   tsdiag invertibility -c "0.5,-0.3"
   tsdiag invertibility -c "0.8,0.15" --analysis --suggest

3. ARMA模型综合检验:
   tsdiag check --ar "0.5,-0.3" --ma "0.4,0.2"
   tsdiag check -a "0.8" -m "0.6"

4. 系数输入格式:
   - 逗号分隔: "0.5,-0.3,0.1"
   - 空格分隔: "0.5 -0.3 0.1"
   - 混合格式: "0.5, -0.3 0.1"

5. 常见AR(1)模型示例:
   - 平稳: tsdiag stationarity -c "0.5"
   - 非平稳: tsdiag stationarity -c "1.1"
   - 单位根: tsdiag stationarity -c "1.0"

6. 常见MA(1)模型示例:
   - 可逆: tsdiag invertibility -c "0.5"
   - 不可逆: tsdiag invertibility -c "1.1"

7. 获取帮助:
   tsdiag --help
   tsdiag stationarity --help
   tsdiag invertibility --help
   tsdiag check --help
"""
    click.echo(examples_text)


if __name__ == '__main__':
    main()
