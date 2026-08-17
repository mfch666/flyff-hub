#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性脚本：把 20 条已采集的 RageZone 英文原文，用准确中文重写标题与摘要。
按 slug（链接序号）匹配。运行后 needs_translation 置为 false。
之后每周新增条目由自动化里的 agent 翻译（collect.py 已标记 needs_translation=true）。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NEWS = ROOT / "content" / "news"

ZH = {
    "1269016": {
        "title_zh": "Reborn MMO 最终公开版发布",
        "excerpt_zh": "作者 Zacks 放出约四个月前版本的 Reborn-MMO 服务端文件，已验证可正常运行，包含多项系统。",
        "summary_zh": "这是 Zacks 发布的 Reborn-MMO 最终公开版本，文件源自约四个月前的版本，经测试可正确运行。该版本包含了世界模型、任务与多项系统改进，适合想搭建 Reborn 系私服的开发者使用。",
    },
    "1235278": {
        "title_zh": "【VS2022】FlyFF v21 源码（免费公开）",
        "excerpt_zh": "此前在其它论坛付费隐藏的 FlyFF v21 源码现已免费公开，支持 Visual Studio 2022 / SQL Server 2019 / Win10-11。",
        "summary_zh": "作者 Poreotix 将原本在其它论坛付费隐藏的 FlyFF v21 完整源码搬运并免费放出。已测试可运行于 Visual Studio Community 2022、SQL Server 2019 Standard 以及 Windows 10/11 专业版，并附带安装说明。",
    },
    "950576": {
        "title_zh": "Atlas Beast 整合包（Repack）",
        "excerpt_zh": "包含约半数的魔兽世界（含 TBC/WotLK/Cata）世界模型，体积更精简，由 Adler 发布。",
        "summary_zh": "Adler 发布的 Atlas Beast 整合包，集成了大约一半来自《魔兽世界》及其资料片（燃烧的远征、巫妖王之怒、大地的裂变）的世界模型，并对资源做了精简压缩，便于在 FlyFF 中使用。",
    },
    "1211433": {
        "title_zh": "【Florist 文件】完整整合包",
        "excerpt_zh": "Zacks 重新发布 Florist 全套文件，含 ServerCommon.h，部分链接需登录或密码查看。",
        "summary_zh": "Zacks 重新放出 Florist 全套服务端文件，包含 ServerCommon.h 等关键文件。部分下载链接需要登录论坛或输入密码（密码为 RageZone）才能查看。",
    },
    "1265455": {
        "title_zh": "官网 Node.js 重构版 V2",
        "excerpt_zh": "官网完成整体重构并集成 PayPal 排行榜系统，修复多项问题、增强稳定性，由 Zacks 发布。",
        "summary_zh": "Zacks 完成了官网的第二次大版本重构：整体重写前端，并集成 PayPal 充值排行榜系统。网站经过大量修复与新系统加入，稳定性与性能显著提升（使用 PM2 进程管理）。",
    },
    "1207559": {
        "title_zh": "【发布】BBeast 与地图资源",
        "excerpt_zh": "Iapin 发布的 BBeast 与地图相关资源（公告性质）。",
        "summary_zh": "Iapin 发布的 BBeast 及配套地图资源，属于该系列的资源放出帖，内容偏宣传性质，供有需要的开发者取用。",
    },
    "1233232": {
        "title_zh": "【VS2022】Caleb FlyFF 源码",
        "excerpt_zh": "基于较早泄露的 Florist 文件构建，支持 VS2022 / SQL2019 / Win10-11，作者 Poreotix。",
        "summary_zh": "Poreotix 发布的 Caleb FlyFF 源码，基于较早泄露的 Florist 旧文件改造而成（作者声明不占有版权）。已测试可运行于 Visual Studio 2022、SQL Server 2019 与 Windows 10/11 专业版，并附截图。",
    },
    "1260864": {
        "title_zh": "FlyFF v21 原生 x64 移植（仅开发版）",
        "excerpt_zh": "Bodyroro 分享将 FlyFF v21 源码完整迁移到原生 64 位的开发项目，目前仅限开发用途。",
        "summary_zh": "Bodyroro 分享了一个仍在开发中的项目：将 FlyFF v21 源码完整迁移到原生 64 位（x64）架构。该项目基于 v21 原始源码，目前处于开发阶段，仅供开发与测试参考。",
    },
    "1233599": {
        "title_zh": "【VS2022】Sakura 项目（自定义 v18）",
        "excerpt_zh": "Poreotix 自研项目，基于自定义 v18，可切换 V19 与 8 套自定义界面，源码已更新至 VS22（兼容 VS26）。",
        "summary_zh": "Poreotix 的私人项目 Sakura，基于自定义 v18 版本，支持在 V19 与 8 套自定义界面之间切换。源码已全面更新到 Visual Studio 2022（并兼容 VS26），包含 GameGuard 等内容；若解压遇到问题建议使用 7zip。",
    },
    "1233223": {
        "title_zh": "【VS2026】FlyFF v18 自定义版",
        "excerpt_zh": "Ketchup 自定义 v18 文件的更新版，源码升级至 VS2026，由 Poreotix 发布。",
        "summary_zh": "Poreotix 放出了 Ketchup 自定义 v18 文件的更新版本，源码已全面升级到 Visual Studio 2026。帖子注明内容复制自原帖，并附带一套安装配置指南供新手参考。",
    },
    "1233513": {
        "title_zh": "【VS2022】Florist 文件（2024 年第二季度）",
        "excerpt_zh": "基于 Florist 自定义 v18 构建，荣誉归 Florist，支持 VS2022 / SQL2019 / Win10-11。",
        "summary_zh": "Poreotix 发布的 Florist 文件（2024 Q2 版），是一套基于 Florist 自定义 v18 构建的服务端，全部荣誉归 Florist。已测试可运行于 Visual Studio 2022、SQL Server 2019 与 Windows 10/11 专业版。",
    },
    "1260214": {
        "title_zh": "小功能发布：随机天气",
        "excerpt_zh": "Soturi1991 放出随机天气的源码改动，支持落叶慢/快与下雨，每 2–5 分钟随机切换。",
        "summary_zh": "Soturi1991 分享了一个轻量级的随机天气源码改动：包含落叶（慢/快）与下雨效果，每 2–5 分钟随机切换一次（间隔可自定义）。通过新增宏 __RANDOM_WEATHER 启用。",
    },
    "1252938": {
        "title_zh": "【更新】Majestics FlyFF V3",
        "excerpt_zh": "Zacks 修复了该版本全部崩溃问题并经过测试，基于旧 Majestics V2 增加了部分内容。",
        "summary_zh": "Zacks 修复了 Majestics FlyFF V3 文件中的所有崩溃问题并进行了测试验证，同时基于旧版 Majestics V2 服务端文件做了少量新增。作者已转做其它项目、暂时不再维护 FlyFF，放出供社区使用。",
    },
    "1263932": {
        "title_zh": "Florist 自定义文件 V2",
        "excerpt_zh": "Zacks 分享 2024 年 Florist Files V2，已修复 AEGON_CRAFTING、WEAPON_RARITY 等复制漏洞，经 4 个月线上测试。",
        "summary_zh": "Zacks 分享其 2024 年的 Florist Files V2，针对新增系统相关的复制漏洞（包括 AEGON_CRAFTING、WEAPON_RARITY 等）全部做了修复。该文件曾进行长达 4 个月的线上实测，稳定性较好。",
    },
    "1233007": {
        "title_zh": "【VS2022】FlyFF v19 源码",
        "excerpt_zh": "Ketchup 干净版 v19 文件的更新版，源码升级至 VS22，由 Poreotix 发布。",
        "summary_zh": "Poreotix 放出了 Ketchup 干净版 v19 文件的更新版本，源码已全面升级到 Visual Studio 2022。帖子注明内容复制自原帖，并附带安装配置指南供新手参考。",
    },
    "1269152": {
        "title_zh": "【发布/教程】Florist 商城管理器集成",
        "excerpt_zh": "新手 engrspade 分享一个轻量独立的 Win32 C++ 商城（Item Mall）管理工具，基于 Zacks 的干净 Florist 源码。",
        "summary_zh": "社区新人 engrspade 分享了一个轻量、独立运行的 Win32 C++ 商城（Item Mall）管理工具，用于配合 Florist 服务端管理道具商城。作者特别感谢 Zacks 提供的干净 2026 Florist 源码。",
    },
    "1263989": {
        "title_zh": "Florist 2026 完整文件（新版）",
        "excerpt_zh": "Zacks 放出完整的 Florist 2026 服务端文件（部分链接需登录查看）。",
        "summary_zh": "Zacks 放出了完整的 Florist 2026 服务端文件，包含完整配置（如版本宏 __VER 18、本地测试宏等）。部分下载内容需要登录论坛后才能查看。",
    },
    "1180343": {
        "title_zh": "时装 / 外观讨论帖",
        "excerpt_zh": "新人 Fiddly 分享 Flyff 私服中的时装模型研究，专注游戏内模型与外观制作。",
        "summary_zh": "Fiddly 作为论坛新人，在自行研究 Flyff 私服的过程中专门投入于时装与外观方向，并在逐渐掌握游戏内模型导入结构后，持续分享相关成果与心得。",
    },
    "1265897": {
        "title_zh": "【Reborn V2】重制版",
        "excerpt_zh": "Zacks 发布最新修正版文件，非常稳定干净，但说明仍为法文（作者为法国人），含自研 CODEX 等系统。",
        "summary_zh": "Zacks 发布其最新修正版 Reborn V2 文件，整体非常稳定、干净。由于作者是法国人，当前说明文字仍为法文。该版本包含作者自研的多数系统，如 Factors 系统、自有 CODEX 系统等。",
    },
    "1254580": {
        "title_zh": "升级版 Florist FlyFF",
        "excerpt_zh": "DevtopZ 借助 VS2022 中的 ChatGPT 与 Copilot 将 Florist FlyFF 改造成一个简单模块并分享。",
        "summary_zh": "DevtopZ 分享其升级版 Florist FlyFF，作者借助 Visual Studio 2022 中的 ChatGPT 与 Copilot，将功能封装成一个简单模块。帖子附有相关链接供取用。",
    },
}

n = 0
for f in sorted(NEWS.glob("*.json")):
    rec = json.loads(f.read_text(encoding="utf-8"))
    slug = rec.get("slug", "")
    if slug in ZH:
        rec.update(ZH[slug])
        rec["needs_translation"] = False
        f.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
        n += 1
        print("zh+", slug, rec["title_zh"][:30])
    else:
        print("MISS", slug, rec.get("title", ""))
print(f"\n已写入中文 {n} 条。")
