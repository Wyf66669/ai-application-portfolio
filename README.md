# AI Application Portfolio · 温耀方

面向 **AI 应用工程 / 平台维护** 岗位的技术展示仓库。

## 在线展示页

**https://wyf66669.github.io/ai-application-portfolio/**

本地预览：打开根目录 `index.html`。

## 仓库结构

```text
ai-application-portfolio/
├── index.html                 # 作品集展示页
├── styles.css
├── README.md
├── agent/                     # ★ 可运行 CampusDoc Agent
├── projects/
│   └── academic-affairs/      # 教务系统 · AI 批改与 RAG
├── algorithms/                # Hot 100 精选 Java 题解
└── scripts/
```

## 岗位匹配摘要

| 岗位要求 | 本仓库对应能力 |
|---------|----------------|
| AI Agent / LLM 应用 | **CampusDoc Agent**（Tool-Calling）+ 教务 AI 批改 |
| Python / 二次开发 | FastAPI Agent 服务，可替换 Dify 知识库 |
| Vue / 前端 | Vue 3 教务前端实践；Agent 演示页 |
| 平台维护 / 工具链 | Spring Boot 分层、JWT、Redis、部署联调 |
| 文档处理 / 数据清洗 | Agent 内置清洗与 RAG 工具 |

## 重点 1：CampusDoc Agent（请优先演示）

```bash
cd agent
pip install -r requirements.txt
python app.py
# http://127.0.0.1:7860
```

可选启用 Live 模式：

```powershell
$env:DEEPSEEK_API_KEY="sk-xxx"
python app.py
```

详见 [`agent/README.md`](agent/README.md)

## 重点 2：教务管理系统（毕设，已答辩通过）

- 技术栈：Spring Boot + MyBatis + MySQL + Vue 3 + DeepSeek
- 亮点：AI 组卷发布、AI 自动批改、概念题 RAG 检索、异常降级

详见 [`projects/academic-affairs/README.md`](projects/academic-affairs/README.md)

## 算法题解

滑动窗口、双指针、前缀和、HashMap 等高频题，见 `algorithms/`。

## License

MIT
