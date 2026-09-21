#!/usr/bin/env python3
"""GitHub Agent —— 课程项目骨架 v0.1"""
import os
import sys
import json
import argparse

from dotenv import load_dotenv

import tools

load_dotenv()

MAX_STEPS = 8

SYSTEM_PROMPT = """你是一个 GitHub 助手 Agent。
规则：
1. 需要真实数据时必须调用工具，不要凭记忆编造。
2. 一次只调用必要的工具，拿到结果后再决定下一步。
3. 信息足够时直接给出最终中文回答，不要再调用工具。
"""


def print_greeting(model: str) -> None:
    has_llm = bool(os.getenv("DEEPSEEK_API_KEY"))
    has_gh = bool(os.getenv("GITHUB_TOKEN"))
    print("=" * 56)
    print("🤖  GitHub Agent 课程项目 v0.1")
    print("=" * 56)
    print(f"  模型          : {model}")
    print(f"  LLM API Key   : {'✅ 已配置' if has_llm else '⚠️  未配置'}")
    print(f"  GitHub Token  : {'✅ 已配置' if has_gh else '⚠️  未配置'}")
    print(f"  可用工具      : {', '.join(tools.TOOL_FUNCTIONS)}")
    print("=" * 56)


def build_client():
    if not os.getenv("DEEPSEEK_API_KEY"):
        return None
    from openai import OpenAI

    return OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL") or "https://api.deepseek.com/v1",
    )


def run_agent(client, model: str, user_input: str, max_steps: int = MAX_STEPS) -> str:
    """Agent 核心：Think → Act → Observe 循环。"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    for step in range(1, max_steps + 1):
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools.TOOL_SCHEMAS,
            tool_choice="auto",
        )
        msg = resp.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            return msg.content or "(空回复)"

        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            print(f"  [step {step}] 🔧 {tc.function.name}({args})")
            result = tools.call_tool(tc.function.name, args)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    return f"⚠️  达到最大步数 {max_steps}，任务未完成。"


def main() -> None:
    model = os.getenv("MODEL", "deepseek-chat")

    parser = argparse.ArgumentParser(description="GitHub Agent CLI")
    parser.add_argument("-q", "--query", help="直接提问，不进入交互模式")
    parser.add_argument("--max-steps", type=int, default=MAX_STEPS)
    args = parser.parse_args()

    print_greeting(model)

    client = build_client()
    if client is None:
        print("\n👋 你好！我是 GitHub Agent。")
        print("   当前未配置 DEEPSEEK_API_KEY，只完成环境自检。")
        print("   请在 .env 中填入 Key 后重新运行，例如：")
        print('   python agent.py -q "看看 torvalds 的 GitHub 资料"')
        return

    def ask(text: str) -> None:
        print(f"\n👤 {text}")
        answer = run_agent(client, model, text, args.max_steps)
        print(f"\n🤖 {answer}\n")

    if args.query:
        ask(args.query)
        return

    print("\n👋 你好！我是 GitHub Agent。输入问题开始，输入 exit 退出。\n")
    while True:
        try:
            text = input("你 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见 👋")
            break
        if not text:
            continue
        if text.lower() in {"exit", "quit", "q"}:
            print("再见 👋")
            break
        ask(text)


if __name__ == "__main__":
    main()