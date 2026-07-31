# RAG 与 Agent 基础

## 什么是 RAG
RAG（Retrieval-Augmented Generation，检索增强生成）是指先从知识库检索相关文档片段，再把片段作为上下文交给大模型生成答案或评分。其目的是减少幻觉，让回答有据可依。

## Agent 工具调用
AI Agent 不只是单次问答，而是能规划步骤并调用工具：例如检索知识库、清洗表格、调用业务 API。典型循环是：理解目标 → 选择工具 → 观察结果 → 继续或给出最终答复。

## Dify 知识库对接思路
可将文档上传到 Dify 知识库完成切片与向量检索，Java/Python 后端通过 Workflow 或 Chat API 调用。业务系统负责鉴权、落库与权限，Dify 负责检索与生成。
