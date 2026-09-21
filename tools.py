"""工具层：Agent 能调用的所有函数都在这里注册。"""
import os
import requests

GITHUB_API = "https://api.github.com"


def explain_github_error(status: int, headers: dict) -> str:
    """把 GitHub 的报错翻译成人话。"""
    remaining = headers.get("X-RateLimit-Remaining")
    if status == 401:
        return "401 Unauthorized —— Token 不对或已过期"
    if status == 403:
        if remaining == "0":
            return "403 限流 —— 请求次数用完，确认带 Token 或稍后重试"
        return "403 权限不够 —— 生成 Token 时需勾选 public_repo"
    if status == 404:
        return "404 Not Found —— 资源不存在或不是公开的"
    return f"{status} —— 未知错误"


def _headers() -> dict:
    h = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _github_get(path: str, params: dict | None = None):
    r = requests.get(
        f"{GITHUB_API}{path}",
        headers=_headers(),
        params=params,
        timeout=15,
    )
    if r.status_code >= 400:
        raise RuntimeError(explain_github_error(r.status_code, r.headers))
    return r.json()


# ---------- 工具 1：查用户资料 ----------
def get_github_user(username: str) -> dict:
    """查询 GitHub 用户的公开资料。"""
    d = _github_get(f"/users/{username}")
    return {
        "login": d.get("login"),
        "name": d.get("name"),
        "bio": d.get("bio"),
        "public_repos": d.get("public_repos"),
        "followers": d.get("followers"),
        "html_url": d.get("html_url"),
    }


# ---------- 工具 2：查仓库列表 ----------
def list_user_repos(username: str, limit: int = 5) -> list:
    """列出某用户最近更新的仓库。"""
    data = _github_get(
        f"/users/{username}/repos",
        params={"sort": "updated", "per_page": int(limit)},
    )
    return [
        {
            "name": r["name"],
            "stars": r["stargazers_count"],
            "language": r["language"],
            "description": r.get("description"),
        }
        for r in data
    ]


# ---------- 工具 3：搜索仓库 ----------
def search_repos(query: str, limit: int = 5) -> list:
    """根据关键词搜索 GitHub 仓库，按 Star 数排序。"""
    data = _github_get(
        "/search/repositories",
        params={"q": query, "sort": "stars", "order": "desc", "per_page": int(limit)},
    )
    return [
        {
            "name": r["name"],
            "owner": r["owner"]["login"],
            "stars": r["stargazers_count"],
            "language": r["language"],
            "description": r.get("description"),
            "html_url": r["html_url"],
        }
        for r in data.get("items", [])
    ]


# ---------- 工具注册表 ----------
TOOL_FUNCTIONS = {
    "get_github_user": get_github_user,
    "list_user_repos": list_user_repos,
    "search_repos": search_repos,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_github_user",
            "description": "查询 GitHub 用户的公开资料（昵称、仓库数、粉丝数等）",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "GitHub 用户名"}
                },
                "required": ["username"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_user_repos",
            "description": "列出某个 GitHub 用户最近更新的仓库",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "GitHub 用户名"},
                    "limit": {"type": "integer", "description": "返回条数，默认 5"},
                },
                "required": ["username"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_repos",
            "description": "根据关键词搜索 GitHub 仓库，返回按 Star 数排序的热门仓库",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词，例如 'machine learning'",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回条数，默认 5",
                    },
                },
                "required": ["query"],
            },
        },
    },
]


def call_tool(name: str, args: dict):
    """统一入口：按名字分发。出错也当成结果返回，让 Agent 自己决定怎么办。"""
    if name not in TOOL_FUNCTIONS:
        return {"error": f"未知工具: {name}"}
    try:
        return TOOL_FUNCTIONS[name](**args)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}