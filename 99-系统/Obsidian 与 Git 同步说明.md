---
title: "Obsidian 与 Git 同步说明"
type: "system"
status: "持续更新"
created: "2026-07-22"
updated: "2026-07-22"
up: "[[00-知识库入口/知识库总览]]"
tags:
  - Obsidian
  - Git
  - 同步
---

# Obsidian 与 Git 同步说明

> 当前状态：本知识库已经初始化为本地 Git 仓库，并已关联远程仓库。  
> 远程仓库：`https://github.com/linlonghui999/chenxiang.git`

## 1. 已完成

- 已初始化本地 Git 仓库。
- 已设置 Git 中文路径显示。
- 已关联远程仓库：`origin -> https://github.com/linlonghui999/chenxiang.git`
- 已确认远程仓库存在 `main` 分支。
- 已将本地分支建立在远程 `main` 历史之上，避免覆盖远程已有采集系统。
- 已更新 `.gitignore`，避免同步本地工作区状态、缓存、AI 凭据和 Claudian 会话目录。

## 2. 推荐同步范围

建议纳入 Git：

- 笔记正文：`*.md`
- Bases 文件：`*.base`
- 模板：`90-模板/`
- 系统规则：`99-系统/`
- 主题地图、提炼卡片、项目中心
- 大部分 `.obsidian/` 配置，便于恢复插件和界面设置

建议忽略：

- `.obsidian/workspace*`
- `.obsidian/cache/`
- `.trash/`
- `.claudian/`
- 本地 AI 插件凭据和备份
- 临时文件、备份文件

## 3. 远程仓库情况

远程仓库已有内容：

- `README.md`
- `collector.py`
- `config.example.json`
- `requirements.txt`
- `run_collect.bat`
- `资料/大地瑰宝/`

这些内容会被保留。本地 Obsidian vault 会作为新增内容叠加到 `main` 分支上。

## 4. 如需更换远程仓库，还需要你提供

任选一种远程仓库方式：

### 方式 A：已有远程仓库

请提供：

```text
远程仓库地址：
HTTPS 或 SSH：
仓库是空仓库还是已有内容：
默认分支名：main / master / 其他
```

示例：

```text
https://github.com/你的用户名/你的仓库名.git
git@github.com:你的用户名/你的仓库名.git
```

### 方式 B：还没有远程仓库

你需要先在 GitHub/Gitee 创建一个**空仓库**，然后把地址发给我。

建议：

- 仓库设为 Private。
- 不要在线创建 README、.gitignore、LICENSE，避免第一次推送冲突。
- 仓库名可用 `lin-obsidian-vault`、`knowledge-base`、`林的知识库` 等。

## 5. 认证条件

### HTTPS

需要：

- Git 平台账号。
- Personal Access Token，不能用普通密码。
- Token 至少需要仓库读写权限。

### SSH

需要：

- 本机已有 SSH key。
- 公钥已添加到 GitHub/Gitee。
- 远程地址使用 `git@...` 格式。

## 6. 推送前建议

在第一次推送前，建议先做一次本地提交：

```text
git add .
git commit -m "初始化 Obsidian 知识库"
git branch -M main
git remote add origin <远程仓库地址>
git push -u origin main
```

如果远程仓库已有内容，需要先审查是否会冲突，不建议直接强推。

## 7. Obsidian 插件建议

可以安装并使用 Obsidian 社区插件 **Obsidian Git**。

建议设置：

- 自动拉取：打开 Obsidian 时 pull。
- 自动提交间隔：30–60 分钟。
- 自动推送：提交后 push。
- commit message：`vault backup: {{date}} {{time}}`
- 冲突处理：出现 conflict 时先停止自动同步，人工审查。

## 8. 安全原则

- 不把 API Key、Token、插件登录数据提交到仓库。
- 第一次推送前先检查 `git status`。
- 多设备同步时，打开 Obsidian 前先 pull，关闭前确认 push。
- 如果出现冲突，不要盲目选择全部保留或全部覆盖。
