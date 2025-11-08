# NEWS GT API 规范

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API Version**: v1
- **认证方式**: API Key (TaaS API)

## API端点概览

### 1. 调查相关 API

#### 1.1 提交调查请求

**POST** `/api/v1/investigation/submit`

提交新闻链接或事件描述，启动调查任务。

**请求体**:
```json
{
  "submission": "https://example.com/news",
  "submission_type": "url"  // "url" 或 "text"
}
```

**响应**:
```json
{
  "investigation_id": "E-12345678",
  "status": "pending",
  "message": "Investigation started successfully"
}
```

#### 1.2 查询调查结果

**GET** `/api/v1/investigation/{investigation_id}`

根据调查ID查询调查进度和结果。

**响应**:
```json
{
  "investigation_id": "E-12345678",
  "status": "completed",
  "credibility_score": 35.5,
  "report": {
    "investigation_id": "E-12345678",
    "timestamp": "2024-01-01T12:00:00",
    "user_submission": "https://example.com/news",
    "source_tracing": {
      "source_name": "@TechInsider",
      "source_type": "social_media",
      "first_appearance": "2024-01-01T10:00:00",
      "confidence": 0.85
    },
    "verification": {
      "claims_verified": 3,
      "overall_status": "存在证伪证据",
      "details": [...]
    },
    "narrative_evolution": {...},
    "summary": "信息最早来自 @TechInsider。发现 2 项声明存在证伪证据。",
    "recommendation": "建议：该信息存在多处不实之处，建议谨慎对待。"
  }
}
```

#### 1.3 取消调查

**DELETE** `/api/v1/investigation/{investigation_id}`

取消正在进行的调查。

**响应**:
```json
{
  "message": "Investigation E-12345678 cancelled successfully"
}
```

### 2. TaaS API

所有TaaS API需要在请求头中包含API密钥：
```
X-API-Key: your-api-key
```

#### 2.1 信源信誉查询

**POST** `/api/v1/taas/source/check`

查询信源的历史信誉和统计数据。

**请求体**:
```json
{
  "source_name": "@TechInsider"
}
```

**响应**:
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

**reputation 等级**:
- `high`: 信誉分 >= 70
- `medium`: 信誉分 40-70
- `low`: 信誉分 < 40

#### 2.2 实时传言风险评分

**POST** `/api/v1/taas/risk/score`

对传言文本进行风险评分，用于金融交易等场景的预警。

**请求体**:
```json
{
  "text": "OpenAI投资AMD 1000亿美元",
  "source": "@TechInsider"  // 可选
}
```

**响应**:
```json
{
  "risk_score": 75.5,
  "risk_level": "high",
  "factors": [
    "信源历史准确率仅18%",
    "未找到官方证据",
    "类似传言曾被证伪"
  ],
  "recommendation": "高度存疑，建议等待官方确认"
}
```

**risk_level 等级**:
- `low`: 风险分 < 40
- `medium`: 风险分 40-70
- `high`: 风险分 > 70

#### 2.3 事实核查

**POST** `/api/v1/taas/fact/check`

对单个声明进行事实核查。

**请求体**:
```json
{
  "claim": "OpenAI将于Q2收购AMD",
  "entities": ["OpenAI", "AMD"]  // 可选
}
```

**响应**:
```json
{
  "claim": "OpenAI将于Q2收购AMD",
  "status": "refuted",
  "confidence": 0.9,
  "evidence": [
    {
      "source": "SEC EDGAR",
      "finding": "未找到相关披露文件",
      "url": "https://www.sec.gov/..."
    }
  ],
  "summary": "在SEC官方数据库中未找到该交易的披露文件"
}
```

**status 状态**:
- `verified`: 已证实
- `refuted`: 已证伪
- `unverifiable`: 无法验证

#### 2.4 获取TaaS统计

**GET** `/api/v1/taas/stats`

获取API使用统计和系统状态。

**响应**:
```json
{
  "total_requests": 1234,
  "sources_indexed": 567,
  "claims_verified": 890,
  "avg_response_time_ms": 120
}
```

### 3. 通用端点

#### 3.1 健康检查

**GET** `/health`

检查API服务状态。

**响应**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2024-01-01T12:00:00"
}
```

## 错误响应

所有错误响应遵循统一格式：

```json
{
  "error": "错误类型",
  "detail": "详细错误信息",
  "investigation_id": "E-12345678"  // 如果适用
}
```

**常见HTTP状态码**:
- `200`: 成功
- `400`: 请求参数错误
- `401`: 未授权（API密钥无效）
- `404`: 资源不存在
- `429`: 请求过于频繁（速率限制）
- `500`: 服务器内部错误

## 速率限制

TaaS API有速率限制：
- 每分钟: 60次请求
- 每小时: 1000次请求

超出限制时返回 `429 Too Many Requests`。

## 示例代码

### Python

```python
import requests

# 提交调查
response = requests.post(
    "http://localhost:8000/api/v1/investigation/submit",
    json={
        "submission": "https://example.com/news",
        "submission_type": "url"
    }
)
investigation_id = response.json()["investigation_id"]

# 查询信源信誉（TaaS）
response = requests.post(
    "http://localhost:8000/api/v1/taas/source/check",
    headers={"X-API-Key": "your-api-key"},
    json={"source_name": "@TechInsider"}
)
credit_score = response.json()["credit_score"]
```

### JavaScript

```javascript
// 提交调查
const response = await fetch('http://localhost:8000/api/v1/investigation/submit', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    submission: 'https://example.com/news',
    submission_type: 'url'
  })
});
const data = await response.json();

// TaaS风险评分
const riskResponse = await fetch('http://localhost:8000/api/v1/taas/risk/score', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-api-key'
  },
  body: JSON.stringify({
    text: 'OpenAI投资AMD 1000亿美元',
    source: '@TechInsider'
  })
});
```

## 交互式文档

访问 `http://localhost:8000/docs` 查看自动生成的Swagger UI文档，可直接在浏览器中测试API。
