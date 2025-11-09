#!/usr/bin/env python3
"""
EKG (事件知识图谱) 独立演示脚本

演示 EKG 的核心功能：
1. 创建信源、事件、声明
2. 信源信誉分动态更新（飞轮机制）
3. 查询信源历史声誉
4. 计算事件可信度
5. 生成事件图谱（可视化数据）

运行方式：
    python demos/ekg_demo.py
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.ekg.models import Base, SourceType, EventStatus, ClaimStatus
from src.ekg.repository import EKGRepository
from src.ekg.graph_ops import EKGGraphOps


class EKGDemo:
    """EKG 演示类"""

    def __init__(self, db_path: str = "demos/ekg_demo.db"):
        """初始化演示环境"""
        self.db_path = db_path
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            echo=False  # 设为 True 可以看到 SQL 语句
        )

        # 创建表
        Base.metadata.drop_all(self.engine)  # 每次运行清空数据
        Base.metadata.create_all(self.engine)

        # 创建 session
        SessionLocal = sessionmaker(bind=self.engine)
        self.session = SessionLocal()

        # 创建 repository 和 graph_ops
        self.repo = EKGRepository(self.session)
        self.graph = EKGGraphOps(self.repo)

        print(f"✅ EKG 演示环境初始化完成")
        print(f"📁 数据库文件: {db_path}\n")

    def scenario_1_basic_operations(self):
        """场景1：基础操作 - 创建信源、事件、声明"""
        print("=" * 80)
        print("场景 1: 基础操作 - 创建信源、事件、声明")
        print("=" * 80)

        # 1. 创建信源
        print("\n📌 步骤 1: 创建信源")
        source1 = self.repo.find_or_create_source(
            name="@TechInsider",
            source_type=SourceType.SOCIAL_MEDIA,
            url="https://twitter.com/techinsider",
            description="科技领域自媒体账号"
        )
        print(f"   创建信源: {source1.name}")
        print(f"   类型: {source1.type.value}")
        print(f"   初始信誉分: {source1.credit_score}")

        source2 = self.repo.find_or_create_source(
            name="SEC官方",
            source_type=SourceType.OFFICIAL_MEDIA,
            url="https://www.sec.gov",
            description="美国证券交易委员会"
        )
        print(f"   创建信源: {source2.name}")
        print(f"   类型: {source2.type.value}")
        print(f"   初始信誉分: {source2.credit_score}")

        # 2. 创建事件
        print("\n📌 步骤 2: 创建事件")
        event = self.repo.create_event(
            event_id="E-001",
            title="OpenAI投资AMD传闻",
            description="网络流传OpenAI将投资AMD 1000亿美元",
            status=EventStatus.DEVELOPING,
            tags=["科技", "金融", "投资"]
        )
        print(f"   创建事件: {event.id}")
        print(f"   标题: {event.title}")
        print(f"   状态: {event.status.value}")

        # 3. 创建声明
        print("\n📌 步骤 3: 创建声明")
        claim1 = self.repo.create_claim(
            text="OpenAI将投资AMD 1000亿美元",
            source_id=source1.id,
            event_id=event.id,
            claim_type="financial",
            entities=["OpenAI", "AMD"]
        )
        print(f"   声明 1: {claim1.text}")
        print(f"   信源: {source1.name}")
        print(f"   状态: {claim1.status.value}")

        claim2 = self.repo.create_claim(
            text="SEC未发现OpenAI-AMD交易披露文件",
            source_id=source2.id,
            event_id=event.id,
            claim_type="verification",
            verification_result={"source": "SEC EDGAR", "finding": "无相关文件"}
        )
        print(f"   声明 2: {claim2.text}")
        print(f"   信源: {source2.name}")

        # 4. 创建证伪关系
        print("\n📌 步骤 4: 创建证伪关系")
        refutation = self.repo.create_claim_refutation(
            refuting_claim_id=claim2.id,
            refuted_claim_id=claim1.id,
            confidence=0.9,
            evidence=[{"source": "SEC EDGAR", "url": "https://www.sec.gov/..."}]
        )
        print(f"   声明 2 证伪了 声明 1")
        print(f"   置信度: {refutation.confidence}")

        return event.id, source1.id, source2.id

    def scenario_2_flywheel_mechanism(self, source_id: int):
        """场景2：飞轮机制 - 信源信誉分动态更新"""
        print("\n" + "=" * 80)
        print("场景 2: 飞轮机制 - 信源信誉分动态更新")
        print("=" * 80)

        # 查询初始信誉分
        stats_before = self.repo.get_source_statistics(source_id)

        print("\n📌 初始状态:")
        print(f"   信源ID: {source_id}")
        print(f"   信誉分: {stats_before['credit_score']}")
        print(f"   历史声明数: {stats_before['total_claims']}")
        print(f"   准确率: {stats_before['accuracy_rate']:.1f}%")

        # 模拟多次调查，信誉分下降
        print("\n📌 模拟调查场景:")
        print("   场景: @TechInsider 连续发布3条虚假消息")

        for i in range(3):
            # 更新声明状态为"已证伪"
            claim = self.repo.create_claim(
                text=f"虚假消息 {i+1}",
                source_id=source_id,
                status=ClaimStatus.REFUTED
            )

            # 更新信誉分（飞轮机制）
            self.repo.update_source_credit_score(source_id, -5)

            stats = self.repo.get_source_statistics(source_id)
            print(f"   第 {i+1} 次: 信誉分 {stats['credit_score']} "
                  f"(准确率 {stats['accuracy_rate']:.1f}%)")

        # 查询最终信誉分
        stats_after = self.repo.get_source_statistics(source_id)

        print("\n📌 最终状态:")
        print(f"   信誉分: {stats_before['credit_score']} → {stats_after['credit_score']}")
        print(f"   准确率: {stats_before['accuracy_rate']:.1f}% → {stats_after['accuracy_rate']:.1f}%")
        print(f"   总声明数: {stats_after['total_claims']}")
        print(f"   已证伪: {stats_after['refuted_claims']}")

        print("\n💡 飞轮效应:")
        print(f"   经过 {stats_after['total_claims']} 次调查，系统已'记住'该信源不可靠")
        print(f"   下次遇到该信源时，可毫秒级预警！")

    def scenario_3_source_reputation_query(self, source_id: int):
        """场景3：查询信源声誉（飞轮的"读"操作）"""
        print("\n" + "=" * 80)
        print("场景 3: 查询信源声誉（毫秒级预警）")
        print("=" * 80)

        # 模拟新调查开始前的查询
        print("\n📌 场景: 用户提交新的可疑新闻")
        print("   新闻来源: @TechInsider")
        print("   内容: 'Google收购Adobe'")

        print("\n📌 系统立即查询 EKG（毫秒级）:")

        # 查询信源声誉
        reputation = self.repo.query_source_reputation("@TechInsider")

        if reputation:
            print(f"   ✅ 找到历史记录!")
            print(f"   信源: {reputation['name']}")
            print(f"   类型: {reputation['type']}")
            print(f"   信誉分: {reputation['credit_score']}")
            print(f"   历史准确率: {reputation['statistics']['accuracy_rate']:.1f}%")
            print(f"   最后更新: {reputation['last_updated']}")

            # 生成预警
            score = reputation['credit_score']
            if score < 30:
                level = "🔴 高度存疑"
            elif score < 60:
                level = "🟡 需要核查"
            else:
                level = "🟢 相对可信"

            print(f"\n   预警等级: {level}")
            print(f"   建议: 该信源历史准确率仅 {reputation['statistics']['accuracy_rate']:.1f}%，"
                  f"建议谨慎对待")
        else:
            print("   ⚠️  未找到历史记录，这是新信源")

    def scenario_4_event_credibility(self, event_id: str):
        """场景4：计算事件整体可信度"""
        print("\n" + "=" * 80)
        print("场景 4: 计算事件整体可信度")
        print("=" * 80)

        print(f"\n📌 分析事件: {event_id}")

        # 计算事件可信度
        credibility = self.graph.calculate_event_credibility(event_id)

        print(f"\n   可信度评分: {credibility['credibility_score']:.1f}/100")
        print(f"   已验证声明: {credibility['verified_claims']}")
        print(f"   已证伪声明: {credibility['refuted_claims']}")
        print(f"   总声明数: {credibility['total_claims']}")
        print(f"   置信度: {credibility['confidence']}")

        # 评级
        score = credibility['credibility_score']
        if score >= 70:
            rating = "✅ 高度可信"
        elif score >= 40:
            rating = "⚠️  存疑"
        else:
            rating = "❌ 不可信"

        print(f"\n   综合评级: {rating}")

    def scenario_5_event_graph_visualization(self, event_id: str):
        """场景5：生成事件图谱（用于可视化）"""
        print("\n" + "=" * 80)
        print("场景 5: 生成事件图谱数据")
        print("=" * 80)

        print(f"\n📌 生成事件 {event_id} 的图谱数据")

        # 生成图谱
        graph_data = self.graph.generate_event_graph(event_id)

        print(f"\n   节点数: {len(graph_data['nodes'])}")
        print(f"   边数: {len(graph_data['edges'])}")

        print("\n   节点列表:")
        for node in graph_data['nodes']:
            print(f"      - {node['type']}: {node['label']}")
            if node['type'] == 'source':
                print(f"        信誉分: {node['credit_score']}")
            elif node['type'] == 'claim':
                print(f"        状态: {node['status']}")

        print("\n   关系列表:")
        for edge in graph_data['edges']:
            print(f"      - {edge['from']} --[{edge['type']}]--> {edge['to']}")

        print("\n   💡 可用于前端可视化（如 D3.js、Cytoscape.js）")

        return graph_data

    def scenario_6_trending_sources(self):
        """场景6：获取热门信源"""
        print("\n" + "=" * 80)
        print("场景 6: 获取热门信源排行")
        print("=" * 80)

        trending = self.repo.get_trending_sources(limit=5)

        print("\n📌 活跃度排行（按声明数）:")
        for i, source in enumerate(trending, 1):
            print(f"   {i}. {source['name']}")
            print(f"      类型: {source['type']}")
            print(f"      信誉分: {source['credit_score']}")
            print(f"      声明数: {source['total_claims']}")

    def scenario_7_complete_investigation(self):
        """场景7：完整调查流程演示"""
        print("\n" + "=" * 80)
        print("场景 7: 完整调查流程演示")
        print("=" * 80)

        print("\n📌 用户提交: 'SpaceX宣布火星移民计划'")

        # 1. 创建事件
        event = self.repo.create_event(
            event_id="E-002",
            title="SpaceX火星移民计划",
            description="网传SpaceX将启动火星移民计划",
            status=EventStatus.DEVELOPING
        )
        print(f"\n✅ 步骤1: 创建事件 {event.id}")

        # 2. 溯源 - 找到原始信源
        source = self.repo.find_or_create_source(
            name="@SpaceNewsDaily",
            source_type=SourceType.SOCIAL_MEDIA
        )
        print(f"✅ 步骤2: 溯源完成，原始信源: {source.name}")

        # 3. 查询EKG - 检查信源历史
        reputation = self.repo.query_source_reputation(source.name)
        if reputation:
            print(f"✅ 步骤3: EKG查询 - 信誉分 {reputation['credit_score']}")
        else:
            print(f"✅ 步骤3: EKG查询 - 新信源，信誉分 {source.credit_score}")

        # 4. 创建声明
        claim = self.repo.create_claim(
            text="SpaceX将于2025年启动火星移民",
            source_id=source.id,
            event_id=event.id,
            status=ClaimStatus.PENDING
        )
        print(f"✅ 步骤4: 提取声明 - '{claim.text[:30]}...'")

        # 5. 核查 - 假设找到官方辟谣
        official_source = self.repo.find_or_create_source(
            name="SpaceX官方",
            source_type=SourceType.OFFICIAL_MEDIA
        )

        refute_claim = self.repo.create_claim(
            text="SpaceX官方辟谣：无此计划",
            source_id=official_source.id,
            event_id=event.id,
            status=ClaimStatus.VERIFIED
        )
        print(f"✅ 步骤5: 核查完成 - 发现官方辟谣")

        # 6. 更新原声明状态
        self.repo.update_claim_status(claim.id, ClaimStatus.REFUTED)
        print(f"✅ 步骤6: 更新声明状态为'已证伪'")

        # 7. 更新信源信誉分（飞轮机制）
        self.repo.update_source_credit_score(source.id, -5)
        print(f"✅ 步骤7: 更新信源信誉分 -5")

        # 8. 更新事件状态
        credibility = self.graph.calculate_event_credibility(event.id)
        self.repo.update_event_status(
            event.id,
            EventStatus.REFUTED,
            credibility['credibility_score']
        )
        print(f"✅ 步骤8: 更新事件状态为'已证伪'，可信度 {credibility['credibility_score']:.1f}")

        # 9. 保存调查历史
        investigation = self.repo.save_investigation_result(
            investigation_id="INV-002",
            event_id=event.id,
            report={
                "title": event.title,
                "conclusion": "已证伪",
                "credibility": credibility['credibility_score']
            },
            credibility_score=credibility['credibility_score'],
            started_at=datetime.now()
        )
        print(f"✅ 步骤9: 保存调查历史 {investigation.investigation_id}")

        print(f"\n🎯 调查完成！下次遇到 {source.name} 时，系统会立即预警。")

    def print_summary(self):
        """打印汇总统计"""
        print("\n" + "=" * 80)
        print("📊 EKG 数据汇总")
        print("=" * 80)

        from src.ekg.models import Source, Event, Claim, ClaimRefutation, InvestigationHistory

        source_count = self.session.query(Source).count()
        event_count = self.session.query(Event).count()
        claim_count = self.session.query(Claim).count()
        refutation_count = self.session.query(ClaimRefutation).count()
        investigation_count = self.session.query(InvestigationHistory).count()

        print(f"\n   信源数: {source_count}")
        print(f"   事件数: {event_count}")
        print(f"   声明数: {claim_count}")
        print(f"   证伪关系数: {refutation_count}")
        print(f"   调查历史数: {investigation_count}")

        print("\n" + "=" * 80)

    def run_all_scenarios(self):
        """运行所有演示场景"""
        print("\n" + "🚀" * 40)
        print("EKG (事件知识图谱) 完整演示")
        print("🚀" * 40 + "\n")

        # 场景1: 基础操作
        event_id, source1_id, source2_id = self.scenario_1_basic_operations()

        # 场景2: 飞轮机制
        self.scenario_2_flywheel_mechanism(source1_id)

        # 场景3: 信源声誉查询
        self.scenario_3_source_reputation_query(source1_id)

        # 场景4: 事件可信度
        self.scenario_4_event_credibility(event_id)

        # 场景5: 事件图谱
        graph_data = self.scenario_5_event_graph_visualization(event_id)

        # 场景6: 热门信源
        self.scenario_6_trending_sources()

        # 场景7: 完整调查流程
        self.scenario_7_complete_investigation()

        # 汇总
        self.print_summary()

        print("\n✅ 所有演示场景运行完成！")
        print(f"📁 数据已保存到: {self.db_path}")
        print("💡 可以用 SQLite 工具打开数据库查看详细数据\n")


def main():
    """主函数"""
    demo = EKGDemo()
    demo.run_all_scenarios()


if __name__ == "__main__":
    main()
