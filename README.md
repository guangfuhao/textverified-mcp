# TextVerified MCP / TextVerified API v2

[English](#english) · [中文](#中文)

<a id="english"></a>

## English

`textverified-mcp` is a small, security-conscious [Model Context Protocol](https://modelcontextprotocol.io/) server and Python client for the complete TextVerified API v2. It works with MCP hosts such as Claude Desktop, ChatGPT-compatible MCP clients, Cursor, and other assistants that support stdio MCP servers.

It exposes one complete API escape hatch, `textverified_request`, generated from the official v2 OpenAPI contract, plus focused tools for common SMS and voice verification workflows:

- create and inspect a verification;
- list and send SMS;
- list calls and create an incoming-call access token;
- create rentals;
- call every other current v2 endpoint through the generic request tool, including pricing, inventory, billing, rentals, backorders, wake requests, webhook definitions, and pagination links.

The checked-in contract is [`docs/api-v2.openapi.json`](docs/api-v2.openapi.json); the endpoint manifest is [`docs/endpoints.md`](docs/endpoints.md).

### Codex plugin installation

This repository is also packaged as a portable Codex plugin with `plugin.json`, `mcp.json`, and the `textverified-usage` skill. Install it from the repository marketplace or add the local folder to a personal marketplace. The bundled launcher uses the repository virtual environment when available and otherwise falls back to `uv run`; credentials remain environment-only.

### Authentication

TextVerified v2 requires **both** the account username (the registration email) and the primary API key to mint a short-lived bearer token. Configure them as environment variables:

```bash
export TEXTVERIFIED_USERNAME='you@example.com'
export TEXTVERIFIED_API_KEY='your-primary-api-key'
```

The key is read only at runtime, never printed, and never belongs in a repository, issue, prompt, or client configuration committed to Git. If the key has been pasted into a public or shared conversation, rotate it in TextVerified API Settings after setup.

### Install and run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
textverified-mcp
```

The default transport is stdio. To use another transport supported by your MCP host, set `TEXTVERIFIED_MCP_TRANSPORT` accordingly.

Example Claude Desktop entry (adapt the absolute path and environment to your machine):

```json
{
  "mcpServers": {
    "textverified": {
      "command": "/absolute/path/to/textverified-mcp/.venv/bin/textverified-mcp",
      "env": {
        "TEXTVERIFIED_USERNAME": "you@example.com",
        "TEXTVERIFIED_API_KEY": "your-primary-api-key"
      }
    }
  }
}
```

### Safe usage

Purchase, refund, renewal, reply, extension, and other state-changing calls can spend credits or change account state. The focused purchase and send tools require an explicit confirmation flag. The generic tool intentionally remains complete and therefore should be used only when the operation is understood. Prefer the documented `test_*` mock service names and the Postman mock collection for integration tests.

The client caches bearer tokens, follows documented links, retries temporary network/5xx/429 failures with bounded exponential backoff, supports `Idempotency-Key` for create requests, and blocks non-TextVerified URLs.

### Development

```bash
pip install -e '.[dev]'  # or install pytest separately
pytest -q
```

The tests use a local mock transport and never call TextVerified or purchase a number.

### License

MIT. TextVerified is a trademark of its respective owner; this project is an independent community client and is not endorsed by TextVerified.

<a id="中文"></a>

## 中文

`textverified-mcp` 是一个面向完整 TextVerified API v2 的安全 MCP 服务端和 Python 客户端，可接入 Claude Desktop、兼容 ChatGPT MCP 的客户端、Cursor 以及其他支持 stdio MCP 的 AI 助手。

它提供一个覆盖全部 API 的 `textverified_request` 通用工具，并提供适合高频验证流程的快捷工具：

- 创建和查询验证任务；
- 查询和发送 SMS；
- 查询语音通话并创建来电访问令牌；
- 创建租号；
- 通过通用工具访问当前 v2 的其他全部接口，包括价格、库存、计费、租号、backorder、唤醒请求、webhook 定义和分页链接。

官方文档对应的 OpenAPI 合同保存在 [`docs/api-v2.openapi.json`](docs/api-v2.openapi.json)，接口清单在 [`docs/endpoints.md`](docs/endpoints.md)。

### Codex 插件安装

本仓库同时包含可安装的 Codex 插件包：`plugin.json`、`mcp.json` 和 `textverified-usage` 技能。可以从仓库 marketplace 或个人 marketplace 安装。启动脚本优先使用仓库虚拟环境，否则使用 `uv run`；凭据只通过环境变量注入。

### 认证配置

TextVerified v2 生成短期 bearer token 时需要 **账号用户名（注册邮箱）和主 API Key 两项**。请通过环境变量配置：

```bash
export TEXTVERIFIED_USERNAME='you@example.com'
export TEXTVERIFIED_API_KEY='你的主 API Key'
```

API Key 只在运行时读取，不会打印，也不会写入仓库、issue、提示词或提交的客户端配置。如果 API Key 曾被粘贴到公开或共享对话中，建议在 TextVerified 的 API Settings 中轮换。

### 安装和运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
textverified-mcp
```

默认使用 stdio。若 MCP 宿主支持其他传输方式，可设置 `TEXTVERIFIED_MCP_TRANSPORT`。

Claude Desktop 配置示例（请改成你机器上的绝对路径，并通过环境变量注入凭据）：

```json
{
  "mcpServers": {
    "textverified": {
      "command": "/absolute/path/to/textverified-mcp/.venv/bin/textverified-mcp",
      "env": {
        "TEXTVERIFIED_USERNAME": "you@example.com",
        "TEXTVERIFIED_API_KEY": "你的主 API Key"
      }
    }
  }
}
```

### 安全使用

购买、退款、续期、回复、扩展等改变状态的操作可能消耗余额或改变账号状态。快捷的购买和发送工具要求显式传入确认标志；通用工具为了覆盖全部 API 会保持完整能力，因此只应在明确了解操作后调用。集成测试优先使用文档中的 `test_*` mock 服务名和 Postman mock collection。

客户端会缓存 bearer token，对官方返回的链接进行跟随，对临时网络错误、5xx 和 429 做有上限的指数退避重试，支持创建操作的 `Idempotency-Key`，并阻止访问非 TextVerified 域名。

### 开发

```bash
pip install -e '.[dev]'  # 或单独安装 pytest
pytest -q
```

测试只使用本地 mock transport，不会访问 TextVerified，也不会购买号码。

### 许可

MIT。本项目是独立的社区客户端，TextVerified 商标归其权利人所有，TextVerified 未对本项目作任何背书。
