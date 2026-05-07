---
name: namecard-to-excel
short_description: Extract namecard photo into a contacts Excel file
description: Extract structured contact info from a namecard photo (name, title, company, email, phone, address, website / LinkedIn) and append it as a row in `contacts.xlsx`. Creates the file with a sensible header row if it doesn't exist. Use when the user shares one or more namecard image files (.jpg, .jpeg, .png, .heic, .webp) and asks to add to contacts / capture business cards / log a card / build a Rolodex / scan a stack of namecards. Handles single-language and dual-language (Thai + English) cards. Confirms the extracted fields with the user before writing — names and phone digits are easy to misread.
model: gpt-4.1-nano
---

# Namecard → Excel

Turn a namecard photo into a row in a contacts spreadsheet. Pure-prompt skill — you have everything you need in the built-in toolset (`Read` for the image, `XlsxCreate` / `XlsxEdit` for the file).

## When to invoke

The user has handed you (or pointed at) a namecard image and wants the contact info captured. Triggers include:

- "Add this namecard to contacts"
- "เก็บนามบัตรนี้ลง excel หน่อย"
- "Scan these business cards"
- "I just got back from the conference, here are the cards I collected"
- A drag-and-drop / paste of a `.jpg` / `.png` / `.heic` / `.webp` file with a clear contact-card layout

If the image is something else (a screenshot, a document page, a UI mockup), don't assume namecard — ask the user what they want.

## Procedure

1. **Read the image.** `Read` on the path. The image bytes go to the model; you see what's on the card.
2. **Extract these fields** (skip if absent — don't invent):
   - `name` — full name, English transliteration if dual-language
   - `name_th` — Thai-script name if present, otherwise leave blank
   - `title` — role / job title
   - `company` — organization name
   - `email` — primary email; lowercase the local part
   - `phone` — primary phone in international format if you can infer the country (e.g. `+66 81 234 5678`); otherwise as printed
   - `mobile` — separate mobile if listed alongside an office line
   - `address` — single-line postal address
   - `website` — URL without scheme prefix unless the card shows it
   - `linkedin` — LinkedIn URL or profile slug
   - `notes` — anything else printed on the card worth capturing (tagline, languages spoken, certifications)
3. **Confirm before writing.** Show the user the extracted fields as a markdown bullet list and ask "Save this to contacts.xlsx?" — letters and phone digits are the most-likely-to-misread fields, so a quick confirm beats silent corruption.
4. **Append to `contacts.xlsx`** (relative to the current working directory):
   - If the file doesn't exist, `XlsxCreate` it with header row: `Date | Name | Name (Thai) | Title | Company | Email | Phone | Mobile | Address | Website | LinkedIn | Notes`.
   - If it exists, `XlsxEdit` to append a new row. Date column = today's date in `YYYY-MM-DD`.
   - Empty fields stay empty (don't fill with "N/A" / "—" — those clutter the sheet).
5. **Report back** with a one-liner: which row was added, total rows in the file now, where the file lives.

## Multiple cards in one prompt

If the user drops several photos at once, process them one at a time, confirm each batch (or ask "shall I just save all of them?"), then write a single batch update so the file stays compact.

## Tips for accurate extraction

- **Names**: when the card shows both Latin and Thai script, capture both. Use the Thai column even if the user types only English in conversation — the original script is searchable later.
- **Phone numbers**: prefer the format the card prints, then add the international prefix as an annotation if you can infer it. Don't strip in-country area codes that look unfamiliar — they're often the right answer.
- **Companies with English + native names**: pick the one most prominently displayed. If both are equal, prefer English for a sortable sheet.
- **Logos and tagline-only cards**: the company name might only appear as a logo. If you can't read the company text reliably, leave it blank and mention this to the user; don't guess.
- **Low-resolution photos**: if the image is blurry or cropped, name what you couldn't read so the user can fill it in manually. The skill should fail visibly, not silently with bad data.

## Output template (the confirm message)

```
Found these fields on the card:

- **Name**: Jimmy Pinyo
- **ชื่อภาษาไทย**: จิมมี่ ภิญโญ
- **Title**: Founder & CEO
- **Company**: ThaiGPT Co., Ltd.
- **Email**: jimmy@thaigpt.com
- **Phone**: +66 81 234 5678
- **Website**: thaigpt.com
- **LinkedIn**: jimmypinyo

Save this to `contacts.xlsx`? (or tell me what to fix first)
```

## Why `gpt-4.1-nano`

The model frontmatter (`model: gpt-4.1-nano`) recommends OpenAI's smallest vision-capable model for this skill — it's fast and cheap, and namecard OCR is a small, structured visual task that doesn't need a heavyweight model. If your default model is already vision-capable (Claude Sonnet, GPT-4o, Gemini 2.5 Pro), thClaws will keep your current model when you don't have an OpenAI key. See the chat status line `[model → gpt-4.1-nano (skill recommendation, reverts at end of turn)]` when the swap takes effect.
