# NEWS GT - AI 新闻真相认知引擎

> **从"事实核查"到"真相重构"** - 利用AI智能体集群全自动重构信息传播演变全貌

## 📖 项目简介

NEWS GT 是一个AI驱动的新闻真相认知引擎，旨在对抗信息"熵增"。通过自主AI智能体（Agent）集群协同作战，不仅告诉用户信息的"对"或"错"，更重要的是重构信息传播和演变的完整拼图。

### 核心亮点

- 🤖 **自主Agent集群** - 5个专业Agent协同工作，自动完成调查全流程
- 🧠 **事件知识图谱（EKG）** - 核心数据壁垒，实现毫秒级信源预警
- 🔌 **真相即服务（TaaS）** - API化溯源能力，可嵌入任何工作流
- 📊 **飞轮效应** - 调查越多，数据越准，系统越智能

## 🏗️ 架构设计

### 系统架构

```
用户层 (Web/API/插件)
    ↓
API网关层 (FastAPI)
    ↓
Agent编排层 (Orchestrator)
    ↓
Agent执行层 (5个专业Agent)
    ↓
数据层 (EKG + 任务队列)
    ↓
外部服务层 (LLM/搜索/数据源)
```

### 核心模块

#### 1. Agent系统

- **MonitorAgent（监控哨兵）** - 接收用户提交，触发调查
- **SourceHunterAgent（溯源猎手）** - 定位信息"0号病人"
- **VerifierAgent（核查专家）** - 交叉验证信息真实性
- **NarrativeAnalystAgent（叙事分析师）** - 分析信息演变和放大
- **SynthesizerAgent（首席编辑）** - 汇总发现，生成报告

#### 2. 事件知识图谱（EKG）

EKG是系统的"记忆"，存储结构化的调查结果：

**节点类型**:
- Source（信源）- 核心节点，含信誉分
- Event（事件）
- Claim（声明）
- Entity（实体）
- Artifact（物料）

**核心机制**:
- 每次调查后更新信源信誉分（飞轮效应）
- 毫秒级查询历史数据，实现快速预警
- 支持复杂图查询和关系分析

#### 3. TaaS API

提供3类核心API：

1. **信源信誉查询** - 查询信源历史可信度
2. **实时传言风险评分** - 为金融等领域提供预警
3. **事实核查** - 快速验证单个声明

## 🚀 快速开始

### 环境要求

- Python 3.10+
- 数据库: SQLite（默认，零配置）或 PostgreSQL（可选，用于生产）
- Redis（可选，用于异步任务队列）

### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/houzl3416/news_agent.git
cd news_agent
```

2. **创建虚拟环境**

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **配置环境变量（可选）**

```bash
cp .env.example .env
# 根据需要编辑 .env
```

**默认即可运行**：使用SQLite数据库，无需额外配置。

可选配置：
- `OPENAI_API_KEY` - OpenAI API密钥（实现完整AI功能时需要）
- `DATABASE_URL` - 如需切换到PostgreSQL
- 其他API密钥根据需要配置

5. **初始化数据库**

```bash
python scripts/setup_db.py
```

6. **启动API服务**

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看API文档

## 📚 使用示例

### 1. 提交调查请求

```bash
curl -X POST "http://localhost:8000/api/v1/investigation/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "submission": "https://example.com/breaking-news",
    "submission_type": "url"
  }'
```

响应：
```json
{
  "investigation_id": "E-12345678",
  "status": "pending",
  "message": "Investigation started successfully"
}
```

### 2. 查询调查结果

```bash
curl "http://localhost:8000/api/v1/investigation/E-12345678"
```

### 3. TaaS API - 查询信源信誉

```bash
curl -X POST "http://localhost:8000/api/v1/taas/source/check" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "source_name": "@TechInsider"
  }'
