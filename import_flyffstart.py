"""从 flyffstart.com 首页抓取全部 thread 文章，转为知识库 JSON（带出处）。
用法：python import_flyffstart.py
"""
import urllib.request
import urllib.parse
import re
import json

BASE = "https://www.flyffstart.com/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
OUT = "content/knowledge"

TAG_CAT = {  # forum id -> 分类标签（用于 tag）
    "站内大厅": "站内大厅",
    "产品发布": "产品发布",
    "求助中心": "求助中心",
    "站务消息": "站务消息",
}


def fetch(url):
    return urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30
    ).read().decode("utf-8", "ignore")


def get_threads():
    d = fetch(BASE + "index.php")
    links = re.findall(r'href="(thread-\d+\.htm)"', d)
    seen, ordered = set(), []
    for l in links:
        if l not in seen:
            seen.add(l)
            ordered.append(l)
    return ordered


def abs_url(val):
    v = (val or "").strip()
    if not v or v.startswith(("http://", "https://", "//", "data:")):
        return v
    return urllib.parse.urljoin(BASE, v)


def rewrite_urls(html):
    def rep(m):
        attr, q, val = m.group(1), m.group(2), m.group(3)
        return f'{attr}={q}{abs_url(val)}{q}'
    return re.sub(r'(src|href)=(["\'])(.*?)\2', rep, html)


def extract_message(html):
    # 取第一个帖子正文：<div class="message break-all" isfirst="1"> ... </div>
    m = re.search(r'<div class="message break-all" isfirst="1">', html)
    if not m:
        m = re.search(r'<div class="message break-all">', html)
    if not m:
        return ""
    start = m.end()
    depth = 1
    i = start
    while i < len(html):
        if html.startswith("<div", i):
            depth += 1
            i = html.find(">", i) + 1
        elif html.startswith("</div>", i):
            depth -= 1
            i += 6
            if depth == 0:
                return rewrite_urls(html[start:i - 6])
        else:
            i += 1
    return rewrite_urls(html[start:])


def text_of(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def parse_thread(url):
    html = fetch(BASE + url)
    # 标题
    mt = re.search(r'<h4 class="break-all">(.*?)</h4>', html, re.S)
    title = re.sub(r"<[^>]+>", "", mt.group(1)).strip() if mt else ""
    if not title:
        mtt = re.search(r"<title>(.*?)</title>", html)
        title = re.sub(r"-.*$", "", mtt.group(1)).strip() if mtt else url
    # 作者
    ma = re.search(r'class="username">\s*<a[^>]*>([^<]+)</a>', html)
    author = ma.group(1).strip() if ma else ""
    # 日期
    md = re.search(r'class="date[^"]*">([^<]+)<', html)
    date = md.group(1).strip() if md else ""
    # 分类（从 <title> 后缀取，如 "...-站内大厅-起航飞飞"）
    tag = "起航飞飞"
    mcat = re.search(r"<title>.*?-([^-]+)-起航飞飞", html)
    if mcat:
        tag = mcat.group(1).strip() or "起航飞飞"
    # 正文
    body = extract_message(html)
    excerpt = text_of(body)[:120]
    slug = re.search(r"thread-(\d+)\.htm", url).group(1)
    return {
        "slug": "fs" + slug,
        "tag": tag,
        "title": title,
        "excerpt": excerpt,
        "body_html": body,
        "date": date,
        "source": "起航飞飞",
        "author": author,
        "source_url": BASE + url,
    }


def main():
    import os
    os.makedirs(OUT, exist_ok=True)
    threads = get_threads()
    print(f"发现 {len(threads)} 个帖子：{threads}")
    ok, fail = 0, []
    for t in threads:
        try:
            rec = parse_thread(t)
            if not rec["body_html"]:
                fail.append((t, "空正文"))
                continue
            path = os.path.join(OUT, rec["slug"] + ".json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(rec, f, ensure_ascii=False, indent=2)
            ok += 1
            print(f"  ✓ {rec['slug']} | {rec['title'][:40]} | {rec['tag']}")
        except Exception as e:
            fail.append((t, repr(e)))
            print(f"  ✗ {t}: {e}")
    print(f"\n完成：成功 {ok} 篇，失败 {len(fail)} 篇")
    for t, r in fail:
        print("  失败", t, r)


if __name__ == "__main__":
    main()
