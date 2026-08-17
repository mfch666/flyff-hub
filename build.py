#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Flyff 静态站生成器：读取 content/news、content/knowledge 的 JSON，
渲染纯静态 HTML 到 public/。零外部依赖（仅标准库），可直接部署到 EdgeOne Makers。
"""
import json
import html
import re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
CONTENT_NEWS = ROOT / "content" / "news"
CONTENT_KNOW = ROOT / "content" / "knowledge"
PUBLIC = ROOT / "public"
PUBLIC_N = PUBLIC / "news"
PUBLIC_K = PUBLIC / "knowledge"
for p in (PUBLIC, PUBLIC_N, PUBLIC_K):
    p.mkdir(parents=True, exist_ok=True)


def load_config():
    return json.loads((ROOT / "config.json").read_text(encoding="utf-8"))


def load_news():
    items = []
    if CONTENT_NEWS.exists():
        for f in sorted(CONTENT_NEWS.glob("*.json")):
            try:
                items.append(json.loads(f.read_text(encoding="utf-8")))
            except Exception:
                pass
    items.sort(key=lambda x: x.get("date", ""), reverse=True)
    return items


def load_knowledge():
    items = []
    if CONTENT_KNOW.exists():
        for f in sorted(CONTENT_KNOW.glob("*.json")):
            try:
                items.append(json.loads(f.read_text(encoding="utf-8")))
            except Exception:
                pass
    return items


def esc(s):
    return html.escape(str(s or ""), quote=False)


CSS = """
:root{--bg:#f7f8fa;--card:#fff;--text:#1f2430;--muted:#6b7280;--line:#e5e7eb;--accent:#3b6d11;--hot:#c0392b}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);line-height:1.65}
.wrap{max-width:880px;margin:0 auto;padding:0 20px}
.site-head{background:#fff;border-bottom:1px solid var(--line)}
.site-head .wrap{display:flex;align-items:center;justify-content:space-between;height:60px}
.brand{font-weight:700;font-size:18px;color:var(--text);text-decoration:none}
.site-head nav a{margin-left:18px;color:var(--muted);text-decoration:none;font-size:14px}
.site-head nav a.active{color:var(--accent);font-weight:600}
main.wrap{padding-top:28px;padding-bottom:48px}
.hero{background:#fff;border:1px solid var(--line);border-radius:14px;padding:28px;margin-bottom:24px}
.hero h1{margin:0 0 8px;font-size:26px}
.hero p{margin:0;color:var(--muted)}
.section-title{font-size:18px;margin:28px 0 12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin-bottom:14px;transition:border-color .15s}
.card:hover{border-color:#c9d2c0}
.card h2{margin:6px 0;font-size:17px;line-height:1.4}
.card h2 a{color:var(--text);text-decoration:none}
.card h2 a:hover{color:var(--accent)}
.meta{font-size:12px;color:var(--muted);display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.orig{font-size:12px;color:#9aa3ad;margin:4px 0 0;font-style:italic}
.excerpt{color:#374151;font-size:14px;margin:8px 0}
.foot{font-size:13px;margin-top:6px;display:flex;gap:14px;align-items:center}
.ext{color:var(--accent);text-decoration:none}
.comments{color:var(--muted)}
.badge{font-size:11px;padding:2px 8px;border-radius:999px;font-weight:600}
.badge.hot{background:#fdecea;color:var(--hot)}
.src{background:#eef2ea;color:#3b6d11;padding:1px 8px;border-radius:6px}
.article{background:#fff;border:1px solid var(--line);border-radius:12px;padding:24px}
.article h1{margin-top:0;font-size:24px}
.article .meta{margin-bottom:16px}
.article-body{font-size:15px}
.article-body img{max-width:100%}
.article-body a{color:var(--accent)}
.article .lead{font-size:15px;color:#1f2430;background:#f3f6ee;border-left:3px solid var(--accent);padding:12px 14px;border-radius:8px;margin:14px 0}
.orig-wrap{margin:18px 0;border:1px solid var(--line);border-radius:10px;overflow:hidden}
.orig-wrap summary{cursor:pointer;padding:10px 14px;background:#fafbfc;font-size:13px;color:var(--muted);user-select:none}
.orig-wrap summary:hover{color:var(--accent)}
.orig-wrap .orig-title{font-size:13px;color:#9aa3ad;font-style:italic;margin:0 0 8px}
.orig-body{padding:0 14px 14px;color:#4b5563;font-size:13px}
.orig-body img{max-width:100%}
.site-foot{border-top:1px solid var(--line);color:var(--muted);font-size:13px;padding:20px 0;text-align:center}
.qq-line{margin-top:6px;font-size:13px}
.qq-link{color:var(--accent);font-weight:600;text-decoration:none}
.qq-link:hover{text-decoration:underline}
.qq-qr{display:inline-flex;flex-direction:column;align-items:center;gap:6px;margin-top:12px}
.qq-qr-img{width:120px;height:120px;object-fit:contain;border:1px solid var(--line);border-radius:8px;padding:5px;background:#fff;display:block}
.qr-tip{font-size:11px;color:var(--muted)}
a.back{display:inline-block;margin-bottom:16px;color:var(--accent);text-decoration:none;font-size:14px}
.empty{color:var(--muted);padding:30px 0;text-align:center}
"""

BASE = """<!DOCTYPE html>
<html lang="{{lang}}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{page_title}} · {{site_title}}</title>
<meta name="description" content="{{subtitle}}">
<style>{{css}}</style>
</head>
<body>
{{head}}
<main class="wrap">{{content}}</main>
<footer class="site-foot"><div class="wrap">© {{year}} {{site_title}} · 内容聚合自 RageZone FlyFF Releases，由 AI 用中文重新整理，版权归原作者所有{{qq_line}}</div></footer>
</body>
</html>"""


def render_page(cfg, page_title, content, nav_active="", assets_path="assets/"):
    def navcls(k):
        return ' class="active"' if nav_active == k else ""

    head = (
        '<header class="site-head"><div class="wrap">'
        f'<a class="brand" href="index.html">{esc(cfg["site"]["title"])}</a>'
        "<nav>"
        f'<a href="index.html"{navcls("home")}>首页</a>'
        f'<a href="news/index.html"{navcls("news")}>新闻/发布</a>'
        f'<a href="knowledge/index.html"{navcls("know")}>知识库</a>'
        "</nav></div></header>"
    )
    owner = cfg.get("owner", {}) or {}
    qq = owner.get("qq", "")
    qqname = owner.get("name", "")
    tip = owner.get("tip", "如有技术要求，可添加站长 QQ")
    qr = owner.get("qr", "")
    if qq:
        qr_html = ""
        if qr:
            qr_html = (
                f'<div class="qq-qr"><img class="qq-qr-img" '
                f'src="{esc(assets_path + qr)}" '
                f'alt="站长 QQ 二维码（{esc(qqname or qq)}）">'
                f'<span class="qr-tip">手机扫一扫，添加站长 QQ</span></div>'
            )
        qq_line = (
            f'<div class="qq-line">{esc(tip)}：'
            f'<span class="qq-num">{esc(qq)}</span>'
            + (f"（{esc(qqname)}）" if qqname else "")
            + qr_html
            + "</div>"
        )
    else:
        qq_line = ""
    return (
        BASE.replace("{{page_title}}", esc(page_title))
        .replace("{{site_title}}", esc(cfg["site"]["title"]))
        .replace("{{subtitle}}", esc(cfg["site"]["subtitle"]))
        .replace("{{head}}", head)
        .replace("{{content}}", content)
        .replace("{{year}}", str(datetime.now().year))
        .replace("{{lang}}", esc(cfg["site"].get("lang", "zh-CN")))
        .replace("{{css}}", CSS)
        .replace("{{qq_line}}", qq_line)
    )


def news_card(it, cfg):
    hot = ""
    if int(it.get("comments") or 0) >= cfg.get("hot_threshold", 30):
        hot = f'<span class="badge hot">热门 · {it["comments"]} 评论</span>'
    comments = ""
    if it.get("comments"):
        comments = f'<span class="comments">{it["comments"]} 评论</span>'
    title = it.get("title_zh") or it.get("title", "")
    excerpt = it.get("excerpt_zh") or it.get("excerpt", "")
    orig = it.get("title", "") if it.get("title_zh") else ""
    orig_line = f'<div class="orig">原文：{esc(orig)}</div>' if orig else ""
    return f'''<article class="card">
  <div class="meta"><span class="date">{esc(it.get("date",""))}</span><span class="src">{esc(it.get("source",""))}</span>{hot}</div>
  <h2><a href="news/{esc(it.get("slug",""))}.html">{esc(title)}</a></h2>
  {orig_line}
    <p class="excerpt">{esc(excerpt)}</p>
  <div class="foot"><a class="ext" href="{esc(it.get("url",""))}" target="_blank" rel="noopener">查看原文 ↗</a>{comments}</div>
</article>'''


def know_card(it):
    return f'''<article class="card">
  <div class="meta"><span class="src">{esc(it.get("tag","知识"))}</span></div>
  <h2><a href="knowledge/{esc(it.get("slug",""))}.html">{esc(it.get("title",""))}</a></h2>
  <p class="excerpt">{esc(it.get("excerpt",""))}</p>
</article>'''


def article_page(cfg, it, kind, assets_path="assets/"):
    body = it.get("body_html") or it.get("body") or ""
    meta = (
        f'<div class="meta"><span class="date">{esc(it.get("date",""))}</span>'
        f'<span class="src">{esc(it.get("source",""))}</span>'
        f'<span class="author">{esc(it.get("author",""))}</span></div>'
    )
    back = "news/index.html" if kind == "news" else "knowledge/index.html"
    label = "新闻/发布" if kind == "news" else "知识库"
    if kind == "news":
        title = it.get("title_zh") or it.get("title", "")
        lead = it.get("summary_zh") or it.get("excerpt_zh") or ""
        orig_title = it.get("title", "") if it.get("title_zh") else ""
        orig_block = ""
        if orig_title or body:
            inner = ""
            if orig_title:
                inner += f'<p class="orig-title">原标题：{esc(orig_title)}</p>'
            if body:
                inner += f'<div class="article-body orig-body">{body}</div>'
            orig_block = (
                '<details class="orig-wrap"><summary>原文（English）</summary>'
                f"{inner}</details>"
            )
        lead_html = f'<p class="lead">{esc(lead)}</p>' if lead else ""
        body_html = lead_html + orig_block
    else:
        title = it.get("title", "")
        body_html = f'<div class="article-body">{body}</div>' if body else "<p>（暂无正文）</p>"
    content = (
        f'<a class="back" href="{back}">← 返回{label}</a>'
        '<article class="article">'
        f"<h1>{esc(title)}</h1>{meta}"
        f"{body_html}"
        f'<p class="foot"><a class="ext" href="{esc(it.get("url",""))}" target="_blank" rel="noopener">查看原文 ↗</a></p>'
        "</article>"
    )
    return render_page(cfg, title, content, "news" if kind == "news" else "know", assets_path)


def build():
    cfg = load_config()
    news = load_news()
    know = load_knowledge()

    # 首页
    hero = (
        '<section class="hero"><h1>'
        + esc(cfg["site"]["title"])
        + "</h1><p>"
        + esc(cfg["site"]["subtitle"])
        + "</p></section>"
    )
    latest = "".join(news_card(n, cfg) for n in news[:8]) or '<p class="empty">暂无新闻，运行 collect.py 采集。</p>'
    know_list = "".join(know_card(k) for k in know) or '<p class="empty">暂无知识库内容。</p>'
    index_content = (
        hero
        + '<h3 class="section-title">最新发布 / 新闻</h3>'
        + latest
        + '<p class="foot"><a class="ext" href="news/index.html">查看全部新闻/发布 →</a></p>'
        + '<h3 class="section-title">知识库</h3>'
        + know_list
    )
    (PUBLIC / "index.html").write_text(
        render_page(cfg, "首页", index_content, "home"), encoding="utf-8"
    )

    # 新闻列表页
    news_index = '<h1>新闻 / 技术发布</h1>' + (
        "".join(news_card(n, cfg) for n in news)
        or '<p class="empty">暂无内容。</p>'
    )
    (PUBLIC_N / "index.html").write_text(
        render_page(cfg, "新闻/发布", news_index, "news", "../assets/"), encoding="utf-8"
    )

    # 新闻详情页
    for n in news:
        (PUBLIC_N / f"{n['slug']}.html").write_text(
            article_page(cfg, n, "news", "../assets/"), encoding="utf-8"
        )

    # 知识库列表页
    know_index = '<h1>知识库</h1>' + (
        "".join(know_card(k) for k in know) or '<p class="empty">暂无内容。</p>'
    )
    (PUBLIC_K / "index.html").write_text(
        render_page(cfg, "知识库", know_index, "know", "../assets/"), encoding="utf-8"
    )

    # 知识库详情页
    for k in know:
        (PUBLIC_K / f"{k['slug']}.html").write_text(
            article_page(cfg, k, "know", "../assets/"), encoding="utf-8"
        )

    print(
        f"构建完成：{len(news)} 条新闻、{len(know)} 篇知识，已输出到 public/。"
    )


if __name__ == "__main__":
    build()
