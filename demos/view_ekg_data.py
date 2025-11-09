#!/usr/bin/env python3
"""
查看 EKG 数据库内容的简单脚本

运行: python demos/view_ekg_data.py
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = "demos/ekg_demo.db"


def view_database():
    """查看数据库内容"""

    if not Path(DB_PATH).exists():
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        print("请先运行: python demos/ekg_demo.py")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 80)
    print("EKG 数据库内容查看")
    print("=" * 80)

    # 查看信源
    print("\n📌 信源表 (sources)")
    print("-" * 80)
    cursor.execute("""
        SELECT id, name, type, credit_score, total_claims, verified_claims, refuted_claims
        FROM sources
    """)
    print(f"{'ID':<5} {'信源名称':<20} {'类型':<15} {'信誉分':<8} {'总声明':<8} {'已验证':<8} {'已证伪':<8}")
    print("-" * 80)
    for row in cursor.fetchall():
        print(f"{row[0]:<5} {row[1]:<20} {row[2]:<15} {row[3]:<8} {row[4]:<8} {row[5]:<8} {row[6]:<8}")

    # 查看事件
    print("\n📌 事件表 (events)")
    print("-" * 80)
    cursor.execute("""
        SELECT id, title, status, credibility_score
        FROM events
    """)
    print(f"{'事件ID':<10} {'标题':<30} {'状态':<15} {'可信度':<10}")
    print("-" * 80)
    for row in cursor.fetchall():
        score = f"{row[3]:.1f}" if row[3] else "N/A"
        print(f"{row[0]:<10} {row[1]:<30} {row[2]:<15} {score:<10}")

    # 查看声明
    print("\n📌 声明表 (claims)")
    print("-" * 80)
    cursor.execute("""
        SELECT c.id, c.text, s.name, c.status
        FROM claims c
        LEFT JOIN sources s ON c.source_id = s.id
        LIMIT 10
    """)
    print(f"{'ID':<5} {'声明内容':<40} {'信源':<20} {'状态':<12}")
    print("-" * 80)
    for row in cursor.fetchall():
        text = row[1][:37] + "..." if len(row[1]) > 40 else row[1]
        source = row[2] or "未知"
        print(f"{row[0]:<5} {text:<40} {source:<20} {row[3]:<12}")

    # 查看证伪关系
    print("\n📌 证伪关系表 (claim_refutations)")
    print("-" * 80)
    cursor.execute("""
        SELECT cr.id, c1.text as refuting, c2.text as refuted, cr.confidence
        FROM claim_refutations cr
        LEFT JOIN claims c1 ON cr.refuting_claim_id = c1.id
        LEFT JOIN claims c2 ON cr.refuted_claim_id = c2.id
    """)
    print(f"{'ID':<5} {'证伪方':<30} {'被证伪':<30} {'置信度':<10}")
    print("-" * 80)
    count = 0
    for row in cursor.fetchall():
        count += 1
        refuting = row[1][:27] + "..." if row[1] and len(row[1]) > 30 else (row[1] or "N/A")
        refuted = row[2][:27] + "..." if row[2] and len(row[2]) > 30 else (row[2] or "N/A")
        print(f"{row[0]:<5} {refuting:<30} {refuted:<30} {row[3]:<10}")

    if count == 0:
        print("(无数据)")

    # 查看调查历史
    print("\n📌 调查历史表 (investigation_history)")
    print("-" * 80)
    cursor.execute("""
        SELECT investigation_id, event_id, credibility_score
        FROM investigation_history
    """)
    print(f"{'调查ID':<15} {'事件ID':<10} {'可信度':<10}")
    print("-" * 80)
    count = 0
    for row in cursor.fetchall():
        count += 1
        score = f"{row[2]:.1f}" if row[2] else "N/A"
        print(f"{row[0]:<15} {row[1]:<10} {score:<10}")

    if count == 0:
        print("(无数据)")

    # 统计汇总
    print("\n📊 统计汇总")
    print("-" * 80)

    tables = ['sources', 'events', 'claims', 'entities', 'artifacts', 'claim_refutations', 'investigation_history']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table:<30} {count:>5} 条记录")

    conn.close()

    print("\n" + "=" * 80)
    print("✅ 查看完成")
    print(f"📁 数据库文件: {DB_PATH}")
    print("=" * 80)


if __name__ == "__main__":
    view_database()
