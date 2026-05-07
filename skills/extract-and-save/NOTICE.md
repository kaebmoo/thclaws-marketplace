# NOTICE

This skill is original work authored by ThaiGPT Co., Ltd. (the
thClaws project) — not a derivative of an upstream skill. Distributed
via the thClaws marketplace at `github.com/thClaws/marketplace` under
the Apache License 2.0.

Copyright © 2026 ThaiGPT Co., Ltd.

## What this skill does

Pure-prompt skill (no scripts) for the recurring knowledge-worker
task of extracting structured information from one file and saving
it to another. Handles the cross-product of input formats (image,
PDF, DOCX, PPTX, XLSX, markdown, plain text) and output formats
(XLSX, DOCX, PPTX, PDF, markdown, JSON).

Common workflows it supports:

- Namecard photo → `contacts.xlsx`
- Receipt / invoice photo → `expense.docx` or `line-items.json`
- Contract PDF → `terms.md` (key-clause summary)
- Meeting screenshot → `followup.docx`
- Spreadsheet → JSON for a downstream pipeline
- ID card / passport scan → structured `.json`

The skill is deliberately a pure-prompt workflow — no helper scripts.
thClaws's built-in document toolset (`Read`, `PdfRead` / `PdfCreate`,
`DocxRead` / `DocxEdit` / `DocxCreate`, `PptxRead` / `PptxEdit` /
`PptxCreate`, `XlsxRead` / `XlsxEdit` / `XlsxCreate`, plus `Write`
and `Edit`) covers every step.

## Why `model: gpt-4.1-nano`

The frontmatter declares `gpt-4.1-nano` as the recommended default —
OpenAI's smallest vision-capable model. It's fast and cheap, sized
appropriately for the typical structured-extraction task this skill
handles. When the user has an `OPENAI_API_KEY` set, the agent
silently switches to gpt-4.1-nano for the duration of the turn the
skill is invoked in, then reverts at end of turn. When they don't,
a warning chat status note is shown and the skill proceeds with
whatever vision-capable model the user already had selected.

For documents larger than ~50 pages (PDFs especially), users may
want to manually `/model` up to a larger model before invoking the
skill — nano's strength is small-task throughput, not handling
massive context.

## Tested with

- Claude Sonnet 4.6 (default; vision-capable; long context)
- gpt-4.1-nano (skill's recommended default)
- gpt-4o (fallback when nano isn't available)

Other vision-capable models (Gemini 2.5 Pro, etc.) work too but
haven't been benchmarked across the full input/output matrix.
Field-extraction quality varies with model size on adversarial
inputs (low resolution, dense small text, multi-column layouts).
