# Skills

Drop self-contained **skills** in this directory. A skill is a folder with a
`SKILL.md` that packages instructions (and optional scripts/references) the bot
loads *on demand* — only when the model decides the skill is relevant, so it
never bloats every conversation.

Everything here (except this `README.md` and the `*.example` template) is
**gitignored**, so your skills never affect `git status` and survive `git pull`.

## Quick start

```bash
# 1. Copy the template into a real skill folder (one folder per skill)
mkdir skills/release-notes
cp skills/example/SKILL.md.example skills/release-notes/SKILL.md

# 2. Enable skills, then restart the bot
#    .env:               ENABLE_SKILLS=on
#    or the web dashboard: Tools → Skills → Enable
```

The folder name is the skill; the `name` in the frontmatter should match it.

## Folder layout

```
skills/
└── release-notes/
    ├── SKILL.md          # required: frontmatter (name, description) + instructions
    ├── references/       # optional: supporting docs, read on demand
    └── scripts/          # optional: runnable script templates
```

## How the bot uses a skill

1. **Browse** — Agno injects each skill's `name` + `description` into the system
   prompt. This is the only part the model sees up front.
2. **Load** — when a request matches a description, the model calls
   `get_skill_instructions(<name>)` to load the full `SKILL.md` body.
3. **Reference / scripts** — it then pulls `references/` or `scripts/` as needed.

The `description` is doing all the triggering work — write it like a trigger
(what it does + when to use it). Vague descriptions never fire.

## Notes

- A malformed `SKILL.md` (e.g. missing frontmatter) **stops the bot at startup**
  with a clear error — broken skills are never silently ignored.
- Skills need a model that supports tool/function calling (Gemini, GPT, Claude).
  Lightweight models without it (e.g. `gemma-*`) won't trigger skills.
- Point at a different directory with the `SKILLS_ROOT` environment variable.

See the [Tools docs](https://zhiro-labs.github.io/dango/features/tools#skills)
for the full guide.
