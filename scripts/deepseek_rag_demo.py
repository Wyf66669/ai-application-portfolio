# 简易 DeepSeek 调用示例（Python）
# 用于展示：可用 Python 做 LLM 工具链脚本 / Agent 编排扩展
# 运行前设置环境变量 DEEPSEEK_API_KEY

import json
import os
import urllib.request


def chat(prompt: str, model: str = "deepseek-chat") -> str:
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        return "[demo] 未配置 DEEPSEEK_API_KEY，此处仅展示调用结构"

    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def rag_grade(stem: str, textbook: str, answer: str, student: str) -> str:
    """概念题：课本片段增强后再批改（与教务系统 RAG 思路一致）"""
    prompt = f"""你是课程批改助手。依据课本原文评分，严格 JSON：
{{"earnedPoints":0-10,"comment":"60字以内"}}

题目：{stem}
课本摘录：{textbook}
参考答案：{answer}
学生作答：{student}
满分：10
"""
    return chat(prompt)


if __name__ == "__main__":
    print(chat("用一句话解释什么是 RAG。"))
