#!/usr/bin/env python3
"""
EKG 交互式 Web 演示

提供一个简单的 Web 界面来浏览和可视化 EKG 数据。

运行方式:
    python demos/ekg_web_demo.py

然后在浏览器中打开: http://localhost:8000
"""
import sqlite3
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

DB_PATH = "demos/ekg_demo.db"

app = FastAPI(title="EKG Web Demo", description="事件知识图谱 交互式演示")


# ============================================================================
# 数据模型
# ============================================================================

class SourceInfo(BaseModel):
    id: int
    name: str
    type: str
    credit_score: int
    total_claims: int
    verified_claims: int
    refuted_claims: int
    accuracy_rate: float


class EventInfo(BaseModel):
    id: str
    title: str
    status: str
    credibility_score: Optional[float]
    claim_count: int


class ClaimInfo(BaseModel):
    id: int
    text: str
    status: str
    source_name: str
    event_id: str


class DBStats(BaseModel):
    sources: int
    events: int
    claims: int
    entities: int
    refutations: int
    investigations: int


# ============================================================================
# 数据库操作
# ============================================================================

def get_db():
    """获取数据库连接"""
    if not Path(DB_PATH).exists():
        raise HTTPException(status_code=404, detail=f"数据库文件不存在: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================================
# API 端点
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def index():
    """主页"""
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EKG 交互式演示 - 事件知识图谱</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }

        .subtitle {
            color: #666;
            font-size: 1.1em;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .stat-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }

        .stat-label {
            color: #666;
            margin-top: 5px;
        }

        .section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        h2 {
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }

        .button-group {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }

        .viz-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 25px;
            border-radius: 10px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .viz-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }

        .viz-button:active {
            transform: translateY(0);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #f0f0f0;
        }

        th {
            background: #f8f9fa;
            color: #667eea;
            font-weight: 600;
        }

        tr:hover {
            background: #f8f9fa;
        }

        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }

        .badge-verified {
            background: #d4edda;
            color: #155724;
        }

        .badge-refuted {
            background: #f8d7da;
            color: #721c24;
        }

        .badge-pending {
            background: #d1ecf1;
            color: #0c5460;
        }

        .score-high {
            color: #28a745;
            font-weight: bold;
        }

        .score-medium {
            color: #ffc107;
            font-weight: bold;
        }

        .score-low {
            color: #dc3545;
            font-weight: bold;
        }

        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }

        .footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
        }

        .event-link {
            color: #667eea;
            text-decoration: none;
            cursor: pointer;
        }

        .event-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 EKG 交互式演示</h1>
            <p class="subtitle">Event Knowledge Graph - 事件知识图谱可视化系统</p>
        </div>

        <div id="stats" class="stats-grid">
            <div class="loading">正在加载统计数据...</div>
        </div>

        <div class="section">
            <h2>📊 可视化视图</h2>
            <div class="button-group">
                <button class="viz-button" onclick="generateViz('all')">
                    📈 全局事件图谱
                </button>
                <button class="viz-button" onclick="generateViz('sources')">
                    🌐 信源网络图
                </button>
                <button class="viz-button" onclick="generateViz('refutations')">
                    ⚡ 证伪关系图
                </button>
            </div>
        </div>

        <div class="section">
            <h2>📋 事件列表</h2>
            <div id="events">
                <div class="loading">正在加载事件数据...</div>
            </div>
        </div>

        <div class="section">
            <h2>📰 信源排行</h2>
            <div id="sources">
                <div class="loading">正在加载信源数据...</div>
            </div>
        </div>

        <div class="section">
            <h2>💬 声明列表</h2>
            <div id="claims">
                <div class="loading">正在加载声明数据...</div>
            </div>
        </div>

        <div class="footer">
            <p>NEWS GT - AI 新闻真相认知引擎</p>
            <p style="font-size: 0.9em; margin-top: 10px;">Powered by EKG (Event Knowledge Graph)</p>
        </div>
    </div>

    <script>
        // 加载统计数据
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();

                const statsHTML = `
                    <div class="stat-card">
                        <div class="stat-number">${data.sources}</div>
                        <div class="stat-label">📰 信源</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.events}</div>
                        <div class="stat-label">📋 事件</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.claims}</div>
                        <div class="stat-label">💬 声明</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.entities}</div>
                        <div class="stat-label">🏷️ 实体</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.refutations}</div>
                        <div class="stat-label">⚡ 证伪</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.investigations}</div>
                        <div class="stat-label">🔎 调查</div>
                    </div>
                `;

                document.getElementById('stats').innerHTML = statsHTML;
            } catch (error) {
                document.getElementById('stats').innerHTML = '<div class="loading">加载失败</div>';
            }
        }

        // 加载事件列表
        async function loadEvents() {
            try {
                const response = await fetch('/api/events');
                const events = await response.json();

                let tableHTML = `
                    <table>
                        <thead>
                            <tr>
                                <th>事件ID</th>
                                <th>标题</th>
                                <th>状态</th>
                                <th>可信度</th>
                                <th>声明数</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                events.forEach(event => {
                    const scoreClass = event.credibility_score >= 70 ? 'score-high' :
                                     event.credibility_score >= 40 ? 'score-medium' : 'score-low';
                    const scoreText = event.credibility_score ? event.credibility_score.toFixed(1) : 'N/A';

                    tableHTML += `
                        <tr>
                            <td><strong>${event.id}</strong></td>
                            <td>${event.title}</td>
                            <td><span class="badge badge-pending">${event.status}</span></td>
                            <td><span class="${scoreClass}">${scoreText}</span></td>
                            <td>${event.claim_count}</td>
                            <td>
                                <a class="event-link" onclick="generateViz('event', '${event.id}')">查看图谱</a>
                            </td>
                        </tr>
                    `;
                });

                tableHTML += '</tbody></table>';
                document.getElementById('events').innerHTML = tableHTML;
            } catch (error) {
                document.getElementById('events').innerHTML = '<div class="loading">加载失败</div>';
            }
        }

        // 加载信源列表
        async function loadSources() {
            try {
                const response = await fetch('/api/sources');
                const sources = await response.json();

                let tableHTML = `
                    <table>
                        <thead>
                            <tr>
                                <th>信源名称</th>
                                <th>类型</th>
                                <th>信誉分</th>
                                <th>准确率</th>
                                <th>总声明</th>
                                <th>已验证</th>
                                <th>已证伪</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                sources.forEach(source => {
                    const scoreClass = source.credit_score >= 70 ? 'score-high' :
                                     source.credit_score >= 40 ? 'score-medium' : 'score-low';

                    tableHTML += `
                        <tr>
                            <td><strong>📰 ${source.name}</strong></td>
                            <td>${source.type}</td>
                            <td><span class="${scoreClass}">${source.credit_score}</span></td>
                            <td>${source.accuracy_rate.toFixed(1)}%</td>
                            <td>${source.total_claims}</td>
                            <td>${source.verified_claims}</td>
                            <td>${source.refuted_claims}</td>
                        </tr>
                    `;
                });

                tableHTML += '</tbody></table>';
                document.getElementById('sources').innerHTML = tableHTML;
            } catch (error) {
                document.getElementById('sources').innerHTML = '<div class="loading">加载失败</div>';
            }
        }

        // 加载声明列表
        async function loadClaims() {
            try {
                const response = await fetch('/api/claims?limit=20');
                const claims = await response.json();

                let tableHTML = `
                    <table>
                        <thead>
                            <tr>
                                <th style="width: 50%">声明内容</th>
                                <th>信源</th>
                                <th>事件</th>
                                <th>状态</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                claims.forEach(claim => {
                    const badgeClass = claim.status === 'verified' ? 'badge-verified' :
                                     claim.status === 'refuted' ? 'badge-refuted' : 'badge-pending';
                    const statusText = claim.status === 'verified' ? '✓ 已验证' :
                                     claim.status === 'refuted' ? '✗ 已证伪' : '? 待核实';

                    tableHTML += `
                        <tr>
                            <td>${claim.text}</td>
                            <td>${claim.source_name}</td>
                            <td>${claim.event_id}</td>
                            <td><span class="badge ${badgeClass}">${statusText}</span></td>
                        </tr>
                    `;
                });

                tableHTML += '</tbody></table>';
                document.getElementById('claims').innerHTML = tableHTML;
            } catch (error) {
                document.getElementById('claims').innerHTML = '<div class="loading">加载失败</div>';
            }
        }

        // 生成可视化
        async function generateViz(type, eventId = null) {
            const url = eventId ?
                `/api/visualize?type=${type}&event_id=${eventId}` :
                `/api/visualize?type=${type}`;

            try {
                const response = await fetch(url);
                const data = await response.json();
                window.open(data.url, '_blank');
            } catch (error) {
                alert('可视化生成失败: ' + error);
            }
        }

        // 页面加载时执行
        window.onload = function() {
            loadStats();
            loadEvents();
            loadSources();
            loadClaims();
        };
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/stats", response_model=DBStats)
async def get_stats():
    """获取数据库统计信息"""
    conn = get_db()
    cursor = conn.cursor()

    stats = {}
    tables = ['sources', 'events', 'claims', 'entities', 'artifacts', 'claim_refutations', 'investigation_history']

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        key = table if table in ['sources', 'events', 'claims', 'entities'] else \
              'refutations' if table == 'claim_refutations' else 'investigations'
        stats[key] = count

    conn.close()
    return stats


@app.get("/api/events", response_model=List[EventInfo])
async def get_events():
    """获取所有事件"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.*,
               COUNT(c.id) as claim_count
        FROM events e
        LEFT JOIN claims c ON e.id = c.event_id
        GROUP BY e.id
        ORDER BY e.created_at DESC
    """)

    events = []
    for row in cursor.fetchall():
        events.append(EventInfo(
            id=row['id'],
            title=row['title'],
            status=row['status'],
            credibility_score=row['credibility_score'],
            claim_count=row['claim_count']
        ))

    conn.close()
    return events


@app.get("/api/sources", response_model=List[SourceInfo])
async def get_sources():
    """获取所有信源"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, type, credit_score, total_claims, verified_claims, refuted_claims
        FROM sources
        ORDER BY credit_score DESC
    """)

    sources = []
    for row in cursor.fetchall():
        accuracy = (row['verified_claims'] / row['total_claims'] * 100) if row['total_claims'] > 0 else 0
        sources.append(SourceInfo(
            id=row['id'],
            name=row['name'],
            type=row['type'],
            credit_score=row['credit_score'],
            total_claims=row['total_claims'],
            verified_claims=row['verified_claims'],
            refuted_claims=row['refuted_claims'],
            accuracy_rate=accuracy
        ))

    conn.close()
    return sources


@app.get("/api/claims", response_model=List[ClaimInfo])
async def get_claims(limit: int = 50):
    """获取声明列表"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.id, c.text, c.status, c.event_id, s.name as source_name
        FROM claims c
        LEFT JOIN sources s ON c.source_id = s.id
        ORDER BY c.created_at DESC
        LIMIT ?
    """, (limit,))

    claims = []
    for row in cursor.fetchall():
        claims.append(ClaimInfo(
            id=row['id'],
            text=row['text'],
            status=row['status'],
            source_name=row['source_name'] or '未知',
            event_id=row['event_id']
        ))

    conn.close()
    return claims


@app.post("/api/import")
async def import_json_data(data: Dict[str, Any]):
    """
    从 JSON 数据导入到 EKG

    接受格式:
    {
        "sources": [...],
        "events": [...],
        "claims": [...],
        "entities": [...],
        "artifacts": [...],
        "refutations": [...]
    }
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from ekg_import_json import EKGJSONImporter

        importer = EKGJSONImporter(DB_PATH)
        success = importer.import_data(data)
        stats = importer.stats.copy()
        importer.close()

        if success:
            return {
                "status": "success",
                "message": "数据导入成功",
                "stats": stats
            }
        else:
            return {
                "status": "error",
                "message": "数据导入失败",
                "stats": stats
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@app.get("/api/visualize")
async def generate_visualization(type: str, event_id: Optional[str] = None):
    """生成可视化图谱"""
    from ekg_visualization import EKGVisualizer

    visualizer = EKGVisualizer(DB_PATH)

    try:
        if type == "event":
            if not event_id:
                raise HTTPException(status_code=400, detail="事件ID不能为空")
            output = visualizer.visualize_event(event_id, f"ekg_event_{event_id}.html")
        elif type == "all":
            output = visualizer.visualize_all_events()
        elif type == "sources":
            output = visualizer.visualize_sources()
        elif type == "refutations":
            output = visualizer.visualize_refutations()
        else:
            raise HTTPException(status_code=400, detail="不支持的可视化类型")

        visualizer.close()

        # 返回文件路径（相对路径）
        return {"url": f"/{output}", "type": type}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 提供静态文件访问（HTML可视化文件）
@app.get("/{file_path:path}")
async def serve_html(file_path: str):
    """提供HTML文件"""
    if file_path.endswith('.html') and Path(file_path).exists():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="文件不存在")


def main():
    """启动Web服务器"""
    print("=" * 80)
    print("EKG 交互式 Web 演示")
    print("=" * 80)
    print()
    print("🌐 启动服务器...")
    print("📍 访问地址: http://localhost:8000")
    print("⏹  停止服务: Ctrl+C")
    print()
    print("=" * 80)

    # 自动打开浏览器
    webbrowser.open("http://localhost:8000")

    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")


if __name__ == "__main__":
    main()
