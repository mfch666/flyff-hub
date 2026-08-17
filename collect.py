#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Flyff 站点采集器：仅对接 RageZone FlyFF Releases RSS。

采集结果写入 content/news/<slug>.json，按 URL 去重（state/seen.json）。
新条目会带上 needs_translation=true，交给翻译步骤（agent 在自动化中完成，
或人工/交互式运行 collect_and_translate）用准确中文重写标题与摘要。
英文原文（body_html）始终保留，供详情页「原文」区块展示。
"""
import json
import re
import os
import html
import urllib.request
import email.utils
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content" / "news"
STATE = ROOT / "state"
SEEN = STATE / "seen.json"
CONTENT.mkdir(parents=True, exist_ok=True)
STATE.mkdir(parents=True, exist_ok=True)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
RSS_NS = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "slash": "http://purl.org/rss/1.0/modules/slash/",
}


def load_config():
    return json.loads((ROOT / "config.json").read_text(encoding="utf-8"))


def load_seen():
    if SEEN.exists():
        try:
            return json.loads(SEEN.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_seen(seen):
    SEEN.write_text(json.dumps(seen, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch(url, headers=None, timeout=30):
    h = {"User-Agent": UA, "Accept": "*/*"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    return urllib.request.urlopen(req, timeout=timeout).read()


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()


def slugify(link, fallback=""):
    # RageZone 帖子 URL 形如 .../threads/<slug>.<帖子ID>/，取最后一个 4+ 位数字作为 ID，
    # 避免把标题里的年份（如 q2-2024 / 2026）误当成 slug。
    nums = re.findall(r"(\d{4,})", link or "")
    if nums:
        return nums[-1]
    base = re.sub(r"\W+", "-", (link or fallback))[:40].strip("-")
    return base or "item"


def write_item(rec, seen, counter):
    link = rec.get("url", "")
    if not link or link in seen:
        return counter
    slug = slugify(link, rec.get("title", ""))
    base = slug
    n = 1
    while (CONTENT / f"{slug}.json").exists():
        n += 1
        slug = f"{base}-{n}"
    rec["slug"] = slug
    (CONTENT / f"{slug}.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    seen[link] = slug
    counter += 1
    print("  +", rec.get("date", ""), rec.get("title", "")[:50])
    return counter


def collect_ragezone(src, cfg, seen, counter):
    try:
        data = fetch(
            src["url"], headers={"Accept": "application/rss+xml, text/xml, */*"}
        )
    except Exception as e:
        print("[WARN] RageZone 抓取失败，跳过：", e)
        return counter
    try:
        root = ET.fromstring(data)
    except Exception as e:
        print("[WARN] RageZone RSS 解析失败，跳过：", e)
        return counter
    chan = root.find("channel")
    if chan is None:
        print("[WARN] RageZone RSS 无 channel，跳过")
        return counter
    for it in chan.findall("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        pub = it.findtext("pubDate") or ""
        creator = (
            it.findtext("dc:creator", namespaces=RSS_NS)
            or it.findtext("author")
            or ""
        )
        comments = it.findtext("slash:comments", namespaces=RSS_NS) or "0"
        body = it.findtext("content:encoded", namespaces=RSS_NS) or ""
        try:
            comments_n = int(comments or 0)
        except Exception:
            comments_n = 0
        dt = None
        if pub:
            try:
                dt = email.utils.parsedate_to_datetime(pub)
            except Exception:
                dt = None
        date_iso = (
            dt.strftime("%Y-%m-%d")
            if dt
            else datetime.now().strftime("%Y-%m-%d")
        )
        rec = {
            "title": title,
            "url": link,
            "date": date_iso,
            "source": src["name"],
            "author": creator,
            "comments": comments_n,
            "category": src.get("category", "release"),
            "excerpt": strip_tags(body)[:240],
            "body_html": body,
            "needs_translation": True,
        }
        counter = write_item(rec, seen, counter)
    return counter


def main():
    cfg = load_config()
    seen = load_seen()
    counter = 0
    print("开始采集（仅 RageZone）...")
    for src in cfg.get("sources", []):
        if src.get("type") == "rss":
            counter = collect_ragezone(src, cfg, seen, counter)
    save_seen(seen)
    print(f"采集完成：本次新增 {counter} 条，累计已知 {len(seen)} 条。")


if __name__ == "__main__":
    main()
