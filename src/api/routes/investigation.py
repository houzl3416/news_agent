"""
调查相关 API 路由
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from ..schemas import (
    InvestigationSubmission,
    InvestigationResponse,
    InvestigationResult,
    ErrorResponse
)
from ...orchestrator import InvestigationOrchestrator

router = APIRouter(
    prefix="/api/v1/investigation",
    tags=["investigation"]
)

# TODO: 初始化Orchestrator（实际应用中从依赖注入获取）
orchestrator = InvestigationOrchestrator()


@router.post(
    "/submit",
    response_model=InvestigationResponse,
    summary="提交调查请求",
    description="用户提交新闻链接或事件描述，启动调查流程"
)
async def submit_investigation(
    submission: InvestigationSubmission,
    background_tasks: BackgroundTasks
) -> InvestigationResponse:
    """
    提交调查请求

    接受用户提交的链接或文本，立即返回调查ID，
    然后在后台异步执行调查流程。

    Args:
        submission: 调查提交数据
        background_tasks: FastAPI后台任务

    Returns:
        InvestigationResponse: 包含调查ID和状态
    """
    try:
        # TODO: 实现异步调查
        # 当前为同步演示
        result = await orchestrator.start_investigation(
            submission=submission.submission,
            submission_type=submission.submission_type
        )

        investigation_id = result.get("investigation_id")

        return InvestigationResponse(
            investigation_id=investigation_id,
            status="pending",
            message="Investigation started successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start investigation: {str(e)}"
        )


@router.get(
    "/{investigation_id}",
    response_model=InvestigationResult,
    summary="查询调查结果",
    description="根据调查ID查询调查进度和结果"
)
async def get_investigation_result(investigation_id: str) -> InvestigationResult:
    """
    查询调查结果

    Args:
        investigation_id: 调查ID

    Returns:
        InvestigationResult: 调查结果（包含报告）
    """
    try:
        # TODO: 从数据库或缓存查询结果
        # 当前为演示数据
        result = await orchestrator.get_investigation_status(investigation_id)

        if result.get("status") == "unknown":
            raise HTTPException(
                status_code=404,
                detail=f"Investigation {investigation_id} not found"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve investigation: {str(e)}"
        )


@router.delete(
    "/{investigation_id}",
    summary="取消调查",
    description="取消正在进行的调查"
)
async def cancel_investigation(investigation_id: str) -> Dict[str, str]:
    """
    取消调查

    Args:
        investigation_id: 调查ID

    Returns:
        dict: 取消结果
    """
    try:
        success = await orchestrator.cancel_investigation(investigation_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Investigation {investigation_id} not found or already completed"
            )

        return {
            "message": f"Investigation {investigation_id} cancelled successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel investigation: {str(e)}"
        )


@router.get(
    "/",
    summary="获取调查列表",
    description="获取所有调查的列表（支持分页和过滤）"
)
async def list_investigations(
    status: str = None,
    limit: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    """
    获取调查列表

    Args:
        status: 过滤状态（pending/completed/failed）
        limit: 返回数量
        offset: 偏移量

    Returns:
        dict: 调查列表
    """
    # TODO: 实现数据库查询
    return {
        "total": 0,
        "limit": limit,
        "offset": offset,
        "investigations": []
    }