```

响应：
```json
{
  "source_name": "@TechInsider",
  "exists": true,
  "credit_score": 25,
  "reputation": "low",
  "statistics": {
    "total_claims": 10,
    "verified_claims": 2,
    "refuted_claims": 6,
    "accuracy_rate": 20.0
  }
}
```

## 🗂️ 项目结构

```
news_agent/
├── src/
│   ├── agents/              # Agent模块
│   │   ├── base.py         # Agent基类
│   │   ├── monitor.py      # 监控哨兵
│   │   ├── source_hunter.py # 溯源猎手
│   │   ├── verifier.py     # 核查专家
│   │   ├── narrative.py    # 叙事分析师
│   │   └── synthesizer.py  # 首席编辑
│   │
│   ├── orchestrator/        # 编排器
│   │   └── investigation.py
│   │
│   ├── ekg/                 # 事件知识图谱
│   │   ├── models.py       # 数据模型
│   │   ├── repository.py   # 数据访问层
│   │   └── graph_ops.py    # 图操作
│   │
│   ├── api/                 # API层
│   │   ├── main.py         # FastAPI主应用
│   │   ├── routes/
│   │   │   ├── investigation.py
│   │   │   └── taas.py
│   │   └── schemas.py      # Pydantic模型
│   │
│   ├── utils/               # 工具函数
│   │   ├── config.py       # 配置管理
│   │   └── logger.py       # 日志
│   └── database/            # 数据库
│       └── connection.py
│
├── tests/                   # 测试
├── docs/                    # 文档
│   ├── requirements.md     # 需求文档
│   └── architecture.md     # 架构文档
├── scripts/                 # 脚本
│   └── setup_db.py         # 数据库初始化
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 🔧 开发指南

### 添加新的Agent

1. 在 `src/agents/` 创建新文件
2. 继承 `BaseAgent` 类
3. 实现 `execute()` 方法
4. 在 `InvestigationOrchestrator` 中注册

示例：
```python
from src.agents.base import BaseAgent, InvestigationContext, AgentResult

class MyCustomAgent(BaseAgent):
    async def execute(self, context: InvestigationContext) -> AgentResult:
        # 你的逻辑
        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            data={"result": "..."}
        )
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行单个测试文件
pytest tests/unit/test_agents.py

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

## 📊 EKG飞轮机制详解

### 写入流程（调查结束后）

1. SynthesizerAgent 生成 `ekg_update` 数据
2. Orchestrator 调用 `EKGRepository.update_source_credit_score()`
3. 信源信誉分根据调查结果更新：
   - 可信度 >= 70: +5分
   - 可信度 < 30: -5分

### 读取流程（调查开始前）

1. Orchestrator 调用 `EKGRepository.query_source_reputation()`
2. 毫秒级返回信源历史信誉
3. 在报告中标注"高度存疑"或"历史准确率高"

### 示例

```
第1次调查: @TechInsider 发布虚假消息
→ 信誉分: 50 → 45

第2次调查: @TechInsider 再次发布虚假消息
→ 信誉分: 45 → 40
→ 调查开始前就预警"该信源历史准确率低"

第10次调查: 信誉分降至 18
→ 系统自动标记为"高度不可信信源"
```

## 🎯 路线图

### v0.1.0（当前 - MVP框架）
- ✅ 核心Agent框架
- ✅ EKG数据模型
- ✅ 基础TaaS API
- ⏳ 端到端调查流程

### v0.2.0（功能完善）
- ⏳ 集成LLM（OpenAI/Claude）
- ⏳ 实现完整的Agent逻辑
- ⏳ 水军检测算法
- ⏳ 前端UI

### v1.0.0（生产就绪）
- ⏳ 性能优化
- ⏳ API密钥管理
- ⏳ 监控和告警
- ⏳ 完整文档

## 📄 许可证

MIT License

## 📧 联系方式

- 项目主页: https://github.com/houzl3416/news_agent
- 问题反馈: https://github.com/houzl3416/news_agent/issues

---

**注意**: 这是一个框架项目（v0.1.0），核心AI功能尚未完全实现。所有Agent的execute方法都是框架代码，需要根据实际需求进行完整开发。

## 🎓 详细文档

- [需求文档](docs/requirements.md) - 完整的产品需求说明
- [架构文档](docs/architecture.md) - 系统架构设计详解