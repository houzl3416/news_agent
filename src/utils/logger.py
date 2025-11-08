"""
日志模块

使用 loguru 提供结构化日志
"""
import sys
from pathlib import Path
from loguru import logger

from .config import settings


def setup_logger():
    """
    配置日志系统

    根据环境变量配置日志级别、输出格式和文件存储
    """
    # 移除默认handler
    logger.remove()

    # 日志格式
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # 控制台输出
    logger.add(
        sys.stderr,
        format=log_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )

    # 文件输出
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        log_file,
        format=log_format,
        level=settings.log_level,
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        compression="zip",
        backtrace=True,
        diagnose=True,
        enqueue=True  # 异步写入
    )

    # 生产环境额外配置
    if settings.is_production():
        # 错误日志单独文件
        error_log_file = log_file.parent / "error.log"
        logger.add(
            error_log_file,
            format=log_format,
            level="ERROR",
            rotation="1 day",
            retention="90 days",
            compression="zip",
            backtrace=True,
            diagnose=True,
            enqueue=True
        )

    logger.info(f"Logger initialized - Level: {settings.log_level}, File: {log_file}")

    return logger


# 初始化日志
app_logger = setup_logger()


def get_logger(name: str = None):
    """
    获取logger实例

    Args:
        name: logger名称（可选）

    Returns:
        logger实例
    """
    if name:
        return logger.bind(name=name)
    return logger
