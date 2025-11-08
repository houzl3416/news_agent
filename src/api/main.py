"""
FastAPI 主应用

NEWS GT - AI 新闻真相认知引擎
"""
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routes import investigation_router, taas_router
from .schemas import HealthCheckResponse

# 创建FastAPI应用
app = FastAPI(
    title="NEWS GT API",
    description="AI 新闻真相认知引擎 - Truth-as-a-Service",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS配置（生产环境需要限制）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(investigation_router)
app.include_router(taas_router)


# ============================================
# 基础端点
# ============================================

@app.get("/", summary="根路径")
async def root():
    """根路径，返回API信息"""
    return {
        "name": "NEWS GT API",
        "version": "0.1.0",
        "description": "AI 新闻真相认知引擎",
        "docs": "/docs"
    }


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="健康检查",
    description="检查API服务状态"
)
async def health_check() -> HealthCheckResponse:
    """
    健康检查端点

    Returns:
        HealthCheckResponse: 健康状态
    """
    return HealthCheckResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now().isoformat()
    )


# ============================================
# 异常处理
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


# ============================================
# 启动和关闭事件
# ============================================

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print("🚀 NEWS GT API starting...")
    # TODO: 初始化数据库连接
    # TODO: 初始化EKG
    # TODO: 初始化缓存
    print("✅ NEWS GT API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    print("🛑 NEWS GT API shutting down...")
    # TODO: 关闭数据库连接
    # TODO: 清理资源
    print("✅ NEWS GT API shut down successfully")


# ============================================
# 运行入口（用于开发）
# ============================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式热重载
        log_level="info"
    )
