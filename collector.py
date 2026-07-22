from __future__ import annotations

import argparse
import email.utils
import hashlib
import html
import json
import re
import sqlite3
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable

from opencc import OpenCC


USER_AGENT = "ChenxiangCollector/1.0 (+https://github.com/linlonghui999/chenxiang)"
SIMPLIFIER = OpenCC("t2s")


def to_simplified(value: str) -> str:
    return SIMPLIFIER.convert(value or "")


@dataclass
class Item:
    title: str
    url: str
    source: str
    published: str
    summary: str


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self.parts.append(text)


def clean_html(value: str) -> str:
    parser = TextExtractor()
    parser.feed(html.unescape(value or ""))
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/xml, application/json, text/xml, */*"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def child_text(node: ET.Element, names: Iterable[str]) -> str:
    wanted = {name.lower() for name in names}
    for child in list(node):
        name = child.tag.split("}")[-1].lower()
        if name in wanted:
            if name == "link" and child.attrib.get("href"):
                return child.attrib["href"].strip()
            return "".join(child.itertext()).strip()
    return ""


def normalize_date(value: str) -> str:
    if not value:
        return ""
    try:
        parsed = email.utils.parsedate_to_datetime(value)
        return parsed.astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError):
        pass
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
    except ValueError:
        return value[:40]


def collect_rss(source: dict, limit: int) -> list[Item]:
    root = ET.fromstring(fetch_bytes(source["url"]))
    nodes = root.findall(".//item")
    if not nodes:
        nodes = [node for node in root.iter() if node.tag.split("}")[-1].lower() == "entry"]

    items: list[Item] = []
    for node in nodes[:limit]:
        title = clean_html(child_text(node, ["title"]))
        url = child_text(node, ["link", "guid", "id"])
        summary = clean_html(child_text(node, ["description", "summary", "content", "encoded"]))
        published = normalize_date(child_text(node, ["pubDate", "published", "updated", "date"]))
        if title and url:
            items.append(Item(to_simplified(title), url, to_simplified(source["name"]), published, to_simplified(summary)))
    return items


def collect_pubmed(source: dict, limit: int) -> list[Item]:
    query = urllib.parse.quote(source["query"])
    search_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=pubmed&term={query}&retmode=json&retmax={limit}&sort=pub+date"
    )
    search_data = json.loads(fetch_bytes(search_url).decode("utf-8"))
    ids = search_data.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []

    summary_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        f"?db=pubmed&id={','.join(ids)}&retmode=json"
    )
    summary_data = json.loads(fetch_bytes(summary_url).decode("utf-8"))
    result = summary_data.get("result", {})

    items: list[Item] = []
    for pubmed_id in ids:
        record = result.get(pubmed_id, {})
        title = to_simplified(clean_html(record.get("title", "")))
        authors = ", ".join(a.get("name", "") for a in record.get("authors", [])[:5])
        journal = record.get("fulljournalname") or record.get("source", "")
        summary = to_simplified("；".join(part for part in [authors, journal] if part))
        if title:
            items.append(
                Item(
                    title=title,
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/",
                    source=to_simplified(source["name"]),
                    published=record.get("pubdate", ""),
                    summary=summary,
                )
            )
    return items


CATEGORY_RULES = {
    "市场价格": ["价格", "市场", "拍卖", "交易", "收藏", "消费", "产业", "品牌"],
    "文化历史": ["文化", "历史", "香道", "非遗", "博物馆", "传统", "古代", "文物"],
    "产区原料": ["产区", "海南", "东莞", "广东", "越南", "印尼", "马来西亚", "种植", "结香"],
    "科研药用": ["研究", "药", "论文", "成分", "药理", "临床", "Aquilaria", "agarwood", "PubMed"],
    "政策监管": ["监管", "海关", "走私", "保护", "濒危", "CITES", "标准", "政策", "执法"],
}


TOPIC_ANGLES = {
    "市场价格": ["价格变化背后的原因", "普通消费者如何判断价值", "行业趋势与常见误区"],
    "文化历史": ["一个历史故事讲清沉香文化", "传统香事如何进入现代生活", "文化概念的通俗解释"],
    "产区原料": ["不同产区差异怎么理解", "从结香过程看品质", "新手认识原料的观察方法"],
    "科研药用": ["把研究结论讲成普通人能懂的知识", "论文发现与传统认识的异同", "避免夸大功效的科学解读"],
    "政策监管": ["政策变化对行业和消费者的影响", "合法合规购买注意事项", "保护资源与产业发展的平衡"],
    "综合资讯": ["事件背后的沉香知识", "从热点延伸一个新手问题", "这条资讯对消费者意味着什么"],
}


def relevance_score(item: Item, keywords: list[str]) -> int:
    haystack = f"{item.title} {item.summary}".lower()
    strong_terms = ["沉香", "棋楠", "莞香", "沉水香", "aquilaria", "agarwood", "oud"]
    qinan_context = ["香", "木", "收藏", "产业", "产区", "手串", "文玩", "结香", "原料"]
    has_strong_term = any(term in haystack for term in strong_terms)
    has_qinan_context = "奇楠" in haystack and any(term in haystack for term in qinan_context)
    if not has_strong_term and not has_qinan_context:
        return 0

    score = 0
    for keyword in keywords:
        occurrences = haystack.count(keyword.lower())
        if occurrences:
            score += min(occurrences, 3)
    return score


def classify(item: Item) -> str:
    haystack = f"{item.title} {item.summary} {item.source}".lower()
    scores = {
        category: sum(haystack.count(keyword.lower()) for keyword in keywords)
        for category, keywords in CATEGORY_RULES.items()
    }
    category, score = max(scores.items(), key=lambda pair: pair[1])
    return category if score else "综合资讯"


def canonical_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url.strip())
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query_map = dict(query)
    if parsed.netloc.lower().endswith("bing.com") and "url" in query_map:
        return canonical_url(query_map["url"])
    ignored = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "ref"}
    clean_query = urllib.parse.urlencode([(k, v) for k, v in query if k.lower() not in ignored])
    return urllib.parse.urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path, clean_query, ""))


def url_hash(url: str) -> str:
    return hashlib.sha256(canonical_url(url).encode("utf-8")).hexdigest()


def safe_filename(title: str, digest: str) -> str:
    cleaned = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", "-", title)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .-")
    return f"{cleaned[:70] or '未命名信息'}-{digest[:8]}.md"


def yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def write_note(path: Path, item: Item, category: str, score: int, collected_at: str) -> None:
    angles = TOPIC_ANGLES[category]
    summary = item.summary or "来源未提供摘要，请打开原文查看。"
    content = f"""---
title: {yaml_quote(item.title)}
source: {yaml_quote(item.source)}
url: {yaml_quote(item.url)}
published: {yaml_quote(item.published)}
collected: {yaml_quote(collected_at)}
category: {yaml_quote(category)}
relevance: {score}
status: {yaml_quote('待阅读')}
tags:
  - 沉香信息
  - {category}
---

# {item.title}

## 信息摘要

{summary}

## 可用选题方向

- {angles[0]}
- {angles[1]}
- {angles[2]}

## 创作记录

- 核心观点：
- 可信依据：
- 适合形式：图文 / 短视频 / 直播
- 目标受众：

## 原文

[{item.source}]({item.url})
"""
    path.write_text(content, encoding="utf-8")


def init_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            url_hash TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            source TEXT NOT NULL,
            published TEXT,
            collected TEXT NOT NULL,
            path TEXT NOT NULL,
            category TEXT NOT NULL,
            score INTEGER NOT NULL
        )
        """
    )
    connection.commit()
    return connection


def update_dashboards(output_root: Path, connection: sqlite3.Connection) -> None:
    rows = connection.execute(
        "SELECT title, url, source, collected, path, category, score "
        "FROM items ORDER BY collected DESC, score DESC LIMIT 200"
    ).fetchall()

    counts = connection.execute(
        "SELECT category, COUNT(*) FROM items GROUP BY category ORDER BY COUNT(*) DESC"
    ).fetchall()
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
    overview = [
        "# 沉香信息总览",
        "",
        f"> 最后更新：{now}",
        "",
        "## 分类统计",
        "",
    ]
    overview.extend(f"- **{category}**：{count} 条" for category, count in counts)
    overview.extend(["", "## 最新信息", ""])
    for title, url, source, collected, path, category, score in rows[:50]:
        relative = Path(path).relative_to(output_root).with_suffix("").as_posix()
        overview.append(f"- [[{relative}|{title}]] · {category} · 相关度 {score} · [{source}]({url})")
    (output_root / "信息总览.md").write_text("\n".join(overview) + "\n", encoding="utf-8")

    topics = [
        "# 沉香自媒体选题池",
        "",
        "> 勾选准备创作的内容，并在对应信息笔记中补充观点和口播思路。",
        "",
    ]
    for title, url, source, collected, path, category, score in rows[:100]:
        relative = Path(path).relative_to(output_root).with_suffix("").as_posix()
        topics.append(f"- [ ] [[{relative}|{title}]] · #{category} · 相关度 {score}")
    (output_root / "选题池.md").write_text("\n".join(topics) + "\n", encoding="utf-8")


def run(config_path: Path) -> int:
    config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    vault_path = Path(config["vault_path"]).expanduser()
    if not vault_path.is_dir():
        raise FileNotFoundError(f"Obsidian 知识库不存在：{vault_path}")

    output_root = vault_path / config.get("output_folder", "沉香信息库")
    day = datetime.now().astimezone().strftime("%Y-%m-%d")
    daily_dir = output_root / "每日收集" / day
    daily_dir.mkdir(parents=True, exist_ok=True)

    state_dir = config_path.parent / "data"
    connection = init_db(state_dir / "collector.db")
    limit = int(config.get("max_items_per_source", 20))
    minimum_score = int(config.get("minimum_relevance_score", 1))
    keywords = list(config.get("keywords", []))
    collected_at = datetime.now().astimezone().isoformat(timespec="seconds")

    candidates: list[Item] = []
    failures: list[str] = []
    for source in config.get("sources", []):
        try:
            if source["type"] == "rss":
                found = collect_rss(source, limit)
            elif source["type"] == "pubmed":
                found = collect_pubmed(source, limit)
            else:
                failures.append(f"{source.get('name', '未知来源')}：不支持的类型")
                continue
            candidates.extend(found)
            print(f"[来源] {source['name']}：读取 {len(found)} 条")
        except Exception as error:  # Keep other sources running when one endpoint fails.
            failures.append(f"{source.get('name', '未知来源')}：{error}")

    added = 0
    skipped_duplicate = 0
    skipped_irrelevant = 0
    for item in candidates:
        digest = url_hash(item.url)
        if connection.execute("SELECT 1 FROM items WHERE url_hash = ?", (digest,)).fetchone():
            skipped_duplicate += 1
            continue

        score = relevance_score(item, keywords)
        if score < minimum_score:
            skipped_irrelevant += 1
            continue

        category = classify(item)
        note_path = daily_dir / safe_filename(item.title, digest)
        write_note(note_path, item, category, score, collected_at)
        connection.execute(
            "INSERT INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                digest,
                item.title,
                item.url,
                item.source,
                item.published,
                collected_at,
                str(note_path),
                category,
                score,
            ),
        )
        added += 1

    connection.commit()
    update_dashboards(output_root, connection)
    connection.close()

    print(f"[完成] 新增 {added} 条，重复 {skipped_duplicate} 条，低相关 {skipped_irrelevant} 条")
    print(f"[输出] {output_root}")
    if failures:
        print("[提醒] 以下来源本次读取失败：")
        for failure in failures:
            print(f"  - {failure}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="收集沉香相关信息并写入 Obsidian")
    parser.add_argument("--config", default="config.json", help="配置文件路径")
    args = parser.parse_args()
    try:
        return run(Path(args.config).resolve())
    except Exception as error:
        print(f"[错误] {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
