**Plan: Telegram MCP สำหรับ thClaws Marketplace**

เป้าหมายคือเพิ่ม `telegram-mcp` เข้า `thClaws/marketplace` เป็น MCP server ที่ให้ thClaws agent ติดต่อ Telegram ได้ โดยไม่แก้ core ของ `thClaws/thClaws`

**Scope**
ทำภายใต้ repo `thClaws/marketplace`:

```text
mcp/
  telegram-mcp/
    README.md
    LICENSE
    NOTICE.md
    pyproject.toml
    telegram_mcp/
      __init__.py
      server.py
    tests/
      test_server.py
```

MCP tools รอบแรก:

```text
telegram_send_message(chat_id, text, parse_mode?)
telegram_send_photo(chat_id, file_path, caption?)
telegram_send_document(chat_id, file_path, caption?)
telegram_get_updates(limit?)
```

ยังไม่ทำ Telegram เป็น UI chat หลัก และยังไม่ทำ approval flow แบบรอ reply ใน PR แรก เพื่อลด scope และ security risk

**Implementation Plan**
1. Fork และสร้าง branch

```bash
git clone https://github.com/<YOUR_USERNAME>/marketplace.git
cd marketplace
git checkout -b feat/telegram-mcp
```

2. สร้าง MCP package ใต้ `mcp/telegram-mcp/`

ใช้ Python เป็นตัวเลือก pragmatic เพราะทำ HTTP ไป Telegram Bot API ง่ายและ test ง่าย

`pyproject.toml` ควรมี:
- package name เช่น `thclaws-telegram-mcp`
- dependencies: MCP SDK หรือ JSON-RPC stdio implementation ที่เลือกใช้, `httpx`
- dev dependencies: `pytest`, `respx` หรือ mock HTTP equivalent

3. Implement config ผ่าน environment variables เท่านั้น

```text
TELEGRAM_BOT_TOKEN            required
TELEGRAM_ALLOWED_CHAT_IDS     required/recommended, comma-separated
TELEGRAM_API_BASE             optional, default https://api.telegram.org
```

ห้าม hardcode token และห้ามใส่ token ใน README ตัวอย่างจริง

4. Implement security checks

ทุก tool ที่รับ `chat_id` ต้องตรวจว่าอยู่ใน `TELEGRAM_ALLOWED_CHAT_IDS`

ถ้าไม่อยู่ ให้ return error ชัดเจน เช่น:

```text
chat_id is not allowed by TELEGRAM_ALLOWED_CHAT_IDS
```

สำหรับ `send_photo` / `send_document`:
- ตรวจว่า `file_path` มีอยู่จริง
- หลีกเลี่ยงอ่าน path จาก URL ใน PR แรก
- จำกัดเป็น local file path เท่านั้น

5. Implement MCP tools

`telegram_send_message`
- input: `chat_id`, `text`, optional `parse_mode`
- call Telegram `sendMessage`
- return summary เช่น message id, chat id

`telegram_send_photo`
- input: `chat_id`, `file_path`, optional `caption`
- call `sendPhoto` multipart upload

`telegram_send_document`
- input: `chat_id`, `file_path`, optional `caption`
- call `sendDocument` multipart upload

`telegram_get_updates`
- input: optional `limit`, optional `offset`
- call `getUpdates`
- return compact JSON/text summary
- ไม่ควร poll ถาวรใน PR แรก

6. Add tests

Test cases ขั้นต่ำ:
- missing `TELEGRAM_BOT_TOKEN` fails clearly
- allowed chat id passes
- disallowed chat id fails
- `send_message` builds correct Telegram API request
- `get_updates` handles Telegram API response
- file upload rejects missing file
- Telegram API error surfaces as MCP tool error

7. Add README

README ต้องมี:
- what it does
- install / local run
- `.thclaws/mcp.json` example
- environment variables
- tool list
- security notes
- limitations

ตัวอย่าง `.thclaws/mcp.json`:

```json
{
  "mcpServers": {
    "telegram": {
      "command": "python",
      "args": ["-m", "telegram_mcp"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "replace-with-your-token",
        "TELEGRAM_ALLOWED_CHAT_IDS": "123456789"
      }
    }
  }
}
```

8. Add license files

ตาม marketplace requirement:
- `LICENSE` เป็น Apache-2.0 หรือ MIT
- `NOTICE.md` ถ้าเป็น original work ให้เขียนสั้น ๆ ว่า original implementation for thClaws marketplace
- ถ้าเอา code จาก repo อื่น ต้องระบุ source/license/modifications ให้ครบ

9. Local verification

จาก root ของ `marketplace`:

```bash
python -m pytest mcp/telegram-mcp/tests
python -m compileall mcp/telegram-mcp/telegram_mcp
```

ถ้ามี formatter/linter ใน repo ให้รันตามนั้นด้วย

10. Commit

```bash
git add mcp/telegram-mcp
git commit -m "feat: add Telegram MCP server"
git push -u origin feat/telegram-mcp
```

**PR Plan**
เปิด PR ไปที่:

```text
base: thClaws/marketplace:main
compare: <YOUR_USERNAME>/marketplace:feat/telegram-mcp
```

PR title:

```text
feat: add Telegram MCP server
```

PR description:

```md
## Summary
Adds a Telegram MCP server under `mcp/telegram-mcp` so thClaws agents can send messages, photos, documents, and read updates through the Telegram Bot API.

## Scope
- Adds `telegram_send_message`
- Adds `telegram_send_photo`
- Adds `telegram_send_document`
- Adds `telegram_get_updates`
- Uses environment variables for configuration
- Enforces `TELEGRAM_ALLOWED_CHAT_IDS`

## Security
- Bot token is read only from `TELEGRAM_BOT_TOKEN`
- No secrets are committed
- Outbound messages are restricted to allowlisted chat IDs
- File uploads only support local paths in this first version

## Testing
- [ ] `python -m pytest mcp/telegram-mcp/tests`
- [ ] `python -m compileall mcp/telegram-mcp/telegram_mcp`

## Notes
This PR intentionally does not implement Telegram as a thClaws UI transport. It only adds Telegram as an MCP/tool surface for agent-initiated communication.
```

**Definition Of Done**
PR พร้อมส่งเมื่อ:
- MCP server รันผ่าน stdio ได้
- tools ทั้ง 4 ทำงานกับ mocked Telegram API ใน tests
- README มีตัวอย่าง config ใช้งานกับ thClaws
- ไม่มี token/example secret จริงใน repo
- มี `LICENSE` และ `NOTICE.md`
- PR scope ไม่แตะ core และไม่รวม Telegram UI bridge ในรอบนี้