# EKG 可视化使用指南

> **一键生成交互式图谱，直观展示事件真相网络**

## 🎨 功能概览

EKG 提供两种可视化方式：

1. **命令行工具** - 快速生成静态图谱 HTML
2. **Web 界面** - 交互式浏览和实时查询

## 📊 可视化类型

### 1. 事件图谱

展示单个事件的完整知识图谱：
- **节点**: 事件、声明、信源
- **关系**: 包含、发布、证伪
- **颜色编码**:
  - 🔴 红色：事件
  - 🟢 绿色：已验证声明
  - 🟠 橙色：已证伪声明
  - 🔵 蓝色：待核实声明
  - 🟢/🟡/🔴 三角：高/中/低信誉信源

### 2. 全局图谱

展示所有事件的关联网络：
- 多事件并列
- 信源跨事件关联
- 证伪关系网络

### 3. 信源网络

展示信源之间的关联：
- 节点大小 = 信誉分
- 边 = 共同关注的事件
- 一目了然的信源质量分布

### 4. 证伪关系图

专注展示真相与谣言的对抗：
- 清晰的证伪链条
- 置信度标注
- 信源对比

## 🚀 快速开始

### 方式一：命令行工具

```bash
# 1. 安装依赖（如果还没安装）
pip install pyvis networkx

# 2. 生成事件图谱
python demos/ekg_visualization.py --event E-001

# 3. 生成全局图谱
python demos/ekg_visualization.py --all

# 4. 生成信源网络
python demos/ekg_visualization.py --sources

# 5. 生成证伪关系图
python demos/ekg_visualization.py --refutations

# 6. 一次生成所有视图
python demos/ekg_visualization.py --all --sources --refutations
```

**输出**: 自动生成 HTML 文件并在浏览器中打开

### 方式二：Web 界面

```bash
# 1. 启动 Web 服务器
python demos/ekg_web_demo.py

# 2. 浏览器自动打开 http://localhost:8000

# 3. 在界面上：
#    - 查看数据统计
#    - 浏览事件/信源/声明列表
#    - 点击按钮生成可视化
#    - 交互式探索图谱
```

## 📖 详细使用

### 命令行参数

```bash
python demos/ekg_visualization.py [选项]

选项:
  --event EVENT_ID    可视化特定事件（如 E-001）
  --all              可视化所有事件
  --sources          可视化信源网络
  --refutations      可视化证伪关系
  --db PATH          指定数据库文件路径（默认: demos/ekg_demo.db）
  --no-open          不自动打开浏览器
  -h, --help         显示帮助信息
```

### 使用示例

#### 示例 1: 调查 OpenAI-AMD 传闻

```bash
# 查看事件 E-001 的图谱
python demos/ekg_visualization.py --event E-001
```

**看到什么**:
- 中心节点：事件 "OpenAI投资AMD传闻"
- 左侧：@TechInsider（低信誉，橙色三角）
- 右侧：SEC官方（中等信誉，黄色三角）
- 证伪箭头：SEC声明 → TechInsider声明

**洞察**: 一眼看出 @TechInsider 发布的传闻被 SEC 证伪

#### 示例 2: 比较所有信源质量

```bash
# 生成信源网络图
python demos/ekg_visualization.py --sources
```

**看到什么**:
- 每个信源是一个三角形节点
- 大小 = 信誉分（20-40）
- 颜色 = 信誉等级
  - 🟢 绿色：70+ 高信誉
  - 🟡 黄色：40-70 中等
  - 🔴 红色：<40 低信誉
- 连线 = 共同关注事件

**洞察**: 快速识别哪些信源经常发布虚假消息

#### 示例 3: 追踪证伪链条

```bash
# 生成证伪关系图
python demos/ekg_visualization.py --refutations
```

**看到什么**:
- 左侧：证伪方声明（绿色）
- 右侧：被证伪声明（橙色）
- 红色虚线箭头：证伪关系 + 置信度

