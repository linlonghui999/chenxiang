# 沉香信息收集系统

这是一个面向沉香自媒体创作者的本地信息收集工具。它从公开新闻 RSS 和 PubMed 科研数据库收集与沉香、奇楠、莞香、Aquilaria、agarwood 相关的信息，自动去重、分类，并保存为 Obsidian 可以直接阅读的 Markdown 笔记。

## 功能

- 收集沉香新闻、市场、文化、产区、政策和科研信息
- 使用 SQLite 自动去重，避免重复保存同一内容
- 按主题自动分类并计算相关度
- 每条信息生成独立 Obsidian 笔记
- 自动更新“信息总览”和“选题池”
- 不需要付费 API 密钥即可运行
- 支持 Windows 计划任务定时执行

## 目录结构

运行后会在 Obsidian 中生成：

```text
沉香信息库/
├─ 信息总览.md
├─ 选题池.md
└─ 每日收集/
   └─ 2026-07-21/
      ├─ 示例信息一.md
      └─ 示例信息二.md
```

## 快速开始

1. 确认电脑已经安装 Python 3.10 或更高版本。
2. 将 `config.example.json` 复制为 `config.json`。
3. 把 `vault_path` 改为你的 Obsidian 知识库路径。
4. 双击 `run_collect.bat`，或执行：

```powershell
py -3 collector.py --config config.json
```

程序只使用 Python 标准库，无需安装额外依赖。

## 自定义信息来源

在 `config.json` 的 `sources` 数组中添加 RSS 地址：

```json
{
  "name": "我的沉香来源",
  "type": "rss",
  "url": "https://example.com/feed.xml"
}
```

也可以添加新的 PubMed 查询：

```json
{
  "name": "PubMed-沉香科研",
  "type": "pubmed",
  "query": "agarwood OR Aquilaria"
}
```

## 数据与隐私

- 抓取状态保存在本机 `data/collector.db`。
- 收集结果直接写入配置的 Obsidian 知识库。
- 程序不会上传你的 Obsidian 笔记。
- `config.json` 和运行数据不会提交到 GitHub。

## 可选增强

基础版本不需要密钥。后续可以接入 OpenAI 或其他兼容接口，为每条信息生成中文摘要、短视频选题、标题和口播提纲。建议先确认基础收集结果符合需求，再配置 AI 密钥。
