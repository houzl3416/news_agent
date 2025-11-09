#!/usr/bin/env python3
"""
EKG JSON 数据导入工具

支持从 JSON 文件导入事件、声明、信源等数据到 EKG 数据库。

运行方式:
    # 从单个 JSON 文件导入
    python demos/ekg_import_json.py --file data.json

    # 从目录批量导入所有 JSON 文件
    python demos/ekg_import_json.py --dir ./data/

    # 指定数据库路径
    python demos/ekg_import_json.py --file data.json --db my_ekg.db

    # 显示 JSON 格式示例
    python demos/ekg_import_json.py --example
"""
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ekg.repository import EKGRepository
from src.ekg.models import SourceType, EventStatus, ClaimStatus, Base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


class EKGJSONImporter:
    """EKG JSON 数据导入器"""

    def __init__(self, db_path: str = "demos/ekg_demo.db"):
        """初始化导入器"""
        self.db_path = db_path

        # 直接创建 SQLAlchemy 引擎和会话
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )

        # 创建表（如果不存在）
        Base.metadata.create_all(bind=self.engine)

        # 创建会话
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = SessionLocal()
        self.repo = EKGRepository(self.session)
        self.stats = {
            "sources": 0,
            "events": 0,
            "claims": 0,
            "entities": 0,
            "artifacts": 0,
            "refutations": 0,
            "errors": 0
        }

    def import_from_file(self, file_path: str) -> bool:
        """
        从 JSON 文件导入数据

        Args:
            file_path: JSON 文件路径

        Returns:
            是否导入成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"📂 正在导入: {file_path}")
            return self.import_data(data)

        except FileNotFoundError:
            print(f"❌ 文件不存在: {file_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ JSON 格式错误: {e}")
            return False
        except Exception as e:
            print(f"❌ 导入失败: {e}")
            return False

    def import_from_directory(self, dir_path: str) -> int:
        """
        从目录批量导入所有 JSON 文件

        Args:
            dir_path: 目录路径

        Returns:
            成功导入的文件数
        """
        directory = Path(dir_path)
        if not directory.exists() or not directory.is_dir():
            print(f"❌ 目录不存在: {dir_path}")
            return 0

        json_files = list(directory.glob("*.json"))
        if not json_files:
            print(f"⚠️  目录中没有 JSON 文件: {dir_path}")
            return 0

        success_count = 0
        print(f"📁 找到 {len(json_files)} 个 JSON 文件")
        print("=" * 80)

        for json_file in json_files:
            if self.import_from_file(str(json_file)):
                success_count += 1
            print()

        return success_count

    def import_data(self, data: Dict[str, Any]) -> bool:
        """
        导入 JSON 数据

        Args:
            data: JSON 数据字典

        Returns:
            是否导入成功
        """
        try:
            # 1. 导入信源
            if "sources" in data:
                self._import_sources(data["sources"])

            # 2. 导入事件
            if "events" in data:
                self._import_events(data["events"])

            # 3. 导入声明
            if "claims" in data:
                self._import_claims(data["claims"])

            # 4. 导入实体
            if "entities" in data:
                self._import_entities(data["entities"])

            # 5. 导入物料
            if "artifacts" in data:
                self._import_artifacts(data["artifacts"])

            # 6. 导入证伪关系
            if "refutations" in data:
                self._import_refutations(data["refutations"])

            print(f"✅ 导入成功")
            self._print_stats()
            return True

        except Exception as e:
            print(f"❌ 导入过程出错: {e}")
            self.stats["errors"] += 1
            return False

    def _import_sources(self, sources: List[Dict[str, Any]]):
        """导入信源"""
        for source_data in sources:
            try:
                source = self.repo.find_or_create_source(
                    name=source_data["name"],
                    source_type=SourceType(source_data.get("type", "unknown")),
                    url=source_data.get("url"),
                    description=source_data.get("description"),
                    extra_data=source_data.get("extra_data", {})
                )
                self.stats["sources"] += 1
                print(f"  ✓ 信源: {source.name}")
            except Exception as e:
                print(f"  ✗ 信源导入失败 ({source_data.get('name', 'unknown')}): {e}")
                self.stats["errors"] += 1

    def _import_events(self, events: List[Dict[str, Any]]):
        """导入事件"""
        for event_data in events:
            try:
                event = self.repo.create_event(
                    event_id=event_data["id"],
                    title=event_data["title"],
                    description=event_data.get("description"),
                    status=EventStatus(event_data.get("status", "developing")),
                    extra_data=event_data.get("extra_data", {})
                )
                self.stats["events"] += 1
                print(f"  ✓ 事件: {event.id} - {event.title}")
            except Exception as e:
                print(f"  ✗ 事件导入失败 ({event_data.get('id', 'unknown')}): {e}")
                self.stats["errors"] += 1

    def _import_claims(self, claims: List[Dict[str, Any]]):
        """导入声明"""
        for claim_data in claims:
            try:
                # 先查找信源ID（如果提供的是名称）
                source_id = claim_data.get("source_id")
                if not source_id and "source_name" in claim_data:
                    source = self.repo.get_source_by_name(claim_data["source_name"])
                    if source:
                        source_id = source.id

                if not source_id:
                    print(f"  ✗ 声明导入失败: 找不到信源")
                    self.stats["errors"] += 1
                    continue

                claim = self.repo.create_claim(
                    text=claim_data["text"],
                    source_id=source_id,
                    event_id=claim_data.get("event_id"),
                    status=ClaimStatus(claim_data.get("status", "pending")),
                    claim_type=claim_data.get("claim_type"),
                    verification_result=claim_data.get("verification_result", {}),
                    extra_data=claim_data.get("extra_data", {})
                )
                self.stats["claims"] += 1
                print(f"  ✓ 声明: {claim.text[:50]}...")
            except Exception as e:
                print(f"  ✗ 声明导入失败: {e}")
                self.stats["errors"] += 1

    def _import_entities(self, entities: List[Dict[str, Any]]):
        """导入实体"""
        for entity_data in entities:
            try:
                entity = self.repo.find_or_create_entity(
                    name=entity_data["name"],
                    entity_type=entity_data["type"],
                    description=entity_data.get("description"),
                    extra_data=entity_data.get("extra_data", {})
                )
                self.stats["entities"] += 1
                print(f"  ✓ 实体: {entity.name} ({entity.type})")
            except Exception as e:
                print(f"  ✗ 实体导入失败 ({entity_data.get('name', 'unknown')}): {e}")
                self.stats["errors"] += 1

    def _import_artifacts(self, artifacts: List[Dict[str, Any]]):
        """导入物料"""
        for artifact_data in artifacts:
            try:
                # 物料需要直接创建，因为没有 find_or_create 方法
                # 直接使用 session 创建
                from src.ekg.models import Artifact
                artifact = Artifact(
                    type=artifact_data["type"],
                    url=artifact_data.get("url"),
                    content_hash=artifact_data.get("hash"),
                    content=artifact_data.get("content"),
                    extra_data=artifact_data.get("extra_data", {})
                )
                # claim_id 不是 Artifact 的字段，存储在 extra_data 中
                if "claim_id" in artifact_data:
                    artifact.extra_data["claim_id"] = artifact_data["claim_id"]

                self.session.add(artifact)
                self.session.commit()
                self.stats["artifacts"] += 1
                print(f"  ✓ 物料: {artifact.type} - {artifact.url[:50] if artifact.url else 'N/A'}...")
            except Exception as e:
                self.session.rollback()
                print(f"  ✗ 物料导入失败: {e}")
                self.stats["errors"] += 1

    def _import_refutations(self, refutations: List[Dict[str, Any]]):
        """导入证伪关系"""
        for refutation_data in refutations:
            try:
                self.repo.create_claim_refutation(
                    refuting_claim_id=refutation_data["refuting_claim_id"],
                    refuted_claim_id=refutation_data["refuted_claim_id"],
                    confidence=refutation_data.get("confidence", 1.0),
                    evidence=refutation_data.get("evidence", {})
                )
                self.stats["refutations"] += 1
                print(f"  ✓ 证伪关系: {refutation_data['refuting_claim_id']} -> {refutation_data['refuted_claim_id']}")
            except Exception as e:
                print(f"  ✗ 证伪关系导入失败: {e}")
                self.stats["errors"] += 1

    def _print_stats(self):
        """打印导入统计"""
        print("\n" + "=" * 80)
        print("📊 导入统计")
        print("=" * 80)
        print(f"  信源数: {self.stats['sources']}")
        print(f"  事件数: {self.stats['events']}")
        print(f"  声明数: {self.stats['claims']}")
        print(f"  实体数: {self.stats['entities']}")
        print(f"  物料数: {self.stats['artifacts']}")
        print(f"  证伪关系数: {self.stats['refutations']}")
        if self.stats['errors'] > 0:
            print(f"  ❌ 错误数: {self.stats['errors']}")
        print("=" * 80)

    def close(self):
        """关闭数据库连接"""
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()


def show_example():
    """显示 JSON 格式示例"""
    example = {
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
            },
            {
                "name": "@TechNews",
                "type": "social_media",
                "url": "https://twitter.com/technews",
                "description": "科技新闻社交媒体账号",
                "extra_data": {
                    "platform": "Twitter",
                    "followers": 50000
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
            },
            {
                "text": "公司官方确认将发布新产品",
                "source_name": "新华社",
                "event_id": "E-DEMO-001",
                "status": "verified",
                "claim_type": "factual",
                "verification_result": {
                    "method": "official_statement",
                    "verified_at": "2024-01-15"
                },
                "extra_data": {}
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
                "claim_id": 1,
                "hash": "abc123def456",
                "extra_data": {
                    "width": 1920,
                    "height": 1080
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

    print("=" * 80)
    print("📋 EKG JSON 数据格式示例")
    print("=" * 80)
    print()
    print(json.dumps(example, indent=2, ensure_ascii=False))
    print()
    print("=" * 80)
    print("📝 字段说明")
    print("=" * 80)
    print()
    print("sources (信源):")
    print("  - name: 信源名称 (必填)")
    print("  - type: 信源类型 (official_media/social_media/news_outlet/blog/forum/anonymous/unknown)")
    print("  - url: 信源URL (可选)")
    print("  - description: 描述 (可选)")
    print("  - extra_data: 额外数据 (可选)")
    print()
    print("events (事件):")
    print("  - id: 事件ID (必填)")
    print("  - title: 事件标题 (必填)")
    print("  - description: 事件描述 (可选)")
    print("  - status: 事件状态 (developing/investigated/verified/refuted)")
    print("  - extra_data: 额外数据 (可选)")
    print()
    print("claims (声明):")
    print("  - text: 声明内容 (必填)")
    print("  - source_id: 信源ID (可选，与source_name二选一)")
    print("  - source_name: 信源名称 (可选，与source_id二选一)")
    print("  - event_id: 关联事件ID (可选)")
    print("  - status: 声明状态 (pending/verified/refuted/unverifiable)")
    print("  - claim_type: 声明类型 (可选)")
    print("  - verification_result: 核查结果 (可选)")
    print("  - extra_data: 额外数据 (可选)")
    print()
    print("entities (实体):")
    print("  - name: 实体名称 (必填)")
    print("  - type: 实体类型 (person/organization/location等)")
    print("  - description: 描述 (可选)")
    print("  - extra_data: 额外数据 (可选)")
    print()
    print("artifacts (物料):")
    print("  - type: 物料类型 (image/video/document等)")
    print("  - url: 物料URL (必填)")
    print("  - claim_id: 关联声明ID (可选)")
    print("  - hash: 文件哈希值 (可选)")
    print("  - extra_data: 额外数据 (可选)")
    print()
    print("refutations (证伪关系):")
    print("  - refuting_claim_id: 证伪方声明ID (必填)")
    print("  - refuted_claim_id: 被证伪方声明ID (必填)")
    print("  - confidence: 置信度 (0-1之间，可选，默认1.0)")
    print("  - evidence: 证据 (可选)")
    print()
    print("=" * 80)
    print("💡 提示:")
    print("  1. 你可以只包含需要的部分，不需要全部字段")
    print("  2. 建议先导入信源，再导入事件和声明")
    print("  3. 声明中可以使用 source_name 代替 source_id")
    print("  4. 所有日期时间使用 ISO 8601 格式")
    print("=" * 80)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="EKG JSON 数据导入工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 显示 JSON 格式示例
  python demos/ekg_import_json.py --example

  # 从单个文件导入
  python demos/ekg_import_json.py --file data.json

  # 从目录批量导入
  python demos/ekg_import_json.py --dir ./data/

  # 指定数据库
  python demos/ekg_import_json.py --file data.json --db my_ekg.db
        """
    )

    parser.add_argument("--file", type=str, help="JSON 文件路径")
    parser.add_argument("--dir", type=str, help="包含 JSON 文件的目录")
    parser.add_argument("--db", type=str, default="demos/ekg_demo.db", help="数据库文件路径")
    parser.add_argument("--example", action="store_true", help="显示 JSON 格式示例")

    args = parser.parse_args()

    # 显示示例
    if args.example:
        show_example()
        sys.exit(0)

    # 检查参数
    if not args.file and not args.dir:
        parser.print_help()
        sys.exit(0)

    # 执行导入
    try:
        importer = EKGJSONImporter(args.db)

        if args.file:
            success = importer.import_from_file(args.file)
            sys.exit(0 if success else 1)

        if args.dir:
            count = importer.import_from_directory(args.dir)
            print(f"\n✅ 成功导入 {count} 个文件")
            sys.exit(0 if count > 0 else 1)

    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    finally:
        if 'importer' in locals():
            importer.close()


if __name__ == "__main__":
    main()
