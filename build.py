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
    # 置顶项排在最前（稳定排序，组内保持原有顺序）
    items.sort(key=lambda x: 0 if x.get("pinned") else 1)
    return items


def esc(s):
    return html.escape(str(s or ""), quote=False)


CSS = """
/* ===== 基础变量 ===== */
:root{
  --bg:#f0f2f5;
  --card:#fff;
  --text:#1a1a2e;
  --muted:#6478b;
  --line:#e2e8f0;
  --accent:#2d6a4f;
  --accent-light:#d8f3dc;
  --hot:#c1121f;
  --hot-light:#ffe5e5;
  --gold:#b8860b;
  --gold-light:#fff8e6;
  --shadow:0 1px 3px rgba(0,0,0,.08),0 4px 12px rgba(0,0,0,.04);
  --shadow-hover:0 4px 12px rgba(0,0,0,.12),0 12px 28px rgba(0,0,0,.08);
  --radius:12px;
  --radius-sm:8px;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
  background:var(--bg);color:var(--text);line-height:1.7;
  background-image:linear-gradient(180deg,#f8fafc 0%,var(--bg) 100%);
  min-height:100vh;
}
.wrap{max-width:860px;margin:0 auto;padding:0 20px}
.site-head{background:rgba(255,255,255,.92);backdrop-filter:blur(12px);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:100;box-shadow:0 1px 0 rgba(0,0,0,.04)}
.site-head .wrap{display:flex;align-items:center;justify-content:space-between;height:62px}
.brand{font-weight:800;font-size:19px;text-decoration:none;letter-spacing:-.3px;background:linear-gradient(135deg,var(--accent) 0%,#1b4332 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.site-head nav{display:flex;gap:4px}
.site-head nav a{padding:8px 16px;color:var(--muted);text-decoration:none;font-size:14px;font-weight:500;border-radius:var(--radius-sm);transition:all .15s ease}
.site-head nav a:hover{color:var(--accent);background:var(--accent-light)}
.site-head nav a.active{color:var(--accent);font-weight:600;background:var(--accent-light)}
main.wrap{padding-top:32px;padding-bottom:56px}
.hero{background:linear-gradient(135deg,#1b4332 0%,#2d6a4f 50%,#40916c 100%);border-radius:16px;padding:36px 32px;margin-bottom:28px;color:#fff;position:relative;overflow:hidden;box-shadow:0 4px 24px rgba(45,106,79,.25)}
.hero::before{content:"";position:absolute;top:-40%;right:-20%;width:500px;height:500px;background:radial-gradient(circle,rgba(255,255,255,.08) 0%,transparent 70%);border-radius:50%}
.hero h1{margin:0 0 10px;font-size:28px;font-weight:800;position:relative}
.hero p{margin:0;font-size:15px;opacity:.85;position:relative;line-height:1.6}
.section-title{font-size:16px;font-weight:700;color:var(--text);margin:32px 0 14px;padding-bottom:10px;border-bottom:2px solid var(--line);display:flex;align-items:center;gap:8px}
.section-title::before{content:"";display:inline-block;width:4px;height:16px;background:linear-gradient(180deg,var(--accent),#52b788);border-radius:2px}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px 20px;margin-bottom:12px;transition:all .2s ease;box-shadow:var(--shadow)}
.card:hover{border-color:#b7e4c7;transform:translateY(-2px);box-shadow:var(--shadow-hover)}
.card h2{margin:0 0 6px;font-size:16px;line-height:1.45;font-weight:650}
.card h2 a{color:var(--text);text-decoration:none;transition:color .15s}
.card h2 a:hover{color:var(--accent)}
.meta{font-size:12px;color:var(--muted);display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.orig{font-size:11px;color:#94a3b8;margin:4px 0 0;font-style:italic}
.excerpt{color:#475569;font-size:13.5px;margin:8px 0 0;line-height:1.6}
.foot{font-size:13px;margin-top:10px;display:flex;gap:14px;align-items:center}
.ext{color:var(--accent);text-decoration:none;font-weight:500}
.ext:hover{text-decoration:underline}
.comments{color:var(--muted)}
.badge{font-size:11px;padding:2px 8px;border-radius:999px;font-weight:600}
.badge.hot{background:var(--hot-light);color:var(--hot)}
.badge.pin{background:var(--gold-light);color:var(--gold)}
.src{background:var(--accent-light);color:var(--accent);padding:2px 8px;border-radius:6px;font-weight:500}
.article{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:28px 32px;box-shadow:var(--shadow)}
.article h1{margin:0 0 12px;font-size:24px;font-weight:800;line-height:1.35}
.article .meta{margin-bottom:20px;font-size:13px}
.article-body{font-size:15px;line-height:1.8}
.article-body img{max-width:100%;border-radius:var(--radius-sm)}
.article-body a{color:var(--accent)}
.article .lead{font-size:15px;color:var(--text);background:linear-gradient(135deg,var(--accent-light) 0%,#edf7ed 100%);border-left:3px solid var(--accent);padding:14px 16px;border-radius:0 var(--radius-sm) var(--radius-sm) 0;margin:16px 0;line-height:1.7}
.orig-wrap{margin:20px 0;border:1px solid var(--line);border-radius:var(--radius-sm);overflow:hidden}
.orig-wrap summary{cursor:pointer;padding:12px 16px;background:#f8fafc;font-size:13px;color:var(--muted);user-select:none;transition:background .15s}
.orig-wrap summary:hover{background:#f1f5f9;color:var(--accent)}
.orig-wrap .orig-title{font-size:13px;color:#94a3b8;font-style:italic;margin:0 0 10px}
.orig-body{padding:0 16px 16px;color:#475569;font-size:13px;line-height:1.7}
.orig-body img{max-width:100%}
a.back{display:inline-flex;align-items:center;gap:4px;margin-bottom:18px;color:var(--accent);text-decoration:none;font-size:14px;font-weight:500;padding:6px 12px;border:1px solid var(--line);border-radius:var(--radius-sm);transition:all .15s}
a.back:hover{background:var(--accent-light);border-color:#b7e4c7}
.site-foot{border-top:1px solid var(--line);color:var(--muted);font-size:12.5px;padding:24px 0;text-align:center;background:rgba(255,255,255,.6)}
.qq-line{margin-top:8px;font-size:12.5px}
.qq-trigger{position:relative;display:inline-block;cursor:pointer;color:var(--accent);font-weight:600;border-bottom:1px dashed var(--accent);transition:color .15s}
.qq-trigger:hover{color:#1b4332}
.qq-popup{display:none;position:absolute;left:50%;bottom:140%;transform:translateX(-50%);z-index:50;flex-direction:column;align-items:center;gap:6px;padding:12px;background:#fff;border:1px solid var(--line);border-radius:var(--radius);box-shadow:0 12px 32px rgba(0,0,0,.15);white-space:nowrap}
.qq-trigger:hover .qq-popup,.qq-trigger:focus .qq-popup{display:flex}
.qq-qr-img{width:140px;height:140px;object-fit:contain;border:1px solid var(--line);border-radius:8px;padding:4px;background:#fff;display:block}
.qr-tip{font-size:11px;color:var(--muted)}
.not-found{text-align:center;padding:80px 20px}
.nf-icon{font-size:140px;font-weight:900;color:var(--accent);line-height:1;margin-bottom:16px;opacity:.1;letter-spacing:-8px}
.not-found h1{margin:0 0 12px;font-size:26px;font-weight:700}
.not-found > p{color:var(--muted);margin:0 0 36px;font-size:15px}
.nf-links{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-bottom:28px}
.nf-btn{display:inline-flex;align-items:center;gap:6px;padding:12px 28px;background:#fff;border:1px solid var(--line);border-radius:var(--radius-sm);color:var(--text);text-decoration:none;font-size:14px;font-weight:500;transition:all .2s;box-shadow:var(--shadow)}
.nf-btn:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-light);transform:translateY(-1px);box-shadow:var(--shadow-hover)}
.nf-auto{font-size:13px;color:var(--muted)}
.empty{color:var(--muted);padding:40px 0;text-align:center;font-size:15px}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
body{animation:fadeIn .3s ease}
.card{animation:fadeIn .3s ease backwards}
.card:nth-child(1){animation-delay:.05s}
.card:nth-child(2){animation-delay:.1s}
.card:nth-child(3){animation-delay:.15s}
.card:nth-child(4){animation-delay:.2s}
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
<footer class="site-foot"><div class="wrap">© {{year}} {{site_title}} · 内容聚合自 RageZone FlyFF Releases，版权归原作者所有{{qq_line}}</div></footer>
</body>
</html>"""


