"""
数据库连接管理

提供SQLAlchemy数据库连接和会话管理
"""
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from ..utils import settings, get_logger
from ..ekg.models import Base

logger = get_logger(__name__)


class DatabaseManager:
    """
    数据库管理器
    负责数据库连接池和会话管理
    """

    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialized = False

    def initialize(self):
        """初始化数据库连接"""
        if self._initialized:
            logger.warning("Database already initialized")
            return

        try:
            # 创建引擎
            self.engine = create_engine(
                settings.database_url,
                poolclass=QueuePool,
                pool_size=settings.database_pool_size,
                max_overflow=settings.database_max_overflow,
                pool_pre_ping=True,  # 连接前ping确保连接可用
                echo=settings.debug,  # 开发环境打印SQL
            )

            # 注册事件监听器
            self._register_event_listeners()

            # 创建SessionLocal
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            self._initialized = True
            logger.info(f"Database initialized: {settings.database_url}")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def _register_event_listeners(self):
        """注册数据库事件监听器"""

        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """连接建立时的回调"""
            logger.debug("Database connection established")

        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            """从连接池获取连接时的回调"""
            logger.debug("Connection checked out from pool")

    def create_tables(self):
        """创建所有表"""
        if not self._initialized:
            raise RuntimeError("Database not initialized")

        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise

    def drop_tables(self):
        """删除所有表（危险操作，仅用于开发）"""
        if settings.is_production():
            raise RuntimeError("Cannot drop tables in production environment")

        if not self._initialized:
            raise RuntimeError("Database not initialized")

        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("Database tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise

    def get_session(self) -> Session:
        """
        获取数据库会话

        Returns:
            Session: SQLAlchemy会话
        """
        if not self._initialized:
            raise RuntimeError("Database not initialized")

        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        提供事务性会话上下文管理器

        Usage:
            with db_manager.session_scope() as session:
                session.query(...)
                session.commit()

        Yields:
            Session: SQLAlchemy会话
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session rollback due to error: {e}")
            raise
        finally:
            session.close()

    def close(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")
            self._initialized = False


# 全局数据库管理器实例
db_manager = DatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI 依赖注入函数

    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()

    Yields:
        Session: SQLAlchemy会话
    """
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()


def init_database():
    """
    初始化数据库（应用启动时调用）

    初始化数据库连接并创建表
    """
    db_manager.initialize()
    db_manager.create_tables()
    logger.info("Database initialization completed")


def close_database():
    """
    关闭数据库（应用关闭时调用）
    """
    db_manager.close()
    logger.info("Database closed")
