#!/usr/bin/env python3
"""
EKG 图谱可视化工具

生成交互式 HTML 图谱，展示事件知识图谱的结构和关系。

运行方式:
    # 可视化特定事件
    python demos/ekg_visualization.py --event E-001

    # 可视化所有事件
    python demos/ekg_visualization.py --all

    # 可视化信源网络
    python demos/ekg_visualization.py --sources

    # 可视化证伪关系
    python demos/ekg_visualization.py --refutations

生成的 HTML 文件会自动在浏览器中打开。
"""
import sys
import sqlite3
import argparse
import webbrowser
from pathlib import Path
from typing import Dict, List, Any, Optional
from pyvis.network import Network
import networkx as nx

DB_PATH = "demos/ekg_demo.db"


class EKGVisualizer:
    """EKG 图谱可视化器"""

    # 配色方案
    COLORS = {
        "event": "#FF6B6B",           # 红色 - 事件
        "claim_verified": "#51CF66",   # 绿色 - 已验证声明
        "claim_refuted": "#FFA94D",    # 橙色 - 已证伪声明
        "claim_pending": "#74C0FC",    # 蓝色 - 待核实声明
        "source_high": "#2ECC71",      # 深绿 - 高信誉信源
        "source_medium": "#FFD93D",    # 黄色 - 中等信誉信源
        "source_low": "#E74C3C",       # 深红 - 低信誉信源
        "entity": "#BE4BDB",           # 紫色 - 实体
    }

    def __init__(self, db_path: str = DB_PATH):
        """初始化可视化器"""
        if not Path(db_path).exists():
            raise FileNotFoundError(f"数据库文件不存在: {db_path}\n请先运行: python demos/ekg_demo.py")

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # 使用字典格式返回

    def visualize_event(self, event_id: str, output_file: str = "ekg_event.html") -> str:
        """
        可视化特定事件的图谱

        Args:
            event_id: 事件ID
            output_file: 输出HTML文件名

        Returns:
            生成的HTML文件路径
        """
        # 创建网络图
        net = Network(
            height="800px",
            width="100%",
            bgcolor="#ffffff",
            font_color="#000000",
            directed=True,
            notebook=False
        )

        # 配置物理引擎
        net.set_options("""
        {
            "physics": {
                "enabled": true,
                "barnesHut": {
                    "gravitationalConstant": -8000,
                    "centralGravity": 0.3,
                    "springLength": 200,
                    "springConstant": 0.04
                },
                "minVelocity": 0.75
            },
            "nodes": {
                "font": {"size": 14}
            },
            "edges": {
                "arrows": {"to": {"enabled": true, "scaleFactor": 0.5}},
                "smooth": {"type": "continuous"}
            }
        }
        """)

        cursor = self.conn.cursor()

        # 1. 获取事件信息
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        event = cursor.fetchone()

        if not event:
            raise ValueError(f"事件不存在: {event_id}")

        # 添加事件节点
        event_label = f"事件: {event['title']}\n状态: {event['status']}"
        if event['credibility_score']:
            event_label += f"\n可信度: {event['credibility_score']:.1f}"

        net.add_node(
            f"event_{event['id']}",
            label=event_label,
            color=self.COLORS['event'],
            size=40,
            shape="box",
            title=f"ID: {event['id']}"
        )

        # 2. 获取相关声明
        cursor.execute("""
            SELECT c.*, s.name as source_name, s.credit_score, s.type as source_type
            FROM claims c
            LEFT JOIN sources s ON c.source_id = s.id
            WHERE c.event_id = ?
        """, (event_id,))

        claims = cursor.fetchall()
        source_ids = set()

        for claim in claims:
            claim_id = f"claim_{claim['id']}"

            # 根据状态选择颜色
            if claim['status'] == 'verified':
                color = self.COLORS['claim_verified']
                status_text = "✓ 已验证"
            elif claim['status'] == 'refuted':
                color = self.COLORS['claim_refuted']
                status_text = "✗ 已证伪"
            else:
                color = self.COLORS['claim_pending']
                status_text = "? 待核实"

            # 截断文本
            text = claim['text'][:50] + "..." if len(claim['text']) > 50 else claim['text']

            # 添加声明节点
            net.add_node(
                claim_id,
                label=f"{status_text}\n{text}",
                color=color,
                size=25,
                shape="ellipse",
                title=claim['text']  # 完整文本作为悬浮提示
            )

            # 事件 -> 声明
            net.add_edge(f"event_{event['id']}", claim_id, label="包含", color="#888888")

            # 添加信源
            if claim['source_id']:
                source_ids.add(claim['source_id'])
                source_id = f"source_{claim['source_id']}"

                # 根据信誉分选择颜色
                score = claim['credit_score']
                if score >= 70:
                    source_color = self.COLORS['source_high']
                elif score >= 40:
                    source_color = self.COLORS['source_medium']
                else:
                    source_color = self.COLORS['source_low']

                # 添加信源节点（如果还没有）
                if source_id not in [node['id'] for node in net.nodes]:
                    net.add_node(
                        source_id,
                        label=f"📰 {claim['source_name']}\n信誉分: {score}",
                        color=source_color,
                        size=30,
                        shape="triangle",
                        title=f"类型: {claim['source_type']}\n信誉分: {score}"
                    )

                # 信源 -> 声明
                net.add_edge(source_id, claim_id, label="发布", color="#666666")

        # 3. 获取证伪关系
        cursor.execute("""
            SELECT cr.*,
                   c1.text as refuting_text,
                   c2.text as refuted_text
            FROM claim_refutations cr
            LEFT JOIN claims c1 ON cr.refuting_claim_id = c1.id
            LEFT JOIN claims c2 ON cr.refuted_claim_id = c2.id
            WHERE c1.event_id = ? OR c2.event_id = ?
        """, (event_id, event_id))

        refutations = cursor.fetchall()
        for ref in refutations:
            net.add_edge(
                f"claim_{ref['refuting_claim_id']}",
                f"claim_{ref['refuted_claim_id']}",
                label=f"证伪 ({ref['confidence']:.0%})",
                color="#E74C3C",
                width=2,
                dashes=True
            )

        # 4. 从声明中提取实体（实体信息存储在claims.entities JSON字段中）
        # 注意：Entity 表是独立的字典表，不直接关联事件
        # 这里我们可以从 claims 的 entities 字段中提取实体信息
        entity_names = set()
        for claim in claims:
            # 如果 claim 中有 entities 信息，提取出来
            # 由于当前demo中可能没有填充entities字段，这里先跳过
            pass

        # 生成HTML
        output_path = Path(output_file)
        net.save_graph(str(output_path))

        print(f"✅ 事件图谱已生成: {output_path}")
        print(f"   事件: {event['title']}")
        print(f"   节点数: {len(net.nodes)}")
        print(f"   边数: {len(net.edges)}")

        return str(output_path)

    def visualize_all_events(self, output_file: str = "ekg_all_events.html") -> str:
        """
        可视化所有事件的全局图谱

        Args:
            output_file: 输出HTML文件名

        Returns:
            生成的HTML文件路径
        """
        net = Network(
            height="900px",
            width="100%",
            bgcolor="#ffffff",
            font_color="#000000",
            directed=True,
            notebook=False
        )

        net.set_options("""
        {
            "physics": {
                "enabled": true,
                "barnesHut": {
                    "gravitationalConstant": -10000,
                    "centralGravity": 0.2,
                    "springLength": 250
                }
            }
        }
        """)

        cursor = self.conn.cursor()

        # 获取所有事件
        cursor.execute("SELECT * FROM events")
        events = cursor.fetchall()

        for event in events:
            event_id = f"event_{event['id']}"
            label = f"📋 {event['title'][:30]}..."
            net.add_node(event_id, label=label, color=self.COLORS['event'], size=35, shape="box")

        # 获取所有声明和信源
        cursor.execute("""
            SELECT c.*, s.name as source_name, s.credit_score
            FROM claims c
            LEFT JOIN sources s ON c.source_id = s.id
        """)
        claims = cursor.fetchall()

        # 第一轮：收集所有信源信息
        sources = {}
        for claim in claims:
            if claim['source_id']:
                if claim['source_id'] not in sources:
                    sources[claim['source_id']] = {
                        'name': claim['source_name'],
                        'score': claim['credit_score']
                    }

        # 第二轮：创建信源节点
        for source_id, source_info in sources.items():
            score = source_info['score']
            if score >= 70:
                color = self.COLORS['source_high']
            elif score >= 40:
                color = self.COLORS['source_medium']
            else:
                color = self.COLORS['source_low']

            net.add_node(
                f"source_{source_id}",
                label=f"📰 {source_info['name']}\n({score})",
                color=color,
                size=25,
                shape="triangle"
            )

        # 第三轮：创建声明节点和边
        for claim in claims:
            claim_id = f"claim_{claim['id']}"

            # 添加声明节点
            color = {
                'verified': self.COLORS['claim_verified'],
                'refuted': self.COLORS['claim_refuted'],
                'pending': self.COLORS['claim_pending']
            }.get(claim['status'], self.COLORS['claim_pending'])

            text = claim['text'][:30] + "..."
            net.add_node(claim_id, label=text, color=color, size=15)

            # 事件 -> 声明
            if claim['event_id']:
                net.add_edge(f"event_{claim['event_id']}", claim_id, color="#888888")

            # 信源 -> 声明
            if claim['source_id']:
                net.add_edge(f"source_{claim['source_id']}", claim_id, color="#666666")

        # 添加证伪关系
        cursor.execute("SELECT * FROM claim_refutations")
        for ref in cursor.fetchall():
            net.add_edge(
                f"claim_{ref['refuting_claim_id']}",
                f"claim_{ref['refuted_claim_id']}",
                label="证伪",
                color="#E74C3C",
                width=2,
                dashes=True
            )

        output_path = Path(output_file)
        net.save_graph(str(output_path))

        print(f"✅ 全局图谱已生成: {output_path}")
        print(f"   事件数: {len(events)}")
        print(f"   信源数: {len(sources)}")
        print(f"   声明数: {len(claims)}")

        return str(output_path)

    def visualize_sources(self, output_file: str = "ekg_sources.html") -> str:
        """
        可视化信源网络和信誉分布

        Args:
            output_file: 输出HTML文件名

        Returns:
            生成的HTML文件路径
        """
        net = Network(
            height="800px",
            width="100%",
            bgcolor="#ffffff",
            font_color="#000000",
            directed=True,
            notebook=False
        )

        cursor = self.conn.cursor()

        # 获取所有信源
        cursor.execute("""
            SELECT id, name, type, credit_score, total_claims, verified_claims, refuted_claims
            FROM sources
            ORDER BY credit_score DESC
        """)
        sources = cursor.fetchall()

        for source in sources:
            source_id = f"source_{source['id']}"

            # 根据信誉分确定大小和颜色
            score = source['credit_score']
            size = 20 + (score / 5)  # 20-40

            if score >= 70:
                color = self.COLORS['source_high']
            elif score >= 40:
                color = self.COLORS['source_medium']
            else:
                color = self.COLORS['source_low']

            accuracy = (source['verified_claims'] / source['total_claims'] * 100) if source['total_claims'] > 0 else 0

            label = f"📰 {source['name']}\n"
            label += f"信誉: {score}\n"
            label += f"准确率: {accuracy:.0f}%\n"
            label += f"声明数: {source['total_claims']}"

            net.add_node(
                source_id,
                label=label,
                color=color,
                size=size,
                shape="triangle",
                title=f"类型: {source['type']}\n已验证: {source['verified_claims']}\n已证伪: {source['refuted_claims']}"
            )

        # 获取信源之间的关联（通过同一事件）
        cursor.execute("""
            SELECT DISTINCT
                c1.source_id as source1,
                c2.source_id as source2,
                c1.event_id
            FROM claims c1
            JOIN claims c2 ON c1.event_id = c2.event_id AND c1.source_id < c2.source_id
            WHERE c1.source_id IS NOT NULL AND c2.source_id IS NOT NULL
        """)

        connections = cursor.fetchall()
        for conn in connections:
            net.add_edge(
                f"source_{conn['source1']}",
                f"source_{conn['source2']}",
                label="共同关注",
                color="#CCCCCC",
                width=1
            )

        output_path = Path(output_file)
        net.save_graph(str(output_path))

        print(f"✅ 信源网络已生成: {output_path}")
        print(f"   信源数: {len(sources)}")

        return str(output_path)

    def visualize_refutations(self, output_file: str = "ekg_refutations.html") -> str:
        """
        可视化证伪关系网络

        Args:
            output_file: 输出HTML文件名

        Returns:
            生成的HTML文件路径
        """
        net = Network(
            height="800px",
            width="100%",
            bgcolor="#ffffff",
            font_color="#000000",
            directed=True,
            notebook=False
        )

        cursor = self.conn.cursor()

        # 获取所有证伪关系
        cursor.execute("""
            SELECT cr.*,
                   c1.text as refuting_text,
                   c1.status as refuting_status,
                   c2.text as refuted_text,
                   c2.status as refuted_status,
                   s1.name as refuting_source,
                   s2.name as refuted_source
            FROM claim_refutations cr
            LEFT JOIN claims c1 ON cr.refuting_claim_id = c1.id
            LEFT JOIN claims c2 ON cr.refuted_claim_id = c2.id
            LEFT JOIN sources s1 ON c1.source_id = s1.id
            LEFT JOIN sources s2 ON c2.source_id = s2.id
        """)

        refutations = cursor.fetchall()

        if not refutations:
            print("⚠️  数据库中没有证伪关系")
            return None

        for ref in refutations:
            # 添加证伪方声明
            refuting_id = f"claim_{ref['refuting_claim_id']}"
            refuting_text = ref['refuting_text'][:40] + "..."
            net.add_node(
                refuting_id,
                label=f"✓ {refuting_text}\n({ref['refuting_source']})",
                color=self.COLORS['claim_verified'],
                size=25,
                shape="box",
                title=ref['refuting_text']
            )

            # 添加被证伪方声明
            refuted_id = f"claim_{ref['refuted_claim_id']}"
            refuted_text = ref['refuted_text'][:40] + "..."
            net.add_node(
                refuted_id,
                label=f"✗ {refuted_text}\n({ref['refuted_source']})",
                color=self.COLORS['claim_refuted'],
                size=25,
                shape="box",
                title=ref['refuted_text']
            )

            # 添加证伪关系边
            net.add_edge(
                refuting_id,
                refuted_id,
                label=f"证伪 ({ref['confidence']:.0%})",
                color="#E74C3C",
                width=3,
                arrows={"to": {"enabled": True, "scaleFactor": 1}}
            )

        output_path = Path(output_file)
        net.save_graph(str(output_path))

        print(f"✅ 证伪关系图已生成: {output_path}")
        print(f"   证伪关系数: {len(refutations)}")

        return str(output_path)

    def close(self):
        """关闭数据库连接"""
        self.conn.close()


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="EKG 图谱可视化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 可视化特定事件
  python demos/ekg_visualization.py --event E-001

  # 可视化所有事件
  python demos/ekg_visualization.py --all

  # 可视化信源网络
  python demos/ekg_visualization.py --sources

  # 可视化证伪关系
  python demos/ekg_visualization.py --refutations

  # 生成所有视图
  python demos/ekg_visualization.py --all --sources --refutations
        """
    )

    parser.add_argument("--event", type=str, help="可视化特定事件（事件ID）")
    parser.add_argument("--all", action="store_true", help="可视化所有事件")
    parser.add_argument("--sources", action="store_true", help="可视化信源网络")
    parser.add_argument("--refutations", action="store_true", help="可视化证伪关系")
    parser.add_argument("--db", type=str, default=DB_PATH, help="数据库文件路径")
    parser.add_argument("--no-open", action="store_true", help="不自动打开浏览器")

    args = parser.parse_args()

    # 如果没有指定任何选项，显示帮助
    if not any([args.event, args.all, args.sources, args.refutations]):
        parser.print_help()
        sys.exit(0)

    try:
        visualizer = EKGVisualizer(args.db)
        generated_files = []

        print("=" * 80)
        print("EKG 图谱可视化")
        print("=" * 80)

        # 可视化特定事件
        if args.event:
            output = visualizer.visualize_event(args.event)
            generated_files.append(output)

        # 可视化所有事件
        if args.all:
            output = visualizer.visualize_all_events()
            generated_files.append(output)

        # 可视化信源网络
        if args.sources:
            output = visualizer.visualize_sources()
            generated_files.append(output)

        # 可视化证伪关系
        if args.refutations:
            output = visualizer.visualize_refutations()
            if output:
                generated_files.append(output)

        visualizer.close()

        # 打印总结
        print("\n" + "=" * 80)
        print(f"✅ 共生成 {len(generated_files)} 个可视化文件")
        for f in generated_files:
            print(f"   - {f}")
        print("=" * 80)

        # 自动打开第一个文件
        if generated_files and not args.no_open:
            print(f"\n🌐 正在打开浏览器...")
            webbrowser.open(f"file://{Path(generated_files[0]).absolute()}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
