# NEWS GT 系统架构设计

## 1. 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Web界面      │  │ TaaS API     │  │ 记者插件     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                      API网关层                               │
│  ┌──────────────────────────────────────────────────┐       │
│  │  REST API (FastAPI)                              │       │
│  │  - 用户提交端点                                   │       │
│  │  - 调查状态查询                                   │       │
│  │  - TaaS服务端点                                   │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Agent编排层                               │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Investigation Orchestrator (调查编排器)          │       │
│  │  - 任务管理                                       │       │
│  │  - Agent调度                                      │       │
│  │  - 状态追踪                                       │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                     Agent执行层                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Monitor  │ │  Source  │ │ Verifier │ │ Narrative│       │
│  │  Agent   │ │  Hunter  │ │  Agent   │ │ Analyst  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                    ┌──────────────┐                         │
│                    │ Synthesizer  │                         │
│                    │    Agent     │                         │
│                    └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                     数据层                                   │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ EKG (PostgreSQL)│  │  任务队列(Redis) │                  │
│  │  - sources      │  │  - 异步任务      │                  │
│  │  - claims       │  │  - 调查队列      │                  │
│  │  - events       │  └─────────────────┘                  │
│  │  - entities     │                                        │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                   外部服务层                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ LLM API  │ │ 搜索API  │ │ 社交媒体 │ │ SEC/监管 │       │
│  │ (OpenAI) │ │ (Serp)   │ │   API    │ │ 数据源   │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## 2. 目录结构

```
news_agent/
├── src/
│   ├── agents/                 # Agent模块
│   │   ├── __init__.py
│   │   ├── base.py            # Agent基类
│   │   ├── monitor.py         # 监控哨兵
│   │   ├── source_hunter.py   # 溯源猎手
│   │   ├── verifier.py        # 核查专家
│   │   ├── narrative.py       # 叙事分析师
│   │   └── synthesizer.py     # 首席编辑
│   │
│   ├── orchestrator/          # 编排器
│   │   ├── __init__.py
│   │   └── investigation.py   # 调查编排器
│   │
│   ├── ekg/                   # 事件知识图谱
│   │   ├── __init__.py
│   │   ├── models.py          # 数据模型
│   │   ├── repository.py      # 数据访问层
│   │   └── graph_ops.py       # 图操作
│   │
│   ├── api/                   # API层
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI主应用
│   │   ├── routes/            # 路由
│   │   │   ├── __init__.py
│   │   │   ├── investigation.py  # 调查相关API
│   │   │   └── taas.py           # TaaS API
│   │   └── schemas.py         # Pydantic模型
│   │
│   ├── services/              # 业务服务
│   │   ├── __init__.py
│   │   ├── llm_client.py      # LLM客户端
│   │   ├── search_client.py   # 搜索客户端
│   │   └── source_analyzer.py # 信源分析
│   │
│   ├── utils/                 # 工具函数
│   │   ├── __init__.py
│   │   ├── config.py          # 配置管理
│   │   └── logger.py          # 日志
│   │
│   └── database/              # 数据库
│       ├── __init__.py
│       ├── connection.py      # 数据库连接
│       └── migrations/        # 数据库迁移
│
├── tests/                     # 测试
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── docs/                      # 文档
│   ├── requirements.md        # 需求文档
│   ├── architecture.md        # 架构文档
│   └── api_spec.md            # API规范
│
├── scripts/                   # 脚本
│   ├── setup_db.py           # 数据库初始化
│   └── seed_data.py          # 种子数据
│
├── .env.example              # 环境变量示例
├── .gitignore
├── requirements.txt          # Python依赖
├── pyproject.toml           # 项目配置
└── README.md                # 项目说明
```

## 3. 核心模块设计

### 3.1 Agent基类

所有Agent继承统一基类，确保可扩展性：

```python
class BaseAgent:
    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config

    async def execute(self, context: InvestigationContext) -> AgentResult:
        """Agent执行的主方法"""
        raise NotImplementedError

    async def validate_input(self, context: InvestigationContext) -> bool:
        """验证输入"""
        pass
```

### 3.2 调查编排器

```python
class InvestigationOrchestrator:
    def __init__(self):
        self.agents = self._initialize_agents()
        self.ekg = EKGRepository()

    async def start_investigation(self, submission: UserSubmission) -> Investigation:
        """启动调查流程"""
        # 1. 创建调查上下文
        # 2. 查询EKG历史数据
        # 3. 按顺序调度Agents
        # 4. 收集结果并更新EKG
        # 5. 返回调查报告
```

### 3.3 EKG数据模型

```python
# SQLAlchemy Models
class Source(Base):
    __tablename__ = 'sources'
    id: int
    name: str
    type: SourceType
    credit_score: int  # 核心指标

class Claim(Base):
    __tablename__ = 'claims'
    id: int
    text: str
    source_id: int
    status: ClaimStatus
    timestamp: datetime

class Event(Base):
    __tablename__ = 'events'
    id: str  # E-1024
    status: EventStatus
    heat_score: float
    tags: list[str]
```

## 4. 数据流

### 4.1 用户提交流程

```
用户提交链接
    ↓
API Gateway 验证
    ↓
创建调查任务（异步）
    ↓
Orchestrator 启动
    ↓
EKG 查询历史（快速预警）
    ↓
Agent Pipeline 执行
    ↓
Synthesizer 生成报告
    ↓
EKG 更新（信誉分、关系）
    ↓
返回结果给用户
```

### 4.2 Agent Pipeline

```
Monitor Agent (可选)
    ↓
Source Hunter Agent（溯源）
    ↓ (原始信源)
EKG 查询信源信誉 ← 飞轮效应
    ↓
Verifier Agent（核查）
    ↓ (核查结果)
Narrative Analyst Agent（传播分析）
    ↓ (演变分析)
Synthesizer Agent（报告生成）
    ↓
EKG 写入（更新信誉分）
```

## 5. 技术决策

### 5.1 为什么选择 FastAPI
- 原生异步支持（Agent调用耗时）
- 自动API文档生成
- 类型安全
- 性能优秀

### 5.2 为什么用 PostgreSQL
- JSONB支持（灵活存储图数据）
- 成熟稳定
- 未来可迁移到专业图数据库（Neo4j）
- 支持复杂查询

### 5.3 为什么需要任务队列
- 调查任务耗时（可能几分钟）
- 需要异步执行
- 支持任务优先级

## 6. 扩展性考虑

### 6.1 Agent可插拔
- 通过配置文件注册新Agent
- 支持自定义Agent顺序
- 支持条件触发Agent

### 6.2 数据源可扩展
- 抽象数据源接口
- 支持新数据源注册
- API密钥集中管理

### 6.3 多租户支持（未来）
- API密钥隔离
- 调查配额管理
- 数据隔离

## 7. 性能目标

- EKG查询响应: < 100ms
- 简单调查完成: < 2分钟
- API响应时间: < 500ms（提交）
- 并发调查支持: 10+

## 8. 安全考虑

- API密钥加密存储
- 用户提交内容验证（防注入）
- 外部API调用速率限制
- 敏感数据脱敏
