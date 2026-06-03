# whisper-travel-skill

面向中文旅行场景的 Codex/Agent 技能仓库。目前核心技能是 `hotel-search-cn`，用于国内酒店聚合搜索、比价和推荐，覆盖高德定位、FlyAI/飞猪、AIGoHotel、同程程心、携程问道、同程网页端、携程网页端等来源。

## 快速安装

安装到 Codex 技能目录：

```bash
set -e
repo_dir="${HOME}/Desktop/workplace/whisper-travel-skill"
mkdir -p "$(dirname "$repo_dir")" "${HOME}/.codex/skills"
if [ -d "$repo_dir/.git" ]; then
  git -C "$repo_dir" pull --ff-only
else
  git clone https://github.com/whispergong/whisper-travel-skill.git "$repo_dir"
fi
rsync -a --delete "$repo_dir/hotel-search-cn/" "${HOME}/.codex/skills/hotel-search-cn/"
echo "Installed: ${HOME}/.codex/skills/hotel-search-cn"
```

如果希望 Cursor 或其他 agent 也复用同一技能，可同步到 `~/.agents/skills`：

```bash
mkdir -p "${HOME}/.agents/skills"
rsync -a --delete "${HOME}/Desktop/workplace/whisper-travel-skill/hotel-search-cn/" "${HOME}/.agents/skills/hotel-search-cn/"
echo "Installed: ${HOME}/.agents/skills/hotel-search-cn"
```

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

- `hotel-search-cn/`：可安装的技能目录，必须提交。
- `hotel-search-cn/evals/`：评测用例定义，建议提交。
- `tools/flyai-cli-mcp/`：技能依赖的 FlyAI MCP 支撑工具，建议提交源码与锁文件。
- `hotel-search-cn-workspace/iteration-*`：技能迭代产生的本地评测结果、报告和调试产物，不提交到 Git。
- `.browser-profiles/`、`.playwright-mcp/`、`node_modules/`、`.env*`：本地会话、依赖或敏感信息，不提交到 Git。
