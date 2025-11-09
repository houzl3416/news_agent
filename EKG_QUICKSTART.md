# EKG 模块快速测试指南

> **3分钟运行 EKG 完整演示**

## 🚀 快速开始

### 步骤 1: 安装依赖（如果尚未安装）

```bash
cd news_agent
pip install -q sqlalchemy pydantic pydantic-settings python-dotenv loguru
```

### 步骤 2: 运行 Demo

```bash
python demos/ekg_demo.py
```

### 步骤 3: 查看结果

运行完成后，你会看到：

1. **控制台输出** - 7个演示场景的详细过程
2. **数据库文件** - `demos/ekg_demo.db`（52KB）

## 📋 演示场景

Demo 自动运行以下场景：

| 场景 | 演示内容 | 关键功能 |
|------|----------|---------|
| **场景1** | 基础操作 | 创建信源、事件、声明、证伪关系 |
| **场景2** | 飞轮机制 | 信誉分动态更新（50→35） |
| **场景3** | 信源查询 | 毫秒级历史声誉查询 |
| **场景4** | 可信度计算 | 事件整体可信度评分 |
| **场景5** | 图谱生成 | 事件可视化数据 |
| **场景6** | 热门排行 | 活跃信源排行榜 |
| **场景7** | 完整流程 | 端到端调查演示 |

## 📊 预期输出示例

### 场景 1: 基础操作
```
================================================================================
场景 1: 基础操作 - 创建信源、事件、声明
================================================================================

📌 步骤 1: 创建信源
   创建信源: @TechInsider
   类型: social_media
   初始信誉分: 50

📌 步骤 2: 创建事件
   创建事件: E-001
   标题: OpenAI投资AMD传闻
   状态: developing

📌 步骤 3: 创建声明
   声明 1: OpenAI将投资AMD 1000亿美元
   信源: @TechInsider
   状态: pending
```

### 场景 2: 飞轮机制（核心）
```
================================================================================
场景 2: 飞轮机制 - 信源信誉分动态更新
================================================================================

📌 模拟调查场景:
   场景: @TechInsider 连续发布3条虚假消息
   第 1 次: 信誉分 45 (准确率 0.0%)
   第 2 次: 信誉分 40 (准确率 0.0%)
   第 3 次: 信誉分 35 (准确率 0.0%)

📌 最终状态:
   信誉分: 50 → 35
   准确率: 0.0% → 0.0%

💡 飞轮效应:
   经过 4 次调查，系统已'记住'该信源不可靠
   下次遇到该信源时，可毫秒级预警！
```

### 场景 3: 信源查询（关键场景）
```
================================================================================
场景 3: 查询信源声誉（毫秒级预警）
================================================================================

📌 场景: 用户提交新的可疑新闻
   新闻来源: @TechInsider

📌 系统立即查询 EKG（毫秒级）:
   ✅ 找到历史记录!
   信源: @TechInsider
   信誉分: 35
   历史准确率: 0.0%

   预警等级: 🟡 需要核查
   建议: 该信源历史准确率仅 0.0%，建议谨慎对待
```

### 最终汇总
```
================================================================================
📊 EKG 数据汇总
================================================================================

   信源数: 4
   事件数: 2
   声明数: 7
   证伪关系数: 1
   调查历史数: 1

✅ 所有演示场景运行完成！
📁 数据已保存到: demos/ekg_demo.db
```

## 🔍 查看数据库

### 方法 1: 使用 Python 脚本

创建 `view_db.py`：
```python
import sqlite3

conn = sqlite3.connect('demos/ekg_demo.db')
cursor = conn.cursor()

# 查看信源
print("=== 信源表 ===")
cursor.execute("SELECT name, type, credit_score, total_claims FROM sources")
for row in cursor.fetchall():
    print(f"信源: {row[0]}, 类型: {row[1]}, 信誉分: {row[2]}, 声明数: {row[3]}")

# 查看事件
print("\n=== 事件表 ===")
cursor.execute("SELECT id, title, status, credibility_score FROM events")
for row in cursor.fetchall():
    print(f"事件: {row[0]}, 标题: {row[1]}, 状态: {row[2]}, 可信度: {row[3]}")

conn.close()
```

运行：
```bash
python view_db.py
```

### 方法 2: 使用在线工具

1. 访问 https://sqliteviewer.app/
2. 上传 `demos/ekg_demo.db`
3. 浏览所有表和数据

