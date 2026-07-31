"""DeepSeek / OpenAI-compatible chat with tool calling."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def chat_with_tools(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    model: str | None = None,
) -> dict[str, Any]:
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        return {"demo": True, "choices": [{"message": {"content": ""}}]}

    model = model or os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    base = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    body = {
        "model": model,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "temperature": 0.2,
    }
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        return {
            "demo": False,
            "error": True,
            "choices": [
                {
                    "message": {
                        "content": f"LLM 调用失败 HTTP {e.code}: {detail[:500]}",
                        "tool_calls": [],
                    }
                }
            ],
        }
    except Exception as e:  # noqa: BLE001
        return {
            "demo": False,
            "error": True,
            "choices": [
                {
                    "message": {
                        "content": f"LLM 调用异常: {e}",
                        "tool_calls": [],
                    }
                }
            ],
        }
