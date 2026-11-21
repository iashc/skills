# AGENTS.md

## Project Overview

This repository contains reusable Agent Skills for `vpx skills` and skills.sh-compatible clients. Each skill lives in `skills/<skill-name>/` and must include a `SKILL.md` file.

## Development

Run these commands from the repository root:

- Install dependencies: `vp install`
- Format files: `vp run format`
- Validate local skill discovery: `vpx skills add . --list`

## Skill Authoring

Place each skill at `skills/<skill-name>/SKILL.md`. Keep the `name` frontmatter value identical to the parent directory name. When you add, remove, or rename a skill, update the skill table in `README.md`.

Use `references/`, `scripts/`, and `assets/` only when a skill needs progressive disclosure, executable helpers, or bundled resources.

- Write `description` as what the skill does and when to use it, without "I" or "you". Include phrases that users type, in English and Chinese. Keep it under 1,024 characters.
- Leave out what agents already do by default. Record rules learned from real failures in a `Common mistakes` section.
- Keep `SKILL.md` under 500 lines. Link each reference file directly from `SKILL.md` and say when to read it. Start reference files longer than 100 lines with a table of contents.
- Use only portable frontmatter keys: `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools`. claude.ai and the Skills API reject Claude Code-only keys such as `context`, `paths`, and `hooks`.

Every `SKILL.md` frontmatter must include:

```yaml
metadata:
  author: Ash Li
  version: 'YYYY-MM-DD'
```

Use the release or update date for `metadata.version`. Quote date-like, numeric, and boolean-like metadata values so YAML parsers keep them as strings. Do not add `metadata.source` unless explicitly requested.

## Evals

Put evals in `evals/<skill-name>/`, outside the skill directory, so installs do not include them.

- Give each skill an `evals/<skill-name>/trigger-cases.json` with `should_trigger` and `should_not_trigger` requests. Include near-miss requests that belong to a neighboring skill.
- When you change a `description`, check it against that file by hand and update the cases.

## PR & Commit Guidelines

Use Conventional Commits for commit messages. Prefer the `conventional-commits` skill when creating, reviewing, or repairing commit messages.
