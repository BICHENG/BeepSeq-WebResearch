## BeepSeq-WebResearch 改进与未完事项（Backlog & Proposals）

本文档汇总当前系统的未完成工作（Backlog）、改进提议（Proposals）、已知失败用例（Failcases）、测试建议与验收标准，确保可用性、兼容性与性能的持续提升，同时最大化 MCP 工具在 Cursor 生态中的“可发现性（SEO）”。

---

### 一、当前状态（Snapshot）
- MCP 集成：已基于 fastapi-mcp 自动暴露 `read_url`、`read_urls`、`search_web`。
- 可用性：
  - GET `/read` 支持 `url` 或 `urls=逗号分隔`；
  - POST `/read` 支持 JSON（`{ urls: [...], config?: {...} }`）。
- 可靠性：
  - 批量抓取并发稳定；单个失败不会影响整体（例如 `wtfpl.net` 提取为空）。
- 兼容性：
  - CORS 已放开；Pydantic 模型（`CrawlerConfig`/`ReadRequest`）便于各类客户端直接调用。
- 精确性：
  - 对维基与 choosealicense 抽取准确；富媒体图片嵌入依赖源站，可进一步压测。

---

### 二、已知失败场景与风险（Failcases & Risks）
- 部分源站结构/反爬导致抽取为空（例：`wtfpl.net` 返回空字符串）。
- 高并发与全文抓取组合下，可能放大外部网络波动与资源压力。
- 没有统一的每 URL 级别元数据（耗时、大小、嵌入图片数、用哪个提取器等）不利于诊断。

---

### 三、未完成工作（Backlog，按优先级）
- P0（本周）
  - 为每个 URL 返回结果增加元数据字段：`status`、`error`、`elapsed_ms`、`content_length`、`images_embedded`、`extractor_used`。
  - 在单条抽取失败时自动进行一次提取器回退（`readability-lxml → trafilatura`）。
  - 新增健康检查端点 `GET /healthz`（返回 cache 大小、并发阈值、uptime 等）。
- P1（本月）
  - 将 `max_concurrency`、`timeout_ms` 暴露到 `CrawlerConfig`，允许请求级覆盖；
  - 在 `search_web?fulltext=true` 路径中，对每个 URL 增加独立超时与失败隔离（不中断）并返回 `error`。
  - 提供更详细的日志等级开关与结构化日志（不影响成功路径性能）。
- P2（酌情）
  - 增加结果中“字数/段落数”等内容统计，辅助后续数据治理与配额评估。
  - 针对富媒体长文的图片限速与重试策略（保护源站与自身资源）。

---

### 四、改进提议（Proposals，含实现要点）
- Proposal A：结果元数据 Schema 扩展（P0）
  - 在 `crawl` 聚合结果中，对每个 URL 返回：
    - `status: "success" | "failed"`
    - `error?: string`（仅失败时）
    - `elapsed_ms: number`、`content_length: number`
    - `images_embedded: number`、`extractor_used: "readability"|"trafilatura"`
  - 验收：批量任务中，任意一条失败不影响整体，且失败条目包含 `error`。

- Proposal B：自动提取器回退（P0）
  - `readability` 失败或抽取空内容时，自动尝试 `trafilatura` 一次。
  - 验收：对于 `wtfpl.net` 等空抽取页面，回退路径能稳定给出最佳可得结果（允许仍为空，但不可抛异常）。

- Proposal C：健康检查与可观测性（P0）
  - 新增 `GET /healthz`：`{"status":"ok","cache_size":N,"max_concurrency":M,"uptime_sec":T}`。
  - 验收：服务启动后能快速诊断存活，压测期间响应稳定。

- Proposal D：并发与超时可配置（P1）
  - `CrawlerConfig` 增加 `max_concurrency`、`request_timeout_ms`（下载/页面加载/图片下载），默认保守；
  - 验收：在高并发批量时，服务能通过配置平衡吞吐/稳定性；不会出现系统性阻塞。

- Proposal E：MCP 工具 SEO（持续）
  - 已优化：`summary`、`tags`、README MCP 示例（含 GET/POST 批量与高级配置）。
  - 建议增强关键词（不改变功能）：
    - `read_url`："RAG-ready Markdown, image embedding, real-browser anti-bot"
    - `read_urls`："Batch, parallel, resilient, RAG-ready Markdown"
    - `search_web`："DuckDuckGo search → optional auto-read to Markdown"
  - 验收：在 Cursor 工具面板中，描述清晰抓住价值点，触发试用意愿。

---

### 五、压力与胡闹测试（建议脚本/步骤）
- 非法/异常输入：
  - `read_url url="notaurl"`
  - `read_url urls="https://example.com,notaurl,https://foo.invalid"`
- 大批量并发：
  - `read_urls` 一次性 50–100 个 URL，混合好坏链接；并行发起 3–5 组请求。
- 搜索+全文链路：
  - `search_web query="wtflicense" max_results=5 fulltext=true`
- 富媒体/反爬页面：
  - `read_url url="https://www.bilibili.com/..."`、大型长文站点
- 极端配置：
  - `embed_images=true` + `save_markdown=true` + `no_cache=true`（观察 IO/CPU/网络）

期望：所有失败有 `error` 字段、不崩溃；成功路径的 Markdown 质量稳定。

---

### 六、验收标准（Acceptance Criteria）
- 功能：GET/POST/批量/全文检索均可稳定执行；失败隔离，返回结构含元数据与错误字段。
- 性能：在并发压力下响应时间可控（根据配置）；不出现整体阻塞或崩溃。
- 精确性：主流资讯文档抽取 Markdown 结构清晰；图片嵌入在允许的场景稳定成功。
- 兼容性：MCP 自动发现正常；工具摘要与 README 示例直观可用。

---

### 七、落地计划（Rollout）
- 小步发布：优先合入 P0 事项 → 压测 → 合入 P1 → 再压测。
- 文档：更新 README 的“健康检查/诊断”与“故障排查”章节；为返回元数据新增说明。
- 监控：在生产使用前引入轻量级日志与指标导出（可选）。

---

### 八、附：常用调用示例（MCP）
- 搜索：`@webresearch search_web query="Latest AI" max_results=3`
- 单页：`@webresearch read_url url="https://example.com"`
- 批量（GET）：`@webresearch read_url urls="https://a,https://b"`
- 批量（POST+配置）：`@webresearch read_urls urls=["https://a","https://b"] config={"embed_images":true,"save_markdown":true}`


