# NOTICE

This skill is original work authored by ThaiGPT Co., Ltd. (the
thClaws project) — not a derivative of an upstream skill. Distributed
via the thClaws marketplace at `github.com/thClaws/marketplace` under
the Apache License 2.0.

Copyright © 2026 ThaiGPT Co., Ltd.

## What this skill does

Pure-prompt skill (no scripts) that turns a namecard photo into a row
in a `contacts.xlsx` Excel file. Uses thClaws's built-in `Read` tool
to ingest the image, the model's vision capability to extract fields,
and built-in `XlsxCreate` / `XlsxEdit` to write the spreadsheet.

## Why `model: gpt-4.1-nano`

The frontmatter declares `gpt-4.1-nano` as the recommended default
model — it's OpenAI's smallest vision-capable model and a good fit
for the small, structured visual task of namecard OCR (fast and
cheap, no heavyweight model needed). When the user has an
`OPENAI_API_KEY` set, the agent silently switches to gpt-4.1-nano for
the duration of the turn the skill is invoked in, then reverts at end
of turn. When they don't, a warning chat status note is shown and the
skill proceeds with whatever vision-capable model the user already
had selected.

## Tested with

- Claude Sonnet 4.6 (current default, vision-capable)
- gpt-4.1-nano (skill's recommended default)
- gpt-4o (alternative if nano isn't available)

Other vision-capable models (Gemini 2.5 Pro, etc.) work too but
haven't been benchmarked for namecard accuracy. Field-extraction
quality may vary.
