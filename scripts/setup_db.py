#!/usr/bin/env python3
"""
数据库初始化脚本

创建数据库表和初始数据
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import init_database, db_manager
from src.utils import get_logger

logger = get_logger(__name__)


def main():
    """主函数"""
    logger.info("Starting database setup...")

    try:
        # 初始化数据库
        init_database()

        logger.info("Database setup completed successfully!")
        logger.info("Tables created:")
        logger.info("  - sources")
        logger.info("  - events")
        logger.info("  - claims")
        logger.info("  - entities")
        logger.info("  - artifacts")
        logger.info("  - claim_refutations")
        logger.info("  - investigation_history")

    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
