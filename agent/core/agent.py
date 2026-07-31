"""
CampusDoc Agent — 文档处理 / 知识问答 / 数据清洗 Agent
岗位对齐：AI Agent 落地、Python、工具调用、RAG、可独立部署
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .llm import chat_with_tools
from .tools import TOOL_DEFINITIONS, TOOL_HANDLERS


@dataclass
class AgentTrace:
    """记录 Agent 思考与工具调用，便于演示与调试。"""

    steps: list[dict[str, Any]] = field(default_factory=list)

    def add(self, kind: str, payload: Any) -> None:
        self.steps.append({"kind": kind, "payload": payload})


SYSTEM_PROMPT = """你是 CampusDoc Agent，一个面向教务/文档场景的 AI 助手。
你可以调用工具完成任务，不要编造工具结果。

可用能力：
1. search_knowledge：从本地知识库检索课本/规章片段（RAG）
2. clean_tabular_text：清洗杂乱表格/CSV 文本
3. summarize_document：总结长文本
4. grade_concept_answer：结合检索到的课本内容批改概念题

规则：
- 需要事实依据时先 search_knowledge
- 用户要清洗数据时调用 clean_tabular_text
- 批改概念题时：先检索，再 grade_concept_answer
- 最后用中文给出简洁、可执行的回答
- 若工具失败，如实说明并给替代建议
"""


class CampusDocAgent:
    def __init__(self, max_rounds: int = 6) -> None:
        self.max_rounds = max_rounds
        self.handlers: dict[str, Callable[..., str]] = TOOL_HANDLERS

    def run(self, user_message: str) -> dict[str, Any]:
        trace = AgentTrace()
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
        trace.add("user", user_message)

        for _ in range(self.max_rounds):
            response = chat_with_tools(messages, TOOL_DEFINITIONS)
            trace.add("llm_raw", response)

            # Demo / offline fallback
            if response.get("demo"):
                answer = self._demo_answer(user_message)
                trace.add("final", answer)
                return {"answer": answer, "trace": trace.steps, "mode": "demo"}

            msg = response["choices"][0]["message"]
            tool_calls = msg.get("tool_calls") or []

            if not tool_calls:
                answer = msg.get("content") or ""
                trace.add("final", answer)
                return {"answer": answer, "trace": trace.steps, "mode": "live"}

            messages.append(
                {
                    "role": "assistant",
                    "content": msg.get("content"),
                    "tool_calls": tool_calls,
                }
            )

            for call in tool_calls:
                name = call["function"]["name"]
                raw_args = call["function"].get("arguments") or "{}"
                try:
                    args = json.loads(raw_args)
                except json.JSONDecodeError:
                    args = {}

                handler = self.handlers.get(name)
                if handler is None:
                    result = f"未知工具: {name}"
                else:
                    try:
                        result = handler(**args)
                    except TypeError as e:
                        result = f"工具参数错误: {e}"
                    except Exception as e:  # noqa: BLE001
                        result = f"工具执行失败: {e}"

                trace.add("tool", {"name": name, "args": args, "result": result[:2000]})
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call["id"],
                        "content": result,
                    }
                )

        answer = "已达到最大工具调用轮次，请缩小问题范围后重试。"
        trace.add("final", answer)
        return {"answer": answer, "trace": trace.steps, "mode": "live"}

    def _demo_answer(self, user_message: str) -> str:
        """无 API Key 时的本地演示逻辑，仍走真实工具。"""
        text = user_message.strip()
        lower = text.lower()

        if any(k in text for k in ("清洗", "csv", "表格", "脏数据")):
            sample = (
                "姓名, 成绩 ,备注\n"
                "张三,,优秀\n"
                "李四, 88 ,\n"
                " ,90,及格\n"
                "王五,abc,异常"
            )
            cleaned = self.handlers["clean_tabular_text"](raw_text=sample)
            return (
                "【Demo 模式】未配置 DEEPSEEK_API_KEY，使用本地工具演示数据清洗：\n\n"
                f"{cleaned}"
            )

        if any(k in text for k in ("批改", "评分", "概念题")):
            stem = "什么是封装？"
            hits = self.handlers["search_knowledge"](query="封装", top_k=2)
            grade = self.handlers["grade_concept_answer"](
                stem=stem,
                textbook=hits,
                reference="封装是将数据与操作数据的方法绑定在一起，隐藏内部细节。",
                student="把数据和操作放在一起，对外隐藏细节。",
            )
            return (
                "【Demo 模式】本地 RAG + 规则批改演示：\n\n"
                f"检索结果：\n{hits}\n\n批改结果：\n{grade}"
            )

        if any(k in text for k in ("总结", "摘要", "summar")):
            doc = (
                "本系统实现了选课、排课、成绩与 AI 作业批改。"
                "概念题批改前会检索课本片段，再调用大模型评分。"
            )
            summary = self.handlers["summarize_document"](text=doc, max_chars=80)
            return f"【Demo 模式】文档总结演示：\n\n{summary}"

        hits = self.handlers["search_knowledge"](query=text or "面向对象", top_k=3)
        return (
            "【Demo 模式】未配置 API Key，已调用本地知识库检索：\n\n"
            f"{hits}\n\n"
            "配置环境变量 DEEPSEEK_API_KEY 后可启用完整 Tool-Calling Agent。"
        )