**洞察**: 清晰展示谣言传播与辟谣路径

### Web 界面功能

访问 http://localhost:8000 后：

#### 1. 首页仪表盘

- 📊 **实时统计**
  - 信源数、事件数、声明数
  - 实体数、证伪数、调查数

- 🔘 **快速可视化**
  - 点击按钮生成图谱
  - 自动在新标签打开

#### 2. 事件列表

- 表格展示所有事件
- 列：事件ID、标题、状态、可信度、声明数
- 点击"查看图谱"→ 生成该事件的可视化

#### 3. 信源排行

- 按信誉分排序
- 显示：类型、信誉分、准确率、声明统计
- 颜色编码的信誉等级

#### 4. 声明列表

- 最新 20 条声明
- 显示：内容、信源、事件、状态
- 徽章标识：✓ 已验证 / ✗ 已证伪 / ? 待核实

### API 端点

Web 服务还提供 RESTful API：

```bash
# 获取统计数据
GET /api/stats

# 获取所有事件
GET /api/events

# 获取所有信源
GET /api/sources

# 获取声明列表
GET /api/claims?limit=50

# 生成可视化
GET /api/visualize?type=all
GET /api/visualize?type=event&event_id=E-001
GET /api/visualize?type=sources
GET /api/visualize?type=refutations
```

## 🎨 可视化效果说明

### 节点颜色含义

| 颜色 | 类型 | 含义 |
|------|------|------|
| 🔴 红色盒子 | 事件 | 核心事件节点 |
| 🟢 绿色椭圆 | 声明 | 已验证的声明 |
| 🟠 橙色椭圆 | 声明 | 已证伪的声明 |
| 🔵 蓝色椭圆 | 声明 | 待核实的声明 |
| 🟢 绿色三角 | 信源 | 高信誉信源（≥70）|
| 🟡 黄色三角 | 信源 | 中等信誉（40-70）|
| 🔴 红色三角 | 信源 | 低信誉信源（<40）|
| 🟣 紫色菱形 | 实体 | 人物/组织/地点 |

### 边的类型

| 标签 | 颜色 | 含义 |
|------|------|------|
| "包含" | 灰色实线 | 事件包含声明 |
| "发布" | 深灰实线 | 信源发布声明 |
| "证伪" | 红色虚线 | 声明证伪另一声明 |
| "涉及" | 浅灰实线 | 事件涉及实体 |
| "共同关注" | 浅灰实线 | 信源共同关注事件 |

### 交互操作

生成的 HTML 图谱支持：

- **拖动**: 鼠标拖动节点调整位置
- **缩放**: 鼠标滚轮缩放视图
- **悬停**: 鼠标悬停显示详细信息
- **点击**: 点击节点高亮关联边
- **物理引擎**: 自动调整节点布局避免重叠

## 🔧 高级配置

### 自定义颜色方案

编辑 `demos/ekg_visualization.py`：

```python
class EKGVisualizer:
    COLORS = {
        "event": "#你的颜色",           # 修改事件颜色
        "claim_verified": "#你的颜色",   # 修改已验证声明颜色
        # ... 其他颜色
    }
```

### 自定义物理引擎

在 `visualize_event()` 方法中修改：

```python
net.set_options("""
{
    "physics": {
        "enabled": true,
        "barnesHut": {
            "gravitationalConstant": -8000,  # 调整引力
            "springLength": 200,             # 调整边长
        }
    }
}
""")
```

### 导出为图片

生成的 HTML 支持截图：

1. 在浏览器中打开生成的 HTML
2. 使用浏览器截图工具（如 Chrome DevTools）
3. 或使用在线工具（如 htmlcsstoimage.com）

## 📝 完整工作流程示例

### 场景：调查新闻真伪