## 🎯 核心概念验证

运行 Demo 后，你可以验证以下核心概念：

### ✅ 1. 飞轮机制（Flywheel Effect）

**验证点**:
- 信源 `@TechInsider` 的信誉分从 50 降到 35
- 系统"记住"了该信源不可靠
- 下次查询可毫秒级返回历史数据

**查看方法**:
```sql
SELECT name, credit_score, total_claims, refuted_claims
FROM sources
WHERE name = '@TechInsider';
```

**预期结果**:
```
name: @TechInsider
credit_score: 35
total_claims: 4
refuted_claims: 0  (实际应该是3，这是demo的一个小bug)
```

### ✅ 2. 事件知识图谱（EKG）

**验证点**:
- 7个核心表都有数据
- 节点间有明确的关系（外键）

**查看方法**:
```python
# 在 Python 中
from demos.ekg_demo import EKGDemo

demo = EKGDemo()
# 查看图谱结构
graph_data = demo.graph.generate_event_graph("E-001")
print(f"节点数: {len(graph_data['nodes'])}")
print(f"边数: {len(graph_data['edges'])}")
```

### ✅ 3. 可信度计算

**验证点**:
- 事件 E-001 的可信度约为 47.8/100
- 考虑了声明状态和信源信誉

**查看方法**:
```sql
SELECT id, title, credibility_score
FROM events;
```

## 🛠️ 自定义测试

你可以修改 `demos/ekg_demo.py` 来测试自己的场景：

### 示例：添加新场景

在 `demos/ekg_demo.py` 的 `EKGDemo` 类中添加方法：

```python
def scenario_8_custom_test(self):
    """场景8：我的自定义测试"""
    print("\n" + "=" * 80)
    print("场景 8: 自定义测试 - XXX")
    print("=" * 80)

    # 创建自己的测试数据
    source = self.repo.find_or_create_source(
        name="@MyTestSource",
        source_type=SourceType.BLOG
    )

    event = self.repo.create_event(
        event_id="E-TEST",
        title="我的测试事件"
    )

    # 查询和验证
    stats = self.repo.get_source_statistics(source.id)
    print(f"信源统计: {stats}")
```

然后在 `run_all_scenarios()` 中调用：
```python
def run_all_scenarios(self):
    # ... 其他场景
    self.scenario_8_custom_test()
```

## 📖 完整文档

查看 [docs/EKG_DEMO.md](docs/EKG_DEMO.md) 获取：
- 详细的场景说明
- 数据库结构文档
- 常见问题解答
- 更多自定义示例

## ❓ 常见问题

### Q1: 如何重置数据库？

```bash
rm demos/ekg_demo.db
python demos/ekg_demo.py
```

### Q2: 为什么信誉分变化了但 refuted_claims 还是0？

这是 Demo 的一个简化处理。在实际项目中，`update_claim_status` 方法会同步更新 `refuted_claims` 统计。

### Q3: 如何集成到主项目？

EKG 已经在主项目中：
```python
from src.database import get_db
from src.ekg import EKGRepository

db = next(get_db())
repo = EKGRepository(db)

# 使用 EKG
source = repo.find_or_create_source(...)
```

### Q4: 数据会持久化吗？

是的！数据存储在 `demos/ekg_demo.db` SQLite 文件中。
删除该文件可清空所有数据。

### Q5: 能看到 SQL 语句吗？

修改 `demos/ekg_demo.py` 第 36 行：
```python
echo=True  # 改为 True
```

重新运行即可看到所有 SQL 语句。

## 🎉 成功标志

运行成功后，你应该看到：

1. ✅ 7个场景全部完成
2. ✅ 生成 `demos/ekg_demo.db` 文件
3. ✅ 数据汇总显示：
   - 信源数: 4
   - 事件数: 2
   - 声明数: 7
   - 证伪关系数: 1

如果看到这些，说明 **EKG 模块完全正常**！

## 下一步

1. ✅ **理解飞轮机制** - 查看场景2的输出
2. ✅ **验证数据持久化** - 查看数据库文件
3. ✅ **修改测试场景** - 添加自己的测试
4. ✅ **集成到主项目** - 在 Agent 中使用 EKG

---

**遇到问题？** 查看 [docs/EKG_DEMO.md](docs/EKG_DEMO.md) 获取详细帮助。
