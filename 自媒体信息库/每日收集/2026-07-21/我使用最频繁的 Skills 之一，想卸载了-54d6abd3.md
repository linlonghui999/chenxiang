---
title: "我使用最频繁的 Skills 之一，想卸载了"
source: "人人都是产品经理"
url: "https://www.woshipm.com/ai/6432655.html"
published: "2026-07-20T07:01:57+00:00"
collected: "2026-07-21T02:32:09+08:00"
category: "AI工具"
relevance: 2
status: "待阅读"
tags:
  - 自媒体信息
  - AI工具
type: "source"
domain: "自媒体"
maturity: "seed"
up: "[[02-主题地图/自媒体 MOC]]"
map: "[[02-主题地图/自媒体/自媒体-AI工具 MOC]]"
---

# 我使用最频繁的 Skills 之一，想卸载了

## 信息摘要

我有点想把 Codex 里的 Superpowers 卸载了 看了一下记录，我几乎每天都在用它 今年 3 月，我还在《最被低估的 Skills》里夸它是最完整的 AI 编程工作流 当时模型容易一言不合就开写，Superpowers 强制先聊需求、写计划、做 TDD 和 Review，确实能拦住很多返工 可模型又升级了一轮，Codex 自己也有了 Plan mode、SubAgent、Review 和验证流程 Superpowers 依然优秀，只是它开始显得太勤快了 好纪律，正在变成默认税 我重看了最新版 using-superpowers 的规则，只要有 1% 的可能命中某个 skill，就必须先调用，连进入 Plan mode 前都要检查是否做过 brainstorming，这个也解释了前面调用排行图中 Superpowers 和 brainstorming 几乎绑定出现 问题不只在大量消耗 token 我原本想做一个小修改，它却先把对话切进另一套流程，规划、提问、子 Agent、Review 一层层叠上来，工作节奏也被接管了 强制流程很像工程保险，高风险项目值得买，每次对话都自动续费就不划算 我更喜欢一把手术刀 最近 Matt Pocock 的 grill-me 和 grill-with-docs 突然又被炒起来了 Matt 做过 Total TypeScript 和 ts-reset ，我之前也写过他的开源 Skills：顶级大佬把 .claude 目录里的 Skills 全开源了，说实话当时并未特别在意 grilling 和 grill-with-docs # 安装 Matt 这套 Skills 只需要一条命令 npx skills@latest add mattpocock/skills # 如果只想先试两个核心 Skills，也可以单独安装 npx skills add mattpocock/skills --skill=grill-me npx skills add mattpocock/skills --skill=grill-with-docs 与SuperPowers 动辄几百行 Prompt 不同， grill-me 和 grill-with-docs 这两个入口文件都只有 7 行，共用的 grilling 也只有 12 行 它没有试图给模型再上一门软件工程课，只规定了几件关键小事：一次问一个问题，附上推荐答案，代码库能查到的事实自己查，需要拍板的决定交给人，双方确认理解一致后才能执行 我认为这才是强模型时代 skill 最有价值的地方 模型已经会写代码，真正稀缺的是 在动手前把决定问对，并且知道哪里必须停下来等人拍板 更合我胃口的是，它默认不会自己跳出来，你点名才启动 工具平时安静，关键时刻再锋利，这种手感舒服得多 grill-with-docs 真正值钱的东西 grill-with-docs 在追问过程中还会维护 CONTEXT.md 和 ADR 前者把项目里的黑话变成统一语言，后者只记录难回头、有真实取舍的关键决定 很多 Agent 文档写得很长，下一次对话照样要重新解释 这两个文件把一次性对话变成可复用的决策资产，也让后面的 to-spec → to-tickets → implement 越跑越省力 我看重的也正是这一点 好的工作流应该沉淀决策资产，同时把控制权留在人手里 我的新选择 强模型时代按任务风险选择 AI 编程工作流 小修改直接做，需求清楚就用 Plan mode，想法里藏着很多分支就开 grill-with-docs 遇到高风险重构，我依然愿意调用 Superpowers 里的 TDD、系统调试和 Review，只是不再让整套框架常驻每次对话 总结 我准备先停用 Superpowers 一周 普通任务交给 Codex 原生能力，模糊决策交给 grill-with-docs ，严格工程纪律按需补上，如果质量明显下降，再装回来也只要一分钟

## 可用选题方向

- 工具能解决哪个真实创作问题
- 人工流程和AI流程的效果对比
- 普通创作者的低成本使用方法

## 创作记录

- 核心观点：
- 可信依据：
- 适合形式：图文 / 短视频 / 直播
- 目标受众：

## 原文

[人人都是产品经理](https://www.woshipm.com/ai/6432655.html)

## 知识连接

- 主题入口：[[02-主题地图/自媒体 MOC|自媒体 MOC]]，用于回到自媒体知识全景。
- 分类地图：[[02-主题地图/自媒体/自媒体-AI工具 MOC|AI工具地图]]，因为本资料归入“AI工具”。
- 提炼动作：把可复用结论写成独立卡片，并明确证据、适用边界和关联内容。
