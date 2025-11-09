# EKG JSON 数据导入指南

> **用 JSON 文件快速录入 EKG 数据**

## 📋 概览

EKG 现在支持通过 JSON 文件批量导入数据，让数据录入变得更加简单和标准化。

### 支持的方式

1. **命令行工具** - 从 JSON 文件或目录导入
2. **Web API** - 通过 HTTP POST 提交 JSON 数据
3. **Python 代码** - 在代码中直接调用导入器

## 🚀 快速开始

### 方式 1: 命令行导入

```bash
# 查看 JSON 格式示例
python demos/ekg_import_json.py --example

# 从单个 JSON 文件导入
python demos/ekg_import_json.py --file data.json

# 从目录批量导入所有 JSON 文件
python demos/ekg_import_json.py --dir ./data/

# 指定数据库文件
python demos/ekg_import_json.py --file data.json --db my_ekg.db
```

### 方式 2: Web API 导入

```bash
# 启动 Web 服务器
python demos/ekg_web_demo.py

# 使用 curl 提交 JSON 数据
curl -X POST http://localhost:8000/api/import \
  -H "Content-Type: application/json" \
  -d @data.json
```

### 方式 3: Python 代码导入

```python
from demos.ekg_import_json import EKGJSONImporter
import json

# 创建导入器
importer = EKGJSONImporter("my_database.db")

# 从文件导入
importer.import_from_file("data.json")

# 或从字典导入
with open("data.json") as f:
    data = json.load(f)
importer.import_data(data)

# 关闭连接
importer.close()
```

## 📝 JSON 数据格式

### 完整示例

```json
{
  "sources": [
    {
      "name": "新华社",
      "type": "official_media",
      "url": "https://www.xinhuanet.com",
      "description": "中国官方通讯社",
      "extra_data": {
        "country": "China",
        "founded": "1931"
      }
    }
  ],
  "events": [
    {
      "id": "E-DEMO-001",
      "title": "某公司发布新产品",
      "description": "某科技公司宣布发布新产品",
      "status": "developing",
      "extra_data": {
        "category": "technology",
        "impact": "high"
      }
    }
  ],
  "claims": [
    {
      "text": "该公司将于下月发布新产品",
      "source_name": "@TechNews",
      "event_id": "E-DEMO-001",
      "status": "pending",
      "claim_type": "temporal",
      "verification_result": {},
      "extra_data": {
        "confidence": 0.8
      }
    }
  ],
  "entities": [
    {
      "name": "某科技公司",
      "type": "organization",
      "description": "一家知名科技公司",
      "extra_data": {
        "industry": "technology",
        "founded": "2000"
      }
    }
  ],
  "artifacts": [
    {
      "type": "image",
      "url": "https://example.com/product_image.jpg",
      "hash": "abc123def456",
      "content": "base64_encoded_content_or_text",
      "extra_data": {
        "width": 1920,
        "height": 1080,
        "claim_id": 1
      }
    }
  ],
  "refutations": [
    {
      "refuting_claim_id": 2,
      "refuted_claim_id": 1,
      "confidence": 0.95,
      "evidence": {
        "source": "official_statement",
        "verified_by": "新华社"
      }
    }
  ]
}
```

### 字段说明

#### sources (信源)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 信源名称 |
| type | string | ✅ | 信源类型 (见下方类型列表) |
| url | string | ❌ | 信源URL |
| description | string | ❌ | 描述 |
| extra_data | object | ❌ | 额外数据 |

**信源类型 (type)**:
- `official_media` - 官方媒体
- `social_media` - 社交媒体
- `news_outlet` - 新闻媒体
- `blog` - 博客
- `forum` - 论坛
- `anonymous` - 匿名
- `unknown` - 未知

#### events (事件)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | ✅ | 事件ID (如 E-001) |
| title | string | ✅ | 事件标题 |
| description | string | ❌ | 事件描述 |
| status | string | ❌ | 事件状态 (默认: developing) |
| extra_data | object | ❌ | 额外数据 |

**事件状态 (status)**:
- `developing` - 发展中
- `investigated` - 已调查
- `verified` - 已证实
- `refuted` - 已证伪

