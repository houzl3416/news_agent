# NEWS GT 快速开始（3分钟运行）

适合小作业和学习演示，使用轻量级配置。

## 最小安装（仅核心依赖）

### 1. 克隆并安装

```bash
# 克隆仓库
git clone https://github.com/houzl3416/news_agent.git
cd news_agent

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装核心依赖
pip install -r requirements.txt
```

### 2. 初始化数据库（SQLite，零配置）

```bash
python scripts/setup_db.py
```

这会在当前目录创建 `news_gt.db` 文件。

### 3. 启动服务

```bash
uvicorn src.api.main:app --reload
```

服务运行在 http://localhost:8000

### 4. 测试 API

访问 http://localhost:8000/docs 查看自动生成的API文档。

或使用命令行测试：

```bash
# 健康检查
curl http://localhost:8000/health

# 提交调查（框架演示）
curl -X POST "http://localhost:8000/api/v1/investigation/submit" \
  -H "Content-Type: application/json" \
  -d '{"submission": "https://example.com/news", "submission_type": "url"}'
```

## 目录结构

运行后会生成：

```
news_agent/
├── news_gt.db          # SQLite数据库文件
├── logs/               # 日志目录
│   └── news_gt.log
└── venv/               # 虚拟环境
```

## 可选增强

### 安装 AI 支持（需要 OpenAI API Key）

```bash
pip install openai
```

编辑 `.env` 文件：
```
OPENAI_API_KEY=sk-your-key-here
```

### 安装 PostgreSQL 支持

```bash
pip install psycopg2-binary
```

修改 `.env` 文件：
```
DATABASE_URL=postgresql://user:password@localhost:5432/news_gt
```

## 常见问题

### Q: 为什么有些功能不工作？
A: 这是框架版本（v0.1.0），Agent 的 execute 方法都是框架代码，需要集成 LLM 才能实现完整功能。

### Q: 数据存在哪里？
A: SQLite 数据库文件 `news_gt.db`，可以用任何 SQLite 工具打开查看。

### Q: 如何重置数据库？
```bash
rm news_gt.db
python scripts/setup_db.py
```

### Q: 需要什么外部服务吗？
A: **不需要**！默认配置使用 SQLite，无需 PostgreSQL、Redis 等外部服务。

## 下一步

- 查看 [README.md](README.md) 了解完整功能
- 查看 [docs/requirements.md](docs/requirements.md) 了解产品设计
- 查看 [docs/architecture.md](docs/architecture.md) 了解系统架构
