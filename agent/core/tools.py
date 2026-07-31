"""Agent tools: RAG search, data cleaning, summarize, concept grading."""

from __future__ import annotations

import csv
import io
import re
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"


def _load_chunks() -> list[dict[str, str]]:
    chunks: list[dict[str, str]] = []
    if not KNOWLEDGE_DIR.exists():
        return chunks
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        parts = re.split(r"\n(?=##\s)", text)
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            title = part.split("\n", 1)[0].lstrip("# ").strip()
            chunks.append(
                {
                    "id": f"{path.stem}-{i}",
                    "source": path.name,
                    "title": title,
                    "content": part,
                }
            )
    return chunks


def search_knowledge(query: str, top_k: int = 3) -> str:
    """关键词轻量 RAG：从 knowledge/*.md 检索相关片段。"""
    query = (query or "").strip()
    if not query:
        return "查询为空"
    # 中文：整词 + 2~4 字滑动片段，提升「什么是封装」类问法命中率
    rough = [t for t in re.split(r"[\s,，。？?、！!；;：:]+", query) if t]
    tokens: list[str] = []
    for t in rough:
        tokens.append(t)
        if re.search(r"[\u4e00-\u9fff]", t):
            for n in (2, 3, 4):
                for i in range(0, max(0, len(t) - n + 1)):
                    tokens.append(t[i : i + n])
    # 去重保序
    seen: set[str] = set()
    uniq_tokens: list[str] = []
    for t in tokens:
        if t not in seen and len(t) >= 1:
            seen.add(t)
            uniq_tokens.append(t)
    tokens = uniq_tokens

    chunks = _load_chunks()
    scored: list[tuple[int, dict[str, str]]] = []
    for ch in chunks:
        hay = (ch["title"] + "\n" + ch["content"]).lower()
        score = sum(1 for t in tokens if t.lower() in hay)
        # bonus for exact phrase
        if query.lower() in hay:
            score += 3
        if score > 0:
            scored.append((score, ch))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[: max(1, min(top_k, 5))]
    if not top:
        return "未检索到相关知识库内容。可补充 agent/knowledge/ 下的 md 文档。"
    lines = []
    for score, ch in top:
        excerpt = ch["content"][:800]
        lines.append(f"[{ch['source']} | {ch['title']} | score={score}]\n{excerpt}")
    return "\n\n---\n\n".join(lines)


def clean_tabular_text(raw_text: str) -> str:
    """清洗杂乱 CSV/表格文本：去空行、统一分隔符、剔除空姓名行、标记异常分数。"""
    raw = (raw_text or "").strip()
    if not raw:
        return "输入为空"
    # normalize separators
    text = raw.replace("\t", ",").replace("，", ",")
    reader = csv.reader(io.StringIO(text))
    rows = [ [c.strip() for c in row] for row in reader if any(c.strip() for c in row) ]
    if not rows:
        return "没有可解析的行"

    header = rows[0]
    body = rows[1:] if len(rows) > 1 else []
    cleaned = [header]
    removed = 0
    flagged = 0
    for row in body:
        # pad
        while len(row) < len(header):
            row.append("")
        row = row[: len(header)]
        name = row[0] if row else ""
        if not name:
            removed += 1
            continue
        # score column heuristic: second column
        if len(row) > 1 and row[1]:
            if not re.fullmatch(r"\d+(\.\d+)?", row[1]):
                row[1] = f"INVALID({row[1]})"
                flagged += 1
        cleaned.append(row)

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerows(cleaned)
    summary = (
        f"清洗完成：保留 {len(cleaned)-1} 行，删除空姓名 {removed} 行，"
        f"异常分数字段 {flagged} 个。\n\n"
    )
    return summary + out.getvalue()


def summarize_document(text: str, max_chars: int = 120) -> str:
    """无 LLM 时的抽取式摘要；有 LLM 时 Agent 仍可直接让模型总结。"""
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return "文本为空"
    if len(text) <= max_chars:
        return text
    # take head + key sentences containing 系统/实现/功能
    sentences = re.split(r"(?<=[。！？.!?])\s*", text)
    key = [s for s in sentences if any(k in s for k in ("系统", "实现", "功能", "Agent", "RAG"))]
    picked = []
    for s in key + sentences:
        if s and s not in picked:
            picked.append(s)
        draft = "".join(picked)
        if len(draft) >= max_chars:
            return draft[:max_chars] + "…"
    return text[:max_chars] + "…"


def grade_concept_answer(
    stem: str,
    textbook: str,
    reference: str,
    student: str,
    max_points: int = 10,
) -> str:
    """结合课本片段的轻量批改：关键词覆盖度 + 说明。"""
    student = (student or "").strip()
    if not student:
        return '{"earnedPoints":0,"comment":"未作答"}'

    # extract simple keywords from reference + textbook headings
    base = f"{reference} {textbook}"
    words = re.findall(r"[\u4e00-\u9fff]{2,6}|[A-Za-z]{3,}", base)
    uniq = []
    for w in words:
        if w not in uniq and w not in ("什么", "如何", "以及", "进行", "可以"):
            uniq.append(w)
        if len(uniq) >= 8:
            break
    hit = [w for w in uniq if w.lower() in student.lower()]
    ratio = len(hit) / max(1, min(len(uniq), 5))
    points = int(round(max_points * min(1.0, ratio)))
    comment = (
        f"命中要点 {len(hit)}/{min(len(uniq),5)}："
        + ("、".join(hit) if hit else "未覆盖核心术语")
        + "。建议结合课本表述补充。"
    )
    return (
        f'{{"earnedPoints":{points},"maxPoints":{max_points},'
        f'"matched":{hit},"comment":"{comment}"}}'
    )


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "从本地知识库检索与问题相关的课本/文档片段（RAG）",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "检索关键词或问题"},
                    "top_k": {"type": "integer", "description": "返回条数，默认3"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "clean_tabular_text",
            "description": "清洗杂乱的 CSV/表格文本，去除空行与异常值",
            "parameters": {
                "type": "object",
                "properties": {
                    "raw_text": {"type": "string", "description": "原始表格文本"},
                },
                "required": ["raw_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_document",
            "description": "对长文本做简短摘要",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "max_chars": {"type": "integer"},
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grade_concept_answer",
            "description": "结合课本原文批改概念题，返回 JSON 分数与评语",
            "parameters": {
                "type": "object",
                "properties": {
                    "stem": {"type": "string"},
                    "textbook": {"type": "string"},
                    "reference": {"type": "string"},
                    "student": {"type": "string"},
                    "max_points": {"type": "integer"},
                },
                "required": ["stem", "textbook", "reference", "student"],
            },
        },
    },
]

TOOL_HANDLERS = {
    "search_knowledge": search_knowledge,
    "clean_tabular_text": clean_tabular_text,
    "summarize_document": summarize_document,
    "grade_concept_answer": grade_concept_answer,
}