def render_page(cfg, page_title, content, nav_active="", assets_path="assets/", base="root"):
    def navcls(k):
        return ' class="active"' if nav_active == k else ""

    # 根据页面所在层级，生成正确的相对导航路径
    if base == "news":
        home_href, news_href, know_href = "../index.html", "index.html", "../knowledge/index.html"
    elif base == "knowledge":
        home_href, news_href, know_href = "../index.html", "../news/index.html", "index.html"
    else:  # root
        home_href, news_href, know_href = "index.html", "news/index.html", "knowledge/index.html"

    head = (
        '<header class="site-head"><div class="wrap">'
        f'<a class="brand" href="{home_href}">{esc(cfg["site"]["title"])}</a>'
        "<nav>"
        f'<a href="{home_href}"{navcls("home")}>首页</a>'
        f'<a href="{news_href}"{navcls("news")}>新闻/发布</a>'
        f'<a href="{know_href}"{navcls("know")}>知识库</a>'
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
                f'<span class="qq-popup">'
                f'<img class="qq-qr-img" src="{esc(assets_path + qr)}" '
                f'alt="站长 QQ 二维码（{esc(qqname or qq)}）">'
                f'<span class="qr-tip">手机扫一扫，添加站长 QQ：{esc(qq)}'
                + (f"（{esc(qqname)}）" if qqname else "")
                + "</span></span>"
            )
        qq_line = (
            f'<div class="qq-line">'
            f'<span class="qq-trigger">{esc(tip)}{qr_html}</span>'
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


def news_card(it, cfg, link_prefix="news/"):
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
  <h2><a href="{esc(link_prefix)}{esc(it.get("slug",""))}.html">{esc(title)}</a></h2>
  {orig_line}
    <p class="excerpt">{esc(excerpt)}</p>
  <div class="foot"><a class="ext" href="{esc(it.get("url",""))}" target="_blank" rel="noopener">查看原文 ↗</a>{comments}</div>
</article>'''


def know_card(it, link_prefix="knowledge/"):
    pin = '<span class="badge pin">置顶</span>' if it.get("pinned") else ""
    return f'''<article class="card">
  <div class="meta"><span class="src">{esc(it.get("tag","知识"))}</span>{pin}</div>
  <h2><a href="{esc(link_prefix)}{esc(it.get("slug",""))}.html">{esc(it.get("title",""))}</a></h2>
  <p class="excerpt">{esc(it.get("excerpt",""))}</p>
</article>'''


def article_page(cfg, it, kind, assets_path="assets/"):
    body = it.get("body_html") or it.get("body") or ""
    meta = (
        f'<div class="meta"><span class="date">{esc(it.get("date",""))}</span>'
        f'<span class="src">{esc(it.get("source",""))}</span>'
        f'<span class="author">{esc(it.get("author",""))}</span></div>'
    )
    back = "index.html" if kind == "news" else "index.html"
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
    src_url = it.get("source_url") or it.get("url", "")
    # 默认展示外链；显式 link_source=false，或来源为将下架的 flyffstart.com 时不展示
    show_link = it.get("link_source", True) and "flyffstart.com" not in src_url
    foot = (
        f'<p class="foot"><a class="ext" href="{esc(src_url)}" '
        f'target="_blank" rel="noopener">查看原文 ↗</a></p>'
        if (src_url and show_link) else ""
    )
    content = (
        f'<a class="back" href="{back}">← 返回{label}</a>'
        '<article class="article">'
        f"<h1>{esc(title)}</h1>{meta}"
        f"{body_html}"
        f"{foot}"
        "</article>"
    )
    return render_page(
        cfg, title, content,
        "news" if kind == "news" else "know", assets_path,
        "news" if kind == "news" else "knowledge",
    )


def render_404(cfg):
    """生成 404 页面，包含导航栏、页脚和视觉设计"""
    def navcfg(k):
        return ' class="active"' if k == "home" else ""

    home_href, news_href, know_href = "index.html", "news/index.html", "knowledge/index.html"
    head = (
        '<header class="site-head"><div class="wrap">'
        f'<a class="brand" href="{home_href}">{esc(cfg["site"]["title"])}</a>'
        "<nav>"
        f'<a href="{home_href}"{navcfg("home")}>首页</a>'
        f'<a href="{news_href}"{navcfg("news")}>新闻/发布</a>'
        f'<a href="{know_href}"{navcfg("know")}>知识库</a>'
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
                f'<span class="qq-popup">'
                f'<img class="qq-qr-img" src="assets/{esc(qr)}" '
                f'alt="站长 QQ 二维码（{esc(qqname or qq)}）">'
                f'<span class="qr-tip">手机扫一扫，添加站长 QQ：{esc(qq)}'
                + (f"（{esc(qqname)}）" if qqname else "")
                + "</span></span>"
            )
        qq_line = (
            f'<div class="qq-line">'
            f'<span class="qq-trigger">{esc(tip)}{qr_html}</span>'
            + "</div>"
        )
    else:
        qq_line = ""

    footer = (
        f'<footer class="site-foot"><div class="wrap">'
        f"© {datetime.now().year} {esc(cfg['site']['title'])} · "
        "内容聚合自 RageZone FlyFF Releases，版权归原作者所有"
        f"{qq_line}"
        "</div></footer>"
    )

    # 404 内容区域
    content = (
        '<section class="not-found">'
        '<div class="nf-icon">404</div>'
        '<h1>页面不存在</h1>'
        '<p>抱歉，您访问的页面已搬家或暂时无法找到</p>'
        '<div class="nf-links">'
        f'<a href="{home_href}" class="nf-btn">返回首页</a>'
        f'<a href="{news_href}" class="nf-btn">浏览新闻</a>'
        f'<a href="{know_href}" class="nf-btn">知识库</a>'
        '</div>'
        '<p class="nf-auto">页面即将自动跳转…</p>'
        '</section>'
    )

    page = (
        f'<!DOCTYPE html>\n'
        f'<html lang="zh-CN">\n'
        f'<head>\n'
        f'<meta charset="utf-8">\n'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f'<title>页面不存在 · {esc(cfg["site"]["title"])}</title>\n'
        f'<meta name="description" content="{esc(cfg["site"]["subtitle"])}">\n'
        f'<style>{CSS}</style>\n'
        '</head>\n'
        f'<body>\n'
        f'{head}\n'
        f'<main class="wrap">{content}</main>\n'
        f'{footer}\n'
        f'<script>window.location.replace("{home_href}");</script>\n'
        f'</body>\n'
        f'</html>'
    )

    return page


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
    latest = "".join(news_card(n, cfg, "news/") for n in news[:8]) or '<p class="empty">暂无新闻，运行 collect.py 采集。</p>'
    know_list = "".join(know_card(k, "knowledge/") for k in know) or '<p class="empty">暂无知识库内容。</p>'
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
        "".join(news_card(n, cfg, "") for n in news)
        or '<p class="empty">暂无内容。</p>'
    )
    (PUBLIC_N / "index.html").write_text(
        render_page(cfg, "新闻/发布", news_index, "news", "../assets/", "news"), encoding="utf-8"
    )

    # 新闻详情页
    for n in news:
        (PUBLIC_N / f"{n['slug']}.html").write_text(
            article_page(cfg, n, "news", "../assets/"), encoding="utf-8"
        )

    # 知识库列表页
    know_index = '<h1>知识库</h1>' + (
        "".join(know_card(k, "") for k in know) or '<p class="empty">暂无内容。</p>'
    )
    (PUBLIC_K / "index.html").write_text(
        render_page(cfg, "知识库", know_index, "know", "../assets/", "knowledge"), encoding="utf-8"
    )

    # 知识库详情页
    for k in know:
        (PUBLIC_K / f"{k['slug']}.html").write_text(
            article_page(cfg, k, "know", "../assets/"), encoding="utf-8"
        )

    print(
        f"构建完成：{len(news)} 条新闻、{len(know)} 篇知识，已输出到 public/。"
    )

    # 生成 404 页面
    (PUBLIC / "404.html").write_text(
        render_404(cfg), encoding="utf-8"
    )
    print("已生成 404.html")


if __name__ == "__main__":
    build()
