# agent-repository-3
# 🤖 GitHub Agent 课程项目

这是一个基于大语言模型（DeepSeek）的轻量级 Agent 项目骨架。
它不仅能聊天，还能**自主调用工具、多步规划、访问真实的 GitHub API** 来完成复杂任务。

## ✨ 核心特性

- **自主决策**：Agent 会根据你的问题，自己决定要不要用工具、用哪个工具。
- **多步执行**：支持 Think → Act → Observe 循环，直到任务完成。
- **可扩展的工具系统**：只需在 `tools.py` 中新增一个函数，无需修改 `agent.py`，模型就能自动学会使用新工具。
- **CLI 交互**：支持单次提问，也支持连续对话。

## 📁 项目结构

```text
github-agent/
├── .env.example      # 环境变量模板（复制为 .env 并填入你的密钥）
├── .gitignore        # Git 忽略配置（确保 .env 不会被提交）
├── requirements.txt  # 项目依赖
├── tools.py          # 工具层：定义 Agent 能调用的所有 GitHub API 工具
└── agent.py          # 核心逻辑：Agent 循环 + CLI 交互界面

