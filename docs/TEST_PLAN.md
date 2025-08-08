## BeepSeq-WebResearch 测试计划（功能/压力/鲁棒性）

目标：验证服务端稳定性、可靠性、精确性与 MCP 兼容性；形成可复用的测试基线，便于下一工作组产品化优化。

---

### 1. 环境准备
- 启动服务：`webresearch serve --port 8000`
- MCP 集成：`~/.cursor/mcp.json` 中添加
  ```json
  {"mcpServers":{"webresearch":{"url":"http://localhost:8000/mcp"}}}
  ```
- 关键端点：
  - GET `/read`（支持 `url` 或 `urls=逗号分隔`）
  - POST `/read`（JSON: `{ urls: [...], config?: {...} }`）
  - GET `/search`（`fulltext` 可选）

---

### 2. 功能测试（功能/兼容性）
1) 单页读取
  - MCP: `@webresearch read_url url="https://example.com"`
  - 期望：返回 Markdown，标题与正文结构清晰

2) 批量读取（GET 逗号分隔）
  - MCP: `@webresearch read_url urls="https://example.com,https://en.wikipedia.org/wiki/WTFPL"`
  - 期望：返回字典/映射；每个 URL 对应 Markdown

3) 批量读取（POST + 高级配置）
  - MCP: `@webresearch read_urls urls=["https://a","https://b"] config={"embed_images":true,"save_markdown":true}`
  - 期望：并行抓取成功；图片嵌入生效（视源站而定）

4) 搜索（仅结果）
  - MCP: `@webresearch search_web query="NVIDIA Blackwell" max_results=3`
  - 期望：返回结构化 `{url, snippet}` 数组

5) 搜索 + 全文抓取
  - MCP: `@webresearch search_web query="wtflicense" max_results=3 fulltext=true`
  - 期望：先搜后读，返回 URL→Markdown 映射；个别失败不影响整体

---

### 3. 胡闹/边界测试（鲁棒性）
1) 非法 URL
  - `@webresearch read_url url="notaurl"`
  - 期望：不崩溃；当前版本可能返回空字符串（改进项：返回 `error` 字段）

2) 混合批量（含失联主机/非法端口）
  - `@webresearch read_urls urls=["https://example.com","http://localhost:65535/","https://en.wikipedia.org/wiki/Artificial_intelligence"]`
  - 期望：`example.com`、`wikipedia` 成功；`localhost:65535` 返回错误页或空；整体不崩溃

3) 大批量并发
  - 一次 50–100 URL（良莠不齐），并行发起 3–5 组
  - 期望：吞吐稳定，拒绝服务风险可控；失败隔离

4) 复杂/反爬页面
  - 如 B 站/重 JS 站点（需浏览器渲染），观察：
    - 抽取质量、速度、是否触发风控

5) 极端配置
  - `embed_images=true` + `save_markdown=true` + `no_cache=true`
  - 期望：IO/网络峰值仍可控；任务完成无崩溃

---

### 4. 已知行为与当前结果（样例）
- `read_url https://example.com`：成功，Markdown 正文正确
- `search_web NVIDIA Blackwell`：成功，返回 3 条链接 + 摘要
- `read_urls [example, wikipedia, choosealicense]`：成功；个别源（如特定站）可能空抽取
- `read_url notaurl`：当前返回空（建议：改为 `{error: "Invalid URL"}`）
- `read_urls` 含 `http://localhost:65535/`：不崩溃，返回错误页内容或空

---

### 5. 验收标准（交付基线）
- 稳定性：高并发/混合失败不导致进程崩溃
- 可靠性：单条失败隔离；批量任务完成率稳定
- 精确性：主流资讯/文档站点 Markdown 结构清晰；图片嵌入在允许情况下生效
- 兼容性：MCP 工具在 Cursor 面板可见且可用，示例可直接运行

---

### 6. 后续优化与跟踪
- 详见 `docs/IMPROVEMENTS.md`（含 Backlog 与验收）


