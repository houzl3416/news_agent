"""
EKG (Event Knowledge Graph) 数据模型

使用 SQLAlchemy 定义知识图谱的节点和关系
"""
from datetime import datetime
from typing import List, Optional
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# ============================================
# 枚举类型
# ============================================

class SourceType(str, Enum):
    """信源类型"""
    OFFICIAL_MEDIA = "official_media"      # 官方媒体
    SOCIAL_MEDIA = "social_media"          # 社交媒体
    NEWS_OUTLET = "news_outlet"            # 新闻媒体
    BLOG = "blog"                          # 博客
    FORUM = "forum"                        # 论坛
    ANONYMOUS = "anonymous"                # 匿名
    UNKNOWN = "unknown"                    # 未知


class EventStatus(str, Enum):
    """事件状态"""
    DEVELOPING = "developing"       # 发展中
    INVESTIGATED = "investigated"   # 已调查
    VERIFIED = "verified"           # 已证实
    REFUTED = "refuted"             # 已证伪


class ClaimStatus(str, Enum):
    """声明状态"""
    PENDING = "pending"           # 待核实
    VERIFIED = "verified"         # 已证实
    REFUTED = "refuted"           # 已证伪
    UNVERIFIABLE = "unverifiable" # 无法验证


# ============================================
# 节点模型（核心表）
# ============================================

class Source(Base):
    """
    信源节点（最重要的节点）
    存储信息来源及其信誉分
    """
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    type = Column(SQLEnum(SourceType), nullable=False)

    # 核心指标：信誉分（0-100）
    credit_score = Column(Integer, default=50, nullable=False)

    # 元数据
    url = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)
    metadata = Column(JSON, default=dict)

    # 统计数据
    total_claims = Column(Integer, default=0)
    verified_claims = Column(Integer, default=0)
    refuted_claims = Column(Integer, default=0)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    claims = relationship("Claim", back_populates="source")

    def __repr__(self):
        return f"<Source(name='{self.name}', type='{self.type.value}', credit={self.credit_score})>"


class Event(Base):
    """
    事件节点
    代表一次调查的事件
    """
    __tablename__ = 'events'

    id = Column(String(64), primary_key=True)  # E-xxxxxxxx
    status = Column(SQLEnum(EventStatus), nullable=False, default=EventStatus.DEVELOPING)

    # 核心信息
    title = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)

    # 评分
    credibility_score = Column(Float, default=50.0)
    heat_score = Column(Float, default=0.0)

    # 标签和分类
    tags = Column(JSON, default=list)  # ["金融", "科技"]
    category = Column(String(64), nullable=True)

    # 元数据
    metadata = Column(JSON, default=dict)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    claims = relationship("Claim", back_populates="event")

    def __repr__(self):
        return f"<Event(id='{self.id}', status='{self.status.value}')>"


class Claim(Base):
    """
    声明节点
    代表一个具体的、可核查的事实断言
    """
    __tablename__ = 'claims'

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False)
    status = Column(SQLEnum(ClaimStatus), nullable=False, default=ClaimStatus.PENDING)

    # 外键
    event_id = Column(String(64), ForeignKey('events.id'), nullable=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)

    # 核查结果
    verification_result = Column(JSON, default=dict)  # 存储详细核查结果

    # 元数据
    claim_type = Column(String(64), nullable=True)  # financial, temporal, etc.
    entities = Column(JSON, default=list)  # 提及的实体
    metadata = Column(JSON, default=dict)

    # 时间戳
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    event = relationship("Event", back_populates="claims")
    source = relationship("Source", back_populates="claims")

    def __repr__(self):
        return f"<Claim(id={self.id}, status='{self.status.value}', text='{self.text[:50]}...')>"


class Entity(Base):
    """
    实体节点
    代表现实世界中的人、组织、地点
    """
    __tablename__ = 'entities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    type = Column(String(64), nullable=False)  # person, organization, location

    # 元数据
    description = Column(Text, nullable=True)
    metadata = Column(JSON, default=dict)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Entity(name='{self.name}', type='{self.type}')>"


class Artifact(Base):
    """
    物料节点
    代表信息的原始载体（URL、Tweet、文件等）
    """
    __tablename__ = 'artifacts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(64), nullable=False)  # url, tweet, document, image

    # 标识符
    url = Column(String(1024), nullable=True)
    content_hash = Column(String(128), nullable=True, index=True)

    # 内容
    content = Column(Text, nullable=True)
    metadata = Column(JSON, default=dict)

    # 时间戳
    captured_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Artifact(type='{self.type}', url='{self.url}')>"


# ============================================
# 关系表（边）
# ============================================

class ClaimRefutation(Base):
    """
    声明证伪关系（核心关系）
    记录一个声明证伪另一个声明
    """
    __tablename__ = 'claim_refutations'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 声明A证伪声明B
    refuting_claim_id = Column(Integer, ForeignKey('claims.id'), nullable=False)
    refuted_claim_id = Column(Integer, ForeignKey('claims.id'), nullable=False)

    # 证伪强度（0-1）
    confidence = Column(Float, default=1.0)

    # 证据
    evidence = Column(JSON, default=list)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ClaimRefutation(refuting={self.refuting_claim_id}, refuted={self.refuted_claim_id})>"


class InvestigationHistory(Base):
    """
    调查历史记录
    存储每次调查的完整结果
    """
    __tablename__ = 'investigation_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    investigation_id = Column(String(64), unique=True, nullable=False, index=True)

    # 关联事件
    event_id = Column(String(64), ForeignKey('events.id'), nullable=True)

    # 调查结果
    report = Column(JSON, nullable=False)  # 完整报告
    credibility_score = Column(Float, nullable=False)

    # 时间戳
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<InvestigationHistory(id='{self.investigation_id}', score={self.credibility_score})>"
