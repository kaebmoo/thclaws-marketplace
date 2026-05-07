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
git clone https://github.com/thClaws/marketplace.git
cd marketplace/mcp/telegram-mcp
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
        "TELEGRAM_ALLOWED_CHAT_IDS": "123456789"
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
        "TELEGRAM_ALLOWED_CHAT_IDS": "123456789"
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
| `TELEGRAM_API_BASE` | Optional Telegram-compatible API base URL | `https://api.telegram.org` |
| `MCP_TRANSPORT` | `stdio` for local install, `sse` for HTTP/SSE hosting | `stdio` |
| `MCP_PORT` | Port for SSE transport | `8000` |

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
- File upload tools only accept local file paths. URL-based uploads are intentionally not supported in this first version.
- `telegram_get_updates` filters output to allowlisted chats before returning data to the agent.
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