#### claims (声明)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| text | string | ✅ | 声明内容 |
| source_id | int | ❌ | 信源ID (与source_name二选一) |
| source_name | string | ❌ | 信源名称 (与source_id二选一) |
| event_id | string | ❌ | 关联事件ID |
| status | string | ❌ | 声明状态 (默认: pending) |
| claim_type | string | ❌ | 声明类型 |
| verification_result | object | ❌ | 核查结果 |
| extra_data | object | ❌ | 额外数据 |

**声明状态 (status)**:
- `pending` - 待核实
- `verified` - 已证实
- `refuted` - 已证伪
- `unverifiable` - 无法验证

**声明类型 (claim_type)**:
- `financial` - 财务类
- `temporal` - 时间类
- `factual` - 事实类
- `opinion` - 观点类
- 或自定义类型

#### entities (实体)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 实体名称 |
| type | string | ✅ | 实体类型 |
| description | string | ❌ | 描述 |
| extra_data | object | ❌ | 额外数据 |

**实体类型 (type)**:
- `person` - 人物
- `organization` - 组织
- `location` - 地点
- 或自定义类型

#### artifacts (物料)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | ✅ | 物料类型 |
| url | string | ❌ | 物料URL |
| hash | string | ❌ | 文件哈希值 (SHA256) |
| content | string | ❌ | 物料内容 |
| extra_data | object | ❌ | 额外数据 (可包含claim_id) |

**物料类型 (type)**:
- `image` - 图片
- `video` - 视频
- `document` - 文档
- `url` - 链接
- `tweet` - 推文
- 或自定义类型

#### refutations (证伪关系)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| refuting_claim_id | int | ✅ | 证伪方声明ID |
| refuted_claim_id | int | ✅ | 被证伪方声明ID |
| confidence | float | ❌ | 置信度 (0-1，默认1.0) |
| evidence | object | ❌ | 证据信息 |

## 💡 使用技巧

### 1. 增量导入

你可以多次导入数据，系统会自动处理：

```bash
# 第一批数据
python demos/ekg_import_json.py --file batch1.json

# 第二批数据
python demos/ekg_import_json.py --file batch2.json
```

对于已存在的信源和实体，系统会自动使用现有记录而不是创建重复。

### 2. 只导入部分数据

JSON 文件可以只包含需要的部分：

```json
{
  "claims": [
    {
      "text": "新的声明",
      "source_name": "已存在的信源",
      "event_id": "E-001",
      "status": "pending"
    }
  ]
}
```

### 3. 使用 source_name 代替 source_id

在声明中，可以使用信源名称而不是ID：

```json
{
  "claims": [
    {
      "text": "...",
      "source_name": "新华社",
      "event_id": "E-001"
    }
  ]
}
```

系统会自动查找对应的信源ID。

### 4. 批量导入目录

如果有多个 JSON 文件：

```
data/
  ├── sources.json
  ├── events_2024.json
  ├── claims_jan.json
  └── claims_feb.json
```

使用目录导入：

```bash
python demos/ekg_import_json.py --dir ./data/
```

### 5. 在 extra_data 中存储自定义信息

所有实体都支持 `extra_data` 字段，可以存储任意 JSON 数据：

```json
{
  "sources": [
    {
      "name": "某博主",
      "type": "blog",
      "extra_data": {
        "followers": 100000,
        "platform": "Weibo",
        "verified": false,
        "tags": ["科技", "财经"],
        "custom_score": 85.5
      }
    }
  ]
}
```

## 📊 导入结果

导入完成后会显示统计信息：

```
================================================================================
📊 导入统计
================================================================================
  信源数: 3
  事件数: 1
  声明数: 3
  实体数: 2
  物料数: 2
  证伪关系数: 1
================================================================================
```

如果有错误，也会显示：

```
================================================================================
📊 导入统计
================================================================================
  信源数: 2
  事件数: 1
  声明数: 3
  实体数: 0
  物料数: 0
  证伪关系数: 1
  ❌ 错误数: 2
================================================================================
```

## 🔧 高级用法

### Web API 导入

启动 Web 服务器后，可以通过 HTTP POST 提交数据：

```bash
# 启动服务器
python demos/ekg_web_demo.py
```

使用 curl:

