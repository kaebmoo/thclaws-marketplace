# thClaws Telegram MCP

Telegram Bot API MCP server for thClaws agents. It lets an agent send messages, photos, documents, and inspect recent bot updates through an allowlisted Telegram bot.

This is a tool surface, not a thClaws UI transport. Use it for notifications, escalation, and sending artifacts after work completes.

## Tools

| Tool | Args | Returns |
|---|---|---|
| `telegram_send_message` | `chat_id`, `text`, optional `parse_mode` | Message id + chat summary |
| `telegram_send_photo` | `chat_id`, `file_path`, optional `caption` | Message id + chat summary |
| `telegram_send_document` | `chat_id`, `file_path`, optional `caption` | Message id + chat summary |
| `telegram_get_updates` | optional `limit`, optional `offset` | Compact JSON for updates from allowlisted chats |

## Install

### Local stdio

```bash
git clone https://github.com/<your-org-or-user>/<your-marketplace-fork>.git
cd <your-marketplace-fork>/mcp/telegram-mcp
pip install -e .
```

Then add the server to `.thclaws/mcp.json` in your project, or to `~/.config/thclaws/mcp.json` for user scope:

```json
{
  "mcpServers": {
    "telegram": {
      "command": "thclaws-telegram",
      "env": {
        "TELEGRAM_BOT_TOKEN": "replace-with-your-bot-token",
        "TELEGRAM_ALLOWED_CHAT_IDS": "123456789",
        "TELEGRAM_ALLOWED_FILE_ROOTS": "/absolute/path/to/reports"
      }
    }
  }
}
```

You can also run it with Python directly:

```json
{
  "mcpServers": {
    "telegram": {
      "command": "python",
      "args": ["-m", "telegram_mcp"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "replace-with-your-bot-token",
        "TELEGRAM_ALLOWED_CHAT_IDS": "123456789",
        "TELEGRAM_ALLOWED_FILE_ROOTS": "/absolute/path/to/reports"
      }
    }
  }
}
```

## Configuration

| Env var | Purpose | Default |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Required Telegram bot token from BotFather | unset |
| `TELEGRAM_ALLOWED_CHAT_IDS` | Required comma-separated allowlist of chat IDs | unset |
| `TELEGRAM_ALLOWED_FILE_ROOTS` | Required for file uploads; comma-separated directories the agent may send files from | unset |
| `TELEGRAM_API_BASE` | Optional Telegram-compatible API base URL | `https://api.telegram.org` |
| `MCP_TRANSPORT` | `stdio` for local install, `sse` for HTTP/SSE hosting | `stdio` |
| `MCP_HOST` | Host bind address for SSE transport | `127.0.0.1` |
| `MCP_PORT` | Port for SSE transport | `8000` |

## Transport and Ports

By default this server uses MCP over stdio:

```text
MCP_TRANSPORT=stdio
```

In stdio mode it does not open a network port. thClaws starts the process and communicates over stdin/stdout.

Only SSE mode opens a port:

```bash
MCP_TRANSPORT=sse MCP_HOST=127.0.0.1 MCP_PORT=8000 thclaws-telegram
```

The default SSE endpoint is:

```text
http://127.0.0.1:8000/sse
```

### Local `.env`

The server reads configuration from process environment variables. It does not parse `.env` files by itself.

For local development, keep a private `.env` at the package root:

```text
mcp/telegram-mcp/.env
```

Use [.env.example](./.env.example) as the template, then export it before running the server:

```bash
cd mcp/telegram-mcp
set -a
source .env
set +a
thclaws-telegram
```

Do not put `.env` under `src/telegram_mcp/`, and do not commit it.

## Test Without thClaws

You can smoke-test the MCP server directly from this package directory.

First export your local environment:

```bash
cd mcp/telegram-mcp
set -a
source .env
set +a
```

Then list tools over stdio:

```bash
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"manual-smoke","version":"0.1.0"}}}' \
  '{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
| ./.venv/bin/python -m telegram_mcp
```

To send a real Telegram message without thClaws, replace `123456789` with an allowlisted chat ID:

```bash
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"manual-smoke","version":"0.1.0"}}}' \
  '{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"telegram_send_message","arguments":{"chat_id":"123456789","text":"Telegram MCP smoke test"}}}' \
| ./.venv/bin/python -m telegram_mcp
```

Running `./.venv/bin/python -m telegram_mcp` by itself is also valid, but it will wait silently for MCP JSON-RPC messages on stdin.

## Finding Your Chat ID

1. Create a bot with Telegram BotFather and copy its token.
2. Send a message to the bot from the chat you want to allow.
3. Query Telegram directly once and inspect the returned `chat.id`:

   ```bash
   curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getUpdates"
   ```

4. Add only the needed IDs to `TELEGRAM_ALLOWED_CHAT_IDS`.

For group chats, Telegram chat IDs are usually negative. Keep the minus sign in the allowlist.

## Security Notes

- The bot token is read only from `TELEGRAM_BOT_TOKEN`.
- No secrets should be committed into `mcp.json`, README examples, screenshots, or tests.
- Every tool is constrained by `TELEGRAM_ALLOWED_CHAT_IDS`.
- File upload tools only accept local file paths under `TELEGRAM_ALLOWED_FILE_ROOTS`. URL-based uploads are intentionally not supported in this first version.
- File upload tools check Telegram's size limits before upload: photos max 10 MB, documents max 50 MB.
- Text messages are limited to Telegram's 4096-character message limit.
- `telegram_get_updates` filters output to allowlisted chats before returning data to the agent.
- SSE transport binds to `127.0.0.1` by default. If you set `MCP_HOST=0.0.0.0`, put the server behind network-level access control; this MCP exposes Telegram actions backed by your bot token.
- Telegram messages may leave your local environment and be stored by Telegram. Do not send secrets unless your operational policy allows it.
- Do not use this MCP server to publish another person's private information without their explicit permission.

## Example Uses

Ask thClaws:

```text
When the tests finish, send me a Telegram message with the result.
```

Or:

```text
Generate the report, then send the PDF to chat 123456789 over Telegram.
```

## Limitations

- This does not make Telegram a chat UI for thClaws.
- It does not implement a long-running approval workflow or wait-for-reply tool yet.
- It does not accept remote file URLs for uploads.
- It does not manage Telegram webhooks.

## License

Apache-2.0 - see [LICENSE](./LICENSE).
