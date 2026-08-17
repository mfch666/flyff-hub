# Flyff 知识站（AI 低频自动运营）

纯静态站点 + Python 采集/构建脚本。内容来自：
- **RageZone FlyFF Releases**（RSS，稳定主线，含技术发布与热门讨论，带评论数可标「热门」）
- **ruiwoo 新闻**（API 尽力采集；当前接口对服务端请求返回 500，会自动跳过，不阻断流程）

## 目录结构
```
flyff-hub/
├── config.json          # 站点信息、采集源、热门阈值
├── collect.py           # 采集器：写 content/news/*.json + state/seen.json（去重）
├── build.py             # 静态站生成器：读 JSON → public/*.html
├── content/
│   ├── news/            # 采集结果（自动）
│   └── knowledge/       # 知识库种子（手动维护，可加 Markdown/JSON）
├── state/seen.json      # 去重索引
└── public/              # 构建产物（部署目录）
```

## 本地运行
```bash
python collect.py     # 采集最新内容
python build.py       # 生成 public/
# 预览：用任意静态服务器打开 public/，例如：
python -m http.server 8080 --directory public
```

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
> 进入 flyff-hub 目录，运行 `python collect.py` 采集最新 RageZone/ruiwoo 内容，再运行 `python build.py` 重建 public/，然后 `git add -A && git commit -m "auto update" && git push` 触发 EdgeOne 重新部署。若采集或构建失败，在结果里说明原因，不要静默。

（git push 需要你事先在仓库 remote 里配置好带权限的凭据/Token。）
不想配推送时：自动化只负责采集+构建更新本地文件，你在 Makers 控制台点「重新部署」即可刷新。

## 频率与扩展
- 采集频率在 WorkBuddy 自动化里调（RRULE：每周 / 每 3 天均可）。当前默认低频。
- 想加 ruiwoo 稳定采集：可后续给 collect.py 增加无头渲染（Playwright）步骤解析其 JS 新闻列表。
- 想做站内搜索 / 评论 / 动态 API：Makers 支持 Edge Functions / Cloud Functions，可在同项目扩展。
