"""
配置管理模块

使用 pydantic-settings 管理环境变量和配置
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    应用配置
    从环境变量和.env文件加载
    """

    # 应用配置
    app_name: str = Field(default="NEWS_GT", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")

    # 数据库配置
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/news_gt",
        alias="DATABASE_URL"
    )
    database_pool_size: int = Field(default=10, alias="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, alias="DATABASE_MAX_OVERFLOW")

    # Redis配置
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # AI服务配置
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", alias="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=4096, alias="OPENAI_MAX_TOKENS")

    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", alias="ANTHROPIC_MODEL")

    # 搜索API配置
    serpapi_key: Optional[str] = Field(default=None, alias="SERPAPI_KEY")
    bing_search_key: Optional[str] = Field(default=None, alias="BING_SEARCH_KEY")

    # 社交媒体API
    twitter_bearer_token: Optional[str] = Field(default=None, alias="TWITTER_BEARER_TOKEN")
    twitter_api_key: Optional[str] = Field(default=None, alias="TWITTER_API_KEY")
    twitter_api_secret: Optional[str] = Field(default=None, alias="TWITTER_API_SECRET")

    # 数据源API
    sec_user_agent: str = Field(
        default="NEWS_GT/0.1 (contact@example.com)",
        alias="SEC_USER_AGENT"
    )
    bloomberg_api_key: Optional[str] = Field(default=None, alias="BLOOMBERG_API_KEY")

    # TaaS API配置
    taas_api_key_salt: str = Field(
        default="random_salt",
        alias="TAAS_API_KEY_SALT"
    )
    taas_rate_limit_per_minute: int = Field(default=60, alias="TAAS_RATE_LIMIT_PER_MINUTE")
    taas_rate_limit_per_hour: int = Field(default=1000, alias="TAAS_RATE_LIMIT_PER_HOUR")

    # Agent配置
    monitor_enabled: bool = Field(default=True, alias="MONITOR_ENABLED")
    monitor_check_interval: int = Field(default=300, alias="MONITOR_CHECK_INTERVAL")
    source_hunter_search_depth: int = Field(default=3, alias="SOURCE_HUNTER_SEARCH_DEPTH")
    source_hunter_max_results: int = Field(default=10, alias="SOURCE_HUNTER_MAX_RESULTS")
    verifier_timeout: int = Field(default=30, alias="VERIFIER_TIMEOUT")
    verifier_primary_sources: str = Field(
        default="SEC,Bloomberg,Reuters",
        alias="VERIFIER_PRIMARY_SOURCES"
    )

    # EKG配置
    ekg_initial_credit_score: int = Field(default=50, alias="EKG_INITIAL_CREDIT_SCORE")
    ekg_credit_score_increment: int = Field(default=5, alias="EKG_CREDIT_SCORE_INCREMENT")
    ekg_credit_score_decrement: int = Field(default=-5, alias="EKG_CREDIT_SCORE_DECREMENT")

    # 日志配置
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="logs/news_gt.log", alias="LOG_FILE")
    log_rotation: str = Field(default="1 day", alias="LOG_ROTATION")
    log_retention: str = Field(default="30 days", alias="LOG_RETENTION")

    # 安全配置
    secret_key: str = Field(default="change-this-in-production", alias="SECRET_KEY")
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        alias="CORS_ORIGINS"
    )

    # 性能配置
    max_concurrent_investigations: int = Field(
        default=10,
        alias="MAX_CONCURRENT_INVESTIGATIONS"
    )
    investigation_timeout: int = Field(default=300, alias="INVESTIGATION_TIMEOUT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        """将CORS origins字符串转换为列表"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def primary_sources_list(self) -> List[str]:
        """将primary sources字符串转换为列表"""
        return [source.strip() for source in self.verifier_primary_sources.split(",")]

    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return self.app_env.lower() == "production"

    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return self.app_env.lower() == "development"


# 全局配置实例
settings = Settings()
