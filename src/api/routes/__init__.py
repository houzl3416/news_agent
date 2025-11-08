"""
API 路由模块

导出所有路由
"""
from .investigation import router as investigation_router
from .taas import router as taas_router

__all__ = [
    "investigation_router",
    "taas_router",
]
