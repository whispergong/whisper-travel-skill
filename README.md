# whisper-travel-skill

面向中文旅行场景的 Codex/Agent 技能仓库。核心技能包括：

- `travel-planning-cn`：完整旅行规划总控，覆盖攻略搜集、图片读取、路线验证、每日行程、住宿安排、费用估算和腾讯智能文档交付。
- `hotel-search-cn`：国内酒店聚合搜索、比价和推荐，覆盖高德定位、FlyAI/飞猪、AIGoHotel、同程程心、携程问道、同程网页端、携程网页端等来源。

## 快速安装

推荐使用 skills CLI 安装指定技能：

```bash
npx skills add https://github.com/whispergong/whisper-travel-skill.git --skill travel-planning-cn
npx skills add https://github.com/whispergong/whisper-travel-skill.git --skill hotel-search-cn
```

手动安装时，可直接同步技能目录：

```bash
git clone https://github.com/whispergong/whisper-travel-skill.git
mkdir -p "${HOME}/.codex/skills"
rsync -a --delete whisper-travel-skill/travel-planning-cn/ "${HOME}/.codex/skills/travel-planning-cn/"
rsync -a --delete whisper-travel-skill/hotel-search-cn/ "${HOME}/.codex/skills/hotel-search-cn/"
```

## 小红书依赖

`travel-planning-cn` 会把小红书作为高权重攻略来源。小红书采集应走本地项目的浏览器自动化路径：`scripts/cli.py` 通过 Chrome/扩展/Bridge 操作真实浏览器页面，登录、扫码验证和风控处理都在可见浏览器里完成。

```bash
cd /Users/whisper/Desktop/workplace/xiaohongshu-skills
./.venv/bin/python scripts/cli.py check-login
```

如未登录，请按该项目的 `xiaohongshu-skills` / `xhs-auth` 指引启动 Chrome 并登录。连续详情采集要控制频率，避免触发风控；同一时间只让一个 agent 操作小红书详情页或同一个可见浏览器。

## 腾讯智能文档依赖

`travel-planning-cn` 完成攻略后，会默认创建一篇腾讯智能文档（smartcanvas），用于沉淀每日计划、路线图、景点链接、酒店和费用表。创建前需确保腾讯文档 MCP 已授权：

```bash
mcporter list tencent-docs
```

如果提示 token 失效或未授权，请按 `/Users/whisper/Desktop/workplace/tencent-docs/SKILL.md` 中的授权说明完成登录授权后重试。文档内图片必须先通过腾讯文档 `upload_image` 上传，不能直接使用外链图片。

## FlyAI MCP 支撑工具

`tools/flyai-cli-mcp` 是本仓库附带的 FlyAI CLI MCP 包装器，用于让 `hotel-search-cn` 通过已认证的 FlyAI CLI 获取飞猪/旅行数据。源码和 `package-lock.json` 应提交到 Git；`node_modules` 不提交。

安装依赖并添加到 Codex MCP：

```bash
cd "${HOME}/Desktop/workplace/whisper-travel-skill/tools/flyai-cli-mcp"
npm install
codex mcp add flyai-cli -- node "${HOME}/Desktop/workplace/whisper-travel-skill/tools/flyai-cli-mcp/server.mjs"
```

FlyAI key 不要提交到仓库。可放到默认 secrets 文件：

```bash
mkdir -p "${HOME}/.config/mcp"
printf 'FLYAI_API_KEY=你的FlyAIKey\n' >> "${HOME}/.config/mcp/secrets.env"
chmod 600 "${HOME}/.config/mcp/secrets.env"
```

## 仓库内容约定

- `travel-planning-cn/`：完整旅行规划总控技能目录，必须提交。
- `hotel-search-cn/`：酒店搜索子技能目录，必须提交。
- `*/evals/`：评测用例定义，建议提交。
- `tools/flyai-cli-mcp/`：技能依赖的 FlyAI MCP 支撑工具，建议提交源码与锁文件。
- `*-workspace/iteration-*`：技能迭代产生的本地评测结果、报告和调试产物，不提交到 Git。
- `.browser-profiles/`、`.playwright-mcp/`、`node_modules/`、`.env*`：本地会话、依赖或敏感信息，不提交到 Git。
