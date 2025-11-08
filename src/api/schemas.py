"""
API 数据模型 (Pydantic Schemas)

定义API的请求和响应模型
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


# ============================================
# 用户提交相关
# ============================================

class InvestigationSubmission(BaseModel):
    """用户提交调查请求"""
    submission: str = Field(..., description="新闻链接或事件描述")
    submission_type: str = Field(
        default="url",
        description="提交类型: url 或 text"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "submission": "https://example.com/news/breaking-story",
                "submission_type": "url"
            }
        }


class InvestigationResponse(BaseModel):
    """调查响应"""
    investigation_id: str = Field(..., description="调查ID")
    status: str = Field(..., description="调查状态")
    message: str = Field(default="Investigation started", description="消息")

    class Config:
        json_schema_extra = {
            "example": {
                "investigation_id": "E-12345678",
                "status": "pending",
                "message": "Investigation started successfully"
            }
        }


# ============================================
# 调查报告相关
# ============================================

class SourceInfo(BaseModel):
    """信源信息"""
    source_name: str
    source_type: str
    first_appearance: str
    confidence: float


class VerificationDetail(BaseModel):
    """核查详情"""
    claim: str
    status: str
    evidence: List[Dict[str, Any]] = []


class VerificationSummary(BaseModel):
    """核查摘要"""
    claims_verified: int
    overall_status: str
    details: List[VerificationDetail]


class NarrativeEvolution(BaseModel):
    """叙事演变"""
    versions_analyzed: int
    evolution_detected: List[Dict[str, Any]]
    suspicious_accounts: List[Dict[str, Any]]


class InvestigationReport(BaseModel):
    """完整调查报告"""
    investigation_id: str
    timestamp: str
    user_submission: str

    # 溯源结果
    source_tracing: SourceInfo

    # 核查结果
    verification: VerificationSummary

    # 叙事分析
    narrative_evolution: NarrativeEvolution

    # 总结和建议
    summary: str
    recommendation: str


class InvestigationResult(BaseModel):
    """调查结果（完整）"""
    investigation_id: str
    status: str
    report: InvestigationReport
    credibility_score: float
    agent_results: List[Dict[str, Any]] = []

    class Config:
        json_schema_extra = {
            "example": {
                "investigation_id": "E-12345678",
                "status": "completed",
                "credibility_score": 35.5,
                "report": {
                    "investigation_id": "E-12345678",
                    "timestamp": "2024-01-01T12:00:00",
                    "summary": "信息最早来自 @UnknownSource。发现 2 项声明存在证伪证据。"
                }
            }
        }


# ============================================
# TaaS API 相关
# ============================================

class TaaSSourceCheckRequest(BaseModel):
    """信源检查请求"""
    source_name: str = Field(..., description="信源名称")

    class Config:
        json_schema_extra = {
            "example": {
                "source_name": "@TechInsider"
            }
        }


class TaaSSourceCheckResponse(BaseModel):
    """信源检查响应"""
    source_name: str
    exists: bool
    credit_score: Optional[int] = None
    reputation: Optional[str] = None
    statistics: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "source_name": "@TechInsider",
                "exists": True,
                "credit_score": 25,
                "reputation": "low",
                "statistics": {
                    "total_claims": 10,
                    "verified_claims": 2,
                    "refuted_claims": 6,
                    "accuracy_rate": 20.0
                }
            }
        }


class TaaSRiskScoreRequest(BaseModel):
    """风险评分请求"""
    text: str = Field(..., description="待评估文本")
    source: Optional[str] = Field(None, description="信源（如果已知）")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "OpenAI投资AMD 1000亿美元",
                "source": "@TechInsider"
            }
        }


class TaaSRiskScoreResponse(BaseModel):
    """风险评分响应"""
    risk_score: float = Field(..., description="风险评分 (0-100, 越高越可疑)")
    risk_level: str = Field(..., description="风险等级: low/medium/high")
    factors: List[str] = Field(default=[], description="风险因素")
    recommendation: str = Field(..., description="建议")

    class Config:
        json_schema_extra = {
            "example": {
                "risk_score": 75.5,
                "risk_level": "high",
                "factors": [
                    "信源历史准确率仅18%",
                    "未找到官方证据",
                    "类似传言曾被证伪"
                ],
                "recommendation": "高度存疑，建议等待官方确认"
            }
        }


class TaaSFactCheckRequest(BaseModel):
    """事实核查请求"""
    claim: str = Field(..., description="待核查的声明")
    entities: Optional[List[str]] = Field(None, description="涉及的实体")

    class Config:
        json_schema_extra = {
            "example": {
                "claim": "OpenAI将于Q2收购AMD",
                "entities": ["OpenAI", "AMD"]
            }
        }


class TaaSFactCheckResponse(BaseModel):
    """事实核查响应"""
    claim: str
    status: str = Field(..., description="核查状态: verified/refuted/unverifiable")
    confidence: float = Field(..., description="置信度 (0-1)")
    evidence: List[Dict[str, str]] = Field(default=[], description="证据列表")
    summary: str

    class Config:
        json_schema_extra = {
            "example": {
                "claim": "OpenAI将于Q2收购AMD",
                "status": "refuted",
                "confidence": 0.9,
                "evidence": [
                    {
                        "source": "SEC EDGAR",
                        "finding": "未找到相关披露文件",
                        "url": "https://www.sec.gov/..."
                    }
                ],
                "summary": "在SEC官方数据库中未找到该交易的披露文件"
            }
        }


# ============================================
# 通用响应
# ============================================

class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    detail: Optional[str] = None
    investigation_id: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    timestamp: str