```bash
curl -X POST http://localhost:8000/api/import \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [
      {
        "name": "测试信源",
        "type": "social_media"
      }
    ],
    "events": [
      {
        "id": "E-TEST-001",
        "title": "测试事件"
      }
    ]
  }'
```

使用 Python requests:

```python
import requests

data = {
    "sources": [{
        "name": "测试信源",
        "type": "social_media"
    }],
    "events": [{
        "id": "E-TEST-001",
        "title": "测试事件"
    }]
}

response = requests.post(
    "http://localhost:8000/api/import",
    json=data
)

print(response.json())
```

### 在代码中使用

```python
from demos.ekg_import_json import EKGJSONImporter

# 创建导入器
importer = EKGJSONImporter("my_database.db")

# 从字典导入
data = {
    "sources": [
        {"name": "Source 1", "type": "news_outlet"},
        {"name": "Source 2", "type": "social_media"}
    ],
    "events": [
        {"id": "E-001", "title": "Event 1"}
    ]
}

success = importer.import_data(data)

# 查看统计
print(importer.stats)

# 关闭连接
importer.close()
```

## ❓ 常见问题

### Q1: 如何处理重复数据？

**A**: 信源和实体会自动去重（根据名称）。事件、声明、物料会创建新记录。

### Q2: 导入失败怎么办？

**A**: 查看错误信息，通常是：
- 字段类型不匹配
- 必填字段缺失
- 外键关联不存在（如声明引用的信源不存在）

### Q3: 可以导入到现有数据库吗？

**A**: 可以！指定现有数据库文件即可：

```bash
python demos/ekg_import_json.py --file new_data.json --db demos/ekg_demo.db
```

### Q4: 声明的 claim_id 是什么？

**A**: 这是数据库自动分配的ID，用于建立证伪关系。通常：
1. 先导入声明，查看生成的ID
2. 再根据ID创建证伪关系

或者先导入所有数据，再手动查询数据库获取ID。

### Q5: extra_data 可以存储什么？

**A**: 任何 JSON 可序列化的数据：

```json
"extra_data": {
  "string": "文本",
  "number": 123,
  "float": 45.67,
  "boolean": true,
  "array": [1, 2, 3],
  "object": {"nested": "value"}
}
```

### Q6: 如何批量导入声明但使用不同的信源？

**A**: 在 JSON 中为每个声明指定不同的 `source_name`:

```json
{
  "claims": [
    {"text": "声明1", "source_name": "信源A"},
    {"text": "声明2", "source_name": "信源B"},
    {"text": "声明3", "source_name": "信源C"}
  ]
}
```

## 📚 示例文件

项目中提供了完整的示例文件：

- `demos/example_data.json` - 包含所有类型数据的示例

查看示例：

```bash
cat demos/example_data.json
```

或使用导入工具查看格式说明：

```bash
python demos/ekg_import_json.py --example
```

## 🎯 最佳实践

1. **先导入信源**：确保所有信源都已存在
2. **再导入事件**：创建事件框架
3. **然后导入声明**：关联到信源和事件
4. **最后导入证伪关系**：在所有声明都存在后创建

示例流程：

```bash
# 步骤1: 导入信源
python demos/ekg_import_json.py --file sources.json

# 步骤2: 导入事件
python demos/ekg_import_json.py --file events.json

# 步骤3: 导入声明
python demos/ekg_import_json.py --file claims.json

# 步骤4: 导入证伪关系（可选）
python demos/ekg_import_json.py --file refutations.json
```

5. **使用有意义的ID**：事件ID建议使用 `E-YYYYMMDD-NNN` 格式
6. **验证数据**：导入后使用可视化工具检查

```bash
# 导入数据
python demos/ekg_import_json.py --file data.json

# 查看数据
python demos/view_ekg_data.py

# 可视化验证
python demos/ekg_visualization.py --all
```

## 🔗 相关文档

- [EKG_QUICKSTART.md](EKG_QUICKSTART.md) - 快速开始指南
- [EKG_VISUALIZATION.md](EKG_VISUALIZATION.md) - 可视化使用指南
- [docs/EKG_GUIDE.md](docs/EKG_GUIDE.md) - EKG 使用场景
- [docs/EKG_TECHNICAL.md](docs/EKG_TECHNICAL.md) - 技术实现细节

---

**让数据录入变得简单！📝**
