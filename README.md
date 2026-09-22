# 🤖 GitHub Agent 课程项目

这是一个基于大语言模型（DeepSeek）的轻量级 Agent 项目骨架。
本项目不仅实现了简单的对话，还具备**自主调用工具、多步规划、访问真实 GitHub API** 的能力，是标准的 Agent 架构实现。

---

## 📌 核心概念：Agent 与普通聊天机器人的区别

根据课程要求，本项目通过代码实现并总结了 Agent 与普通聊天机器人的三大本质区别：

1. **是否调用工具**：普通聊天机器人只能基于模型内部知识生成文本（容易产生幻觉）；而本项目 Agent 拥有 `tools.py` 工具层，能自主调用 GitHub API 获取真实的用户资料、仓库列表和搜索结果。
2. **是否多步执行**：普通聊天机器人是“一问一答”单步结束；而本项目 Agent 实现了 `Think → Act → Observe` 的 `while` 循环（`agent.py` 中的 `run_agent` 函数），可以多次调用工具，直到任务完成。
3. **是否自主决策**：普通聊天机器人被动应答，由用户决定一切；而本项目 Agent 由大模型根据当前上下文，**自主决定**是否调用工具、调用哪个工具、传入什么参数。如果工具返回错误，模型还能自主调整策略重试。

---

## ✨ 功能特性
- **自主决策**：Agent 根据问题自己决定用不用工具、用哪个工具。
- **多步执行**：支持 Think → Act → Observe 循环，直到任务完成。
- **可扩展的工具系统**：只需在 `tools.py` 中新增函数并在 `TOOL_SCHEMAS` 中注册，模型就能自动学会使用新工具。
- **CLI 交互**：支持单次提问，也支持连续对话。

---

## 📁 项目结构

```text
github-agent/
├── .env.example      # 环境变量模板（复制为 .env 并填入密钥）
├── .gitignore        # Git 忽略配置（确保 .env 不会被提交）
├── requirements.txt  # 项目依赖
├── tools.py          # 工具层：定义 Agent 能调用的所有 GitHub API 工具
└── agent.py          # 核心逻辑：Agent 循环 + CLI 交互界面
🔐 安全配置与证据说明
本项目严格执行密钥安全规范，具体措施如下：
1. 本地已创建 .env：本地开发环境已创建 .env 文件，包含 GITHUB_TOKEN、DEEPSEEK_API_KEY 等敏感信息，供程序运行时读取。
2. .gitignore 已配置忽略：项目根目录的 .gitignore 第一行就是 .env，确保本地密钥不会被误传到 GitHub。
3. 源码无硬编码 Token：agent.py 和 tools.py 中均通过 os.getenv("GITHUB_TOKEN") 和 os.getenv("DEEPSEEK_API_KEY") 动态读取环境变量，源码中不存在任何 ghp_ 开头的明文 Token。
4. 全仓安全自查：在项目根目录执行 Select-String -Path .\* -Pattern "ghp_"，无任何输出，证明全仓无泄漏。
git clone https://github.com/3110lmy/agent-repository-3.git
cd agent-repository-3
pip install -r requirements.txt
GITHUB_TOKEN=你的GitHub_Token
DEEPSEEK_API_KEY=你的DeepSeek_API_Key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
MODEL=deepseek-chat
========================================================
🤖  GitHub Agent 课程项目 v0.1
========================================================
  模型          : deepseek-chat
  LLM API Key   : ✅ 已配置
  GitHub Token  : ✅ 已配置
  可用工具      : get_github_user, list_user_repos, search_repos
========================================================

👋 你好！我是 GitHub Agent。输入问题开始，输入 exit 退出。
你 >
👤 帮我搜索一下 GitHub 上最火的 Python 爬虫仓库
  [step 1] 🔧 search_repos({'query': 'python crawler', 'limit': 5})

🤖 以下是 GitHub 上最火的 Python 爬虫仓库...
（此处为真实 API 返回数据，已验证成功）
---

## 🤖 Agent 与普通聊天机器人的区别（自述说明）

我认为 Agent 与普通聊天机器人最大的区别有两点：
1. **是否调用外部工具获取真实数据**：普通聊天机器人只能凭大模型参数生成文本，容易产生幻觉；而 Agent 会调用真实的外部工具（如 GitHub API），用真实数据来回答问题。
2. **是否具备多步自主决策循环**：普通聊天机器人是一问一答，单轮结束；而 Agent 具备 Think → Act → Observe 循环，能根据上一步的结果，自主决定下一步该调用哪个工具。

### 📊 真实多步运行示例

在执行复杂任务（如“搜索 Star 最高的 Python 爬虫仓库，然后看看作者资料”）时，终端输出了真正的多步回显：
[step 1] 🔧 search_repos({'query': 'python crawler', 'limit': 5})
[step 2] 🔧 get_github_user({'username': 'D4Vinci'})

模型先调用了 search_repos 搜索仓库，拿到结果后，自己判断出需要再调用 get_github_user 去查作者资料。这证明 Agent 不是单轮问答，而是真正在自主规划、多步执行。



