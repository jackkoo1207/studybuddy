# StudyBuddy Agent Knowledge Base

Only two files matter — they are concatenated as system prompts for the two runtime agents:

| File | Agent | Where it's used |
|---|---|---|
| `lesson-planner-agent.md` | 課程設計師 (Lesson Planner) | `POST /api/generate-plan` → DeepSeek (serve.py loads it; inline fallback if missing) |
| `tutor-agent.md` | 英語導師 (Tutor, ElevenLabs Convai) | Live voice lesson system prompt / `lesson_context` injection |

- `raw/` — archival source books (Doman, etc.), read-only reference, never loaded into prompts.
- Keep these two files self-contained: no wiki links, no citations, no changelogs. Every rule in them must be executable at runtime.
