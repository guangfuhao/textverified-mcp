# TextVerified 插件

[English README](README.en.md) · [GitHub](https://github.com/guangfuhao/textverified-mcp) · [TextVerified API v2 文档](https://app.textverified.com/docs/api/v2#overview)

`textverified-mcp` 是一个可安装到 Codex、ChatGPT 以及其他兼容 Agent 的 TextVerified 插件。它封装完整的 TextVerified API v2，并为 SMS 和 voice verification 提供快捷工作流。

## 一句话安装

把下面这句话直接发给支持插件的 Agent：

> 请从 https://github.com/guangfuhao/textverified-mcp 安装 TextVerified 插件，安装完成后打开插件设置页面，让我配置 TextVerified 用户名和 API Key。

Codex CLI 也可以从个人或仓库 marketplace 安装：

```bash
codex plugin marketplace add https://github.com/guangfuhao/textverified-mcp
codex plugin add textverified-mcp
```

不同 Agent 的插件目录和命令可能不同；上面的一句话安装请求会让 Agent 选择其支持的安装方式。

## 首次配置

插件安装后会通过 `textverified-setup` onboarding skill 引导用户进入独立的 **TextVerified 插件设置页面**，填写：

- **TextVerified username**：TextVerified 注册邮箱；
- **TextVerified API key**：TextVerified 主 API Key；
- **API base URL**：默认使用 `https://www.textverified.com`。

保存后，插件把凭据写入当前用户的本地配置文件，并设置为仅文件所有者可读（权限 `0600`）。API Key 在设置读取结果中始终显示为掩码，不会写入 GitHub、README、聊天消息或工具参数。无图形设置页的 CI/headless 环境可以使用 `TEXTVERIFIED_USERNAME` 和 `TEXTVERIFIED_API_KEY` 环境变量。

如果插件宿主支持 OpenAI MCP Extensions，设置页由 `openai/settings` capability 原生渲染；其他宿主会执行 onboarding skill，并提示使用其安全配置方式。

## 支持能力

- `textverified_request`：调用所有 `/api/pub/v2/*` API v2 接口；
- 创建和查询 SMS/voice verification；
- 查询和发送 SMS；
- 查询语音通话并创建来电访问令牌；
- 创建租号；
- 访问服务、价格、库存、计费、backorder、唤醒请求、webhook 定义和分页链接等其他接口。

完整 OpenAPI 合同见 [`docs/api-v2.openapi.json`](docs/api-v2.openapi.json)，接口清单见 [`docs/endpoints.md`](docs/endpoints.md)。

## 安全行为

购买、退款、续期、回复、发送 SMS、扩展等操作可能消耗余额或改变账号状态。快捷写操作要求显式确认参数，通用 API 工具也应只在明确了解请求后使用。建议集成测试优先使用官方文档中的 `test_*` mock 服务名。

客户端会缓存短期 bearer token，对临时网络错误、429 和 5xx 做有上限的退避重试，支持 `Idempotency-Key`，并限制请求只能访问 TextVerified API v2 域名。

## 本地开发

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
```

测试使用本地 mock transport，不会访问 TextVerified，也不会购买号码。

## 项目文件

- `plugin.json`：可移植 Agent Plugins 清单；
- `mcp.json`：插件内置 stdio MCP server 配置；
- `.agents/plugins/marketplace.json`：从 GitHub 仓库发现和安装插件的 marketplace 清单；
- `skills/setup/SKILL.md`：首次安装配置引导；
- `skills/textverified-usage/SKILL.md`：使用与安全规则；
- `docs/api-v2.openapi.json`：官方 API v2 OpenAPI 快照；
- `src/textverified_mcp/`：Python 客户端和 MCP server。

## 许可

MIT。本项目是独立的社区客户端，TextVerified 商标归其权利人所有，TextVerified 未对本项目作任何背书。
