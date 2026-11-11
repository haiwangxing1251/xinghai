# -*- coding: utf-8 -*-
"""
星海科技官网生成器
读取 src/template.html 模板 + data/*.json 数据 → 生成 docs/index.html

零依赖，纯标准库。GitHub Actions 自动运行。
二期将接入：行业资讯爬虫 + 招标公告爬虫（写入 data/news.json、data/tenders.json）
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

CST = timezone(timedelta(hours=8))
ROOT = os.path.dirname(os.path.abspath(__file__))

COMPANY = "邵阳市星海科技有限公司"
COMPANY_SHORT = "星海科技"


def load_json(name: str):
    """读取 data/name.json，不存在返回 None。"""
    path = os.path.join(ROOT, "data", name)
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[site] 读取 {name} 失败: {e}")
        return None


def render_news_section(items):
    """行业资讯区块。无数据时显示占位。"""
    if not items:
        return """
<div class="empty-hint">行业资讯板块即将上线，届时自动同步弱电安防行业动态</div>
"""
    cards = []
    for it in items[:8]:
        cards.append(
            '<a class="news-item" href="' + it.get("url", "#") + '" target="_blank" rel="noopener">'
            '<span class="news-title">' + it.get("title", "") + "</span>"
            '<span class="news-date">' + it.get("date", "") + "</span></a>"
        )
    return "\n".join(cards)


def render_tender_section(items):
    """招标商机区块。无数据时显示占位。"""
    if not items:
        return """
<div class="empty-hint">招标商机板块即将上线，届时自动同步公开招标公告</div>
"""
    rows = []
    for it in items[:10]:
        rows.append(
            '<a class="tender-item" href="' + it.get("url", "#") + '" target="_blank" rel="noopener">'
            '<span class="tender-title">' + it.get("title", "") + "</span>"
            '<span class="tender-meta">' + it.get("region", "") + " · " + it.get("date", "") + "</span></a>"
        )
    return "\n".join(rows)


def main():
    template_path = os.path.join(ROOT, "src", "template.html")
    with open(template_path, encoding="utf-8") as f:
        html = f.read()

    now = datetime.now(CST).strftime("%Y-%m-%d %H:%M")

    # 二期数据（当前为空 → 显示占位）
    news = load_json("news.json") or []
    tenders = load_json("tenders.json") or []

    html = (html
            .replace("__COMPANY__", COMPANY)
            .replace("__COMPANY_SHORT__", COMPANY_SHORT)
            .replace("__UPDATED__", now)
            .replace("__NEWS_ITEMS__", render_news_section(news))
            .replace("__TENDER_ITEMS__", render_tender_section(tenders)))

    out = os.path.join(ROOT, "docs", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[site] 官网已生成: {out}")
    print(f"[site] 资讯 {len(news)} 条 / 招标 {len(tenders)} 条 / 生成时间 {now}")


if __name__ == "__main__":
    main()
