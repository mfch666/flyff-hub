# Flyff 知识站（AI 低频自动运营 · 中文整理）

纯静态站点 + Python 采集/构建脚本。内容**仅**来自：
- **RageZone FlyFF Releases**（RSS，稳定主线，含技术发布、私服源码、热门讨论，带评论数可标「热门」）

英文原文由 AI 用**准确中文**重写标题与摘要后发布，详情页顶部为中文描述，下方折叠「原文（English）」保留原始出处。

## 目录结构
```
flyff-hub/
├── config.json          # 站点信息、采集源（仅 RageZone）、热门阈值
├── collect.py           # 采集器：写 content/news/*.json + state/seen.json（去重）
├── translate_seed.py    # 一次性脚本：把已采集英文原文批量注入中文翻译
├── build.py             # 静态站生成器：读 JSON → public/*.html（中文为主）
├── content/
│   ├── news/            # 采集结果（自动；含 title_zh / excerpt_zh / summary_zh）
│   └── knowledge/       # 知识库种子（手动维护 JSON）
├── state/seen.json      # 去重索引
└── public/              # 构建产物（部署目录）
```

## 本地运行
```bash
python collect.py     # 采集 RageZone 最新 RSS（新条目标记 needs_translation=true）
python build.py       # 生成 public/
# 预览：用任意静态服务器打开 public/，例如：
python -m http.server 8080 --directory public
```
> 新采集的条目需先有中文（title_zh / excerpt_zh / summary_zh）才会以中文展示。
> 历史 20 条已用 `translate_seed.py` 注入；后续每周新增条目由自动化里的 agent 翻译。

## 部署到 EdgeOne Makers（静态，免费）
1. 在 GitHub / GitLab 新建仓库，把本目录（含 public/）推上去：
   ```bash
   git init
   git add -A
   git commit -m "init flyff hub"
   git remote add origin <你的仓库地址>
   git push -u origin main
   ```
2. 打开 [EdgeOne Makers 控制台](https://edgeone.ai/products/makers)，新建项目 → 连接 Git 仓库 → 选择该仓库。
3. 框架选 **其他 / 静态**，构建命令留空（或填 `echo ok`），**输出目录填 `public`**，绑定域名（可选，免费 SSL 自动签发）。
4. 之后每次推送，Makers 自动重新部署 `public/` 静态文件。

> 由于 Makers 构建环境不一定带 Python，本方案让**所有逻辑都在本地/自动化里跑完，只把纯静态的 `public/` 推上去部署**，最稳。

## 让 AI 全权运营（周级自动化）
用 WorkBuddy 的「自动化」建一个**每周**任务，prompt 大致为：
> 进入 flyff-hub 目录，运行 `python collect.py` 采集 RageZone 最新 RSS；遍历 content/news 下所有 *.json，把 needs_translation=true 的新条目用准确中文重写（title_zh 标题、excerpt_zh 摘要、summary_zh 描述，保留版本号/引擎名/文件名），写回并把 needs_translation 设为 false；再运行 `python build.py` 重建 public/；最后 `git add -A && git commit -m "auto update" && git push` 触发 EdgeOne 重新部署。任一步失败需在结果里说明原因，不要静默。

（git push 需要你事先在仓库 remote 里配置好带权限的凭据/Token。）

## 频率与扩展
- 采集频率在自动化里调（RRULE：每周 / 每 3 天均可）。当前默认低频。
- 想做站内搜索 / 评论 / 动态 API：Makers 支持 Edge Functions / Cloud Functions，可在同项目扩展。
