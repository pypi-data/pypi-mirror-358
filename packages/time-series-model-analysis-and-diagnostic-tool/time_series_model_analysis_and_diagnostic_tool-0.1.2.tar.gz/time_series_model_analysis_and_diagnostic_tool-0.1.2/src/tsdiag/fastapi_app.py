"""
时间序列模型分析与诊断工具的FastAPI Web服务

提供REST API接口来进行时间序列模型分析。
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
import numpy as np
from datetime import datetime

from .api import (
    TSModelDiagnostic,
    quick_ar_check,
    quick_ma_check,
    quick_arma_check,
    analyze_model_stability,
    batch_model_analysis
)


# Pydantic 数据模型
class ARModelRequest(BaseModel):
    """AR模型检验请求"""
    coefficients: List[float] = Field(..., description="AR系数列表", min_items=1)
    verbose: bool = Field(False, description="是否返回详细信息")
    
    @validator('coefficients')
    def validate_coefficients(cls, v):
        if not v:
            raise ValueError("系数列表不能为空")
        if any(not isinstance(x, (int, float)) for x in v):
            raise ValueError("所有系数必须是数值类型")
        return v


class MAModelRequest(BaseModel):
    """MA模型检验请求"""
    coefficients: List[float] = Field(..., description="MA系数列表", min_items=1)
    verbose: bool = Field(False, description="是否返回详细信息")
    
    @validator('coefficients')
    def validate_coefficients(cls, v):
        if not v:
            raise ValueError("系数列表不能为空")
        if any(not isinstance(x, (int, float)) for x in v):
            raise ValueError("所有系数必须是数值类型")
        return v


class ARMAModelRequest(BaseModel):
    """ARMA模型检验请求"""
    ar_coefficients: List[float] = Field(..., description="AR系数列表", min_items=1)
    ma_coefficients: List[float] = Field(..., description="MA系数列表", min_items=1)
    verbose: bool = Field(False, description="是否返回详细信息")
    
    @validator('ar_coefficients', 'ma_coefficients')
    def validate_coefficients(cls, v):
        if not v:
            raise ValueError("系数列表不能为空")
        if any(not isinstance(x, (int, float)) for x in v):
            raise ValueError("所有系数必须是数值类型")
        return v


class ModelForBatch(BaseModel):
    """批量分析中的单个模型"""
    ar: Optional[List[float]] = Field(None, description="AR系数（可选）")
    ma: Optional[List[float]] = Field(None, description="MA系数（可选）")
    
    @validator('ar', 'ma')
    def validate_coefficients(cls, v):
        if v is not None:
            if not v:
                raise ValueError("如果提供系数列表，不能为空")
            if any(not isinstance(x, (int, float)) for x in v):
                raise ValueError("所有系数必须是数值类型")
        return v


class BatchAnalysisRequest(BaseModel):
    """批量模型分析请求"""
    models: List[ModelForBatch] = Field(..., description="模型列表", min_items=1)
    model_names: Optional[List[str]] = Field(None, description="模型名称列表（可选）")
    
    @validator('model_names')
    def validate_model_names(cls, v, values):
        if v is not None and 'models' in values:
            if len(v) != len(values['models']):
                raise ValueError("模型名称数量必须与模型数量相同")
        return v


class RootInfoResponse(BaseModel):
    """根信息响应"""
    value: str
    magnitude: float
    outside_unit_circle: bool


class StationarityResponse(BaseModel):
    """平稳性检验响应"""
    is_stationary: bool
    ar_coefficients: List[float]
    roots: List[RootInfoResponse]
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class InvertibilityResponse(BaseModel):
    """可逆性检验响应"""
    is_invertible: bool
    ma_coefficients: List[float]
    roots: List[RootInfoResponse]
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ARMAResponse(BaseModel):
    """ARMA模型检验响应"""
    ar_result: StationarityResponse
    ma_result: InvertibilityResponse
    overall_valid: bool
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class QuickCheckResponse(BaseModel):
    """快速检验响应"""
    result: bool
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class QuickARMAResponse(BaseModel):
    """快速ARMA检验响应"""
    ar_stationary: bool
    ma_invertible: bool
    overall_valid: bool
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class StabilityAnalysisResponse(BaseModel):
    """稳定性分析响应"""
    analysis: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class BatchAnalysisResponse(BaseModel):
    """批量分析响应"""
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# 创建FastAPI应用
app = FastAPI(
    title="时间序列模型分析与诊断API",
    description="提供AR模型平稳性检验和MA模型可逆性检验的REST API服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def convert_root_info(root_info):
    """转换根信息为响应格式"""
    return RootInfoResponse(
        value=str(root_info.value),
        magnitude=root_info.magnitude,
        outside_unit_circle=root_info.is_outside_unit_circle
    )


@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径，返回API文档链接"""
    return """
    <html>
        <head>
            <title>时间序列模型分析与诊断API</title>
        </head>
        <body>
            <h1>时间序列模型分析与诊断API</h1>
            <p>欢迎使用时间序列模型分析与诊断工具的REST API服务！</p>
            <h2>文档链接：</h2>
            <ul>
                <li><a href="/docs">Swagger UI 文档</a></li>
                <li><a href="/redoc">ReDoc 文档</a></li>
            </ul>
            <h2>主要功能：</h2>
            <ul>
                <li>AR模型平稳性检验</li>
                <li>MA模型可逆性检验</li>
                <li>ARMA模型综合检验</li>
                <li>模型稳定性分析</li>
                <li>批量模型分析</li>
            </ul>
        </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/v1/ar/check", response_model=StationarityResponse)
async def check_ar_stationarity(request: ARModelRequest):
    """
    检验AR模型的平稳性
    
    - **coefficients**: AR系数列表
    - **verbose**: 是否返回详细信息
    """
    try:
        diagnostic = TSModelDiagnostic()
        result = diagnostic.check_ar_model(request.coefficients, verbose=request.verbose)
        
        return StationarityResponse(
            is_stationary=result.is_stationary,
            ar_coefficients=result.ar_coefficients,
            roots=[convert_root_info(root) for root in result.roots],
            message=result.message
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"检验失败: {str(e)}")


@app.post("/api/v1/ma/check", response_model=InvertibilityResponse)
async def check_ma_invertibility(request: MAModelRequest):
    """
    检验MA模型的可逆性
    
    - **coefficients**: MA系数列表
    - **verbose**: 是否返回详细信息
    """
    try:
        diagnostic = TSModelDiagnostic()
        result = diagnostic.check_ma_model(request.coefficients, verbose=request.verbose)
        
        return InvertibilityResponse(
            is_invertible=result.is_invertible,
            ma_coefficients=result.ma_coefficients,
            roots=[convert_root_info(root) for root in result.roots],
            message=result.message
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"检验失败: {str(e)}")


@app.post("/api/v1/arma/check", response_model=ARMAResponse)
async def check_arma_model(request: ARMAModelRequest):
    """
    检验ARMA模型的平稳性和可逆性
    
    - **ar_coefficients**: AR系数列表
    - **ma_coefficients**: MA系数列表
    - **verbose**: 是否返回详细信息
    """
    try:
        diagnostic = TSModelDiagnostic()
        ar_result, ma_result = diagnostic.check_arma_model(
            request.ar_coefficients, 
            request.ma_coefficients, 
            verbose=request.verbose
        )
        
        return ARMAResponse(
            ar_result=StationarityResponse(
                is_stationary=ar_result.is_stationary,
                ar_coefficients=ar_result.ar_coefficients,
                roots=[convert_root_info(root) for root in ar_result.roots],
                message=ar_result.message
            ),
            ma_result=InvertibilityResponse(
                is_invertible=ma_result.is_invertible,
                ma_coefficients=ma_result.ma_coefficients,
                roots=[convert_root_info(root) for root in ma_result.roots],
                message=ma_result.message
            ),
            overall_valid=ar_result.is_stationary and ma_result.is_invertible
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"检验失败: {str(e)}")


@app.post("/api/v1/ar/quick", response_model=QuickCheckResponse)
async def quick_ar_stationarity(request: ARModelRequest):
    """
    快速AR平稳性检验，只返回布尔结果
    
    - **coefficients**: AR系数列表
    """
    try:
        result = quick_ar_check(request.coefficients)
        return QuickCheckResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"检验失败: {str(e)}")


@app.post("/api/v1/ma/quick", response_model=QuickCheckResponse)
async def quick_ma_invertibility(request: MAModelRequest):
    """
    快速MA可逆性检验，只返回布尔结果
    
    - **coefficients**: MA系数列表
    """
    try:
        result = quick_ma_check(request.coefficients)
        return QuickCheckResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"检验失败: {str(e)}")


@app.post("/api/v1/arma/quick", response_model=QuickARMAResponse)
async def quick_arma_check_endpoint(request: ARMAModelRequest):
    """
    快速ARMA模型检验，只返回布尔结果
    
    - **ar_coefficients**: AR系数列表
    - **ma_coefficients**: MA系数列表
    """
    try:
        ar_stationary, ma_invertible = quick_arma_check(
            request.ar_coefficients, 
            request.ma_coefficients
        )
        return QuickARMAResponse(
            ar_stationary=ar_stationary,
            ma_invertible=ma_invertible,
            overall_valid=ar_stationary and ma_invertible
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"检验失败: {str(e)}")


@app.post("/api/v1/stability/analyze", response_model=StabilityAnalysisResponse)
async def analyze_stability(request: ARMAModelRequest):
    """
    全面分析模型稳定性
    
    - **ar_coefficients**: AR系数列表
    - **ma_coefficients**: MA系数列表
    """
    try:
        analysis = analyze_model_stability(
            ar_coefficients=request.ar_coefficients,
            ma_coefficients=request.ma_coefficients
        )
        return StabilityAnalysisResponse(analysis=analysis)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"分析失败: {str(e)}")


@app.post("/api/v1/batch/analyze", response_model=BatchAnalysisResponse)
async def batch_analyze(request: BatchAnalysisRequest):
    """
    批量模型分析
    
    - **models**: 模型列表，每个模型包含ar和/或ma系数
    - **model_names**: 模型名称列表（可选）
    """
    try:
        # 转换请求格式
        models = []
        for model in request.models:
            model_dict = {}
            if model.ar is not None:
                model_dict['ar'] = model.ar
            if model.ma is not None:
                model_dict['ma'] = model.ma
            models.append(model_dict)
        
        results = batch_model_analysis(models, request.model_names)
        
        # 计算摘要信息
        summary = {
            "total_models": len(results),
            "valid_models": 0,
            "error_models": 0,
            "ar_stationary_count": 0,
            "ma_invertible_count": 0
        }
        
        for result in results:
            if 'error' in result:
                summary["error_models"] += 1
            else:
                if 'overall' in result and result['overall'].get('model_valid', False):
                    summary["valid_models"] += 1
                if 'ar' in result and result['ar'].get('is_stationary', False):
                    summary["ar_stationary_count"] += 1
                if 'ma' in result and result['ma'].get('is_invertible', False):
                    summary["ma_invertible_count"] += 1
        
        return BatchAnalysisResponse(results=results, summary=summary)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"批量分析失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
