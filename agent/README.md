# CampusDoc Agent

可运行的 **AI Agent** 示例，对齐岗位：文档处理 Agent、数据清洗、RAG、工具调用、Python 独立部署。

## 能力

| 工具 | 作用 |
|------|------|
| `search_knowledge` | 本地知识库关键词 RAG |
| `clean_tabular_text` | CSV/表格脏数据清洗 |
| `summarize_document` | 文档摘要 |
| `grade_concept_answer` | 结合课本片段的概念题批改 |

配置 `DEEPSEEK_API_KEY` 后走 **真实 Tool-Calling**；未配置时自动 **Demo 模式**（仍调用真实本地工具）。

## 快速启动

```bash
cd agent
pip install -r requirements.txt

# 可选：启用 Live Agent
# Windows PowerShell:
#   $env:DEEPSEEK_API_KEY="sk-xxx"
# Linux/macOS:
#   export DEEPSEEK_API_KEY=sk-xxx

python app.py
```

浏览器打开：http://127.0.0.1:7860

## 目录

```text
agent/
├── app.py                 # FastAPI 入口
├── core/
│   ├── agent.py           # Agent 循环
│   ├── llm.py             # DeepSeek Tool Calling
│   └── tools.py           # 工具实现
├── knowledge/             # RAG 语料
└── static/                # 演示网页
```

## 与 Dify 的关系

本 Agent 演示 **自研 Tool-Calling + 本地 RAG**。生产环境可把 `search_knowledge` 换成 Dify 知识库 API，业务后端仍负责鉴权与落库。

## 岗位匹配

- AI Agent 落地：可观察工具调用轨迹（trace）
- Python：独立服务
- 文档处理 / 数据清洗：内置工具
- 平台维护：FastAPI + 静态页，易嵌入内部门户