```bash
# 步骤 1: 运行 EKG Demo 生成数据
python demos/ekg_demo.py

# 步骤 2: 查看数据库内容
python demos/view_ekg_data.py

# 步骤 3: 可视化特定事件
python demos/ekg_visualization.py --event E-001

# 步骤 4: 分析信源质量
python demos/ekg_visualization.py --sources

# 步骤 5: 追踪证伪关系
python demos/ekg_visualization.py --refutations

# 步骤 6: 启动 Web 界面进行交互探索
python demos/ekg_web_demo.py
```

### 场景：演示展示

```bash
# 方案 1: 命令行演示（适合技术展示）
python demos/ekg_visualization.py --all --sources --refutations
# 生成3个HTML文件，逐个展示

# 方案 2: Web 界面演示（适合产品展示）
python demos/ekg_web_demo.py
# 访问 http://localhost:8000，实时交互
```

## ❓ 常见问题

### Q1: 可视化显示"no such column"错误？

**原因**: 数据库结构不匹配

**解决**:
```bash
# 重新生成数据库
rm demos/ekg_demo.db
python demos/ekg_demo.py
```

### Q2: 浏览器没有自动打开？

**解决**:
```bash
# 手动打开生成的 HTML 文件
open ekg_event.html  # macOS
xdg-open ekg_event.html  # Linux
start ekg_event.html  # Windows

# 或使用 --no-open 选项手动控制
python demos/ekg_visualization.py --event E-001 --no-open
```

### Q3: Web 界面无法访问？

**检查**:
```bash
# 1. 确认端口没有被占用
lsof -i :8000

# 2. 尝试其他端口
# 编辑 ekg_web_demo.py 最后一行
uvicorn.run(app, host="0.0.0.0", port=8080)  # 改为 8080
```

### Q4: 图谱太大，节点重叠？

**解决**:

1. 调整物理引擎参数（增大 springLength）
2. 手动拖动节点调整布局
3. 缩小视图范围

### Q5: 如何导出高清图片？

**方法 1**: 浏览器截图
```bash
# Chrome DevTools
1. F12 打开开发者工具
2. Ctrl+Shift+P
3. 输入 "screenshot"
4. 选择 "Capture full size screenshot"
```

**方法 2**: 使用在线工具
- https://htmlcsstoimage.com/
- 上传 HTML 文件
- 导出为 PNG/JPG

### Q6: 可以集成到主项目吗？

**可以！** 参考示例：

```python
from demos.ekg_visualization import EKGVisualizer

# 在你的代码中
visualizer = EKGVisualizer("path/to/your.db")
html_path = visualizer.visualize_event("E-001", "output.html")
visualizer.close()

print(f"图谱已生成: {html_path}")
```

## 🎯 最佳实践

### 1. 调查分析

- 先用 `--all` 了解全局
- 再用 `--event` 深入单个事件
- 最后用 `--sources` 评估信源质量

### 2. 演示展示

- Web 界面更适合非技术观众
- 命令行工具更适合开发调试
- 提前生成 HTML 可离线展示

### 3. 数据探索

- 结合 `view_ekg_data.py` 查看原始数据
- 用可视化发现模式和异常
- 追踪证伪链条找到真相来源

## 📚 相关文档

- [EKG_QUICKSTART.md](EKG_QUICKSTART.md) - 3分钟快速开始
- [docs/EKG_DEMO.md](docs/EKG_DEMO.md) - 完整测试文档
- [docs/EKG_GUIDE.md](docs/EKG_GUIDE.md) - 使用指南
- [docs/EKG_TECHNICAL.md](docs/EKG_TECHNICAL.md) - 技术实现

## 🎉 总结

EKG 可视化让真相网络一目了然：

✅ **4种视图** - 事件、全局、信源、证伪
✅ **2种方式** - 命令行 + Web 界面
✅ **交互式** - 拖动、缩放、悬停
✅ **颜色编码** - 快速识别信誉等级
✅ **一键生成** - 自动打开浏览器

开始可视化你的真相网络：

```bash
python demos/ekg_web_demo.py
```

---

**让假新闻无处遁形！🔍**
