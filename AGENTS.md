# AGENTS.md

## Project Overview

This repository contains reusable Agent Skills for `vpx skills` and skills.sh-compatible clients. Each skill lives in `skills/<skill-name>/` and must include a `SKILL.md` file.

## Development

Run these commands from the repository root:

- Install dependencies: `vp install`
- Format files: `vp run format`
- Validate local skill discovery: `vpx skills add . --list`

## Skill Authoring

Place each skill at `skills/<skill-name>/SKILL.md`. Keep the `name` frontmatter value identical to the parent directory name.

Use `references/`, `scripts/`, and `assets/` only when a skill needs progressive disclosure, executable helpers, or bundled resources.

Every `SKILL.md` frontmatter must include:

```yaml
metadata:
  author: Ash Li
  version: 'YYYY-MM-DD'
```

Use the release or update date for `metadata.version`. Quote date-like, numeric, and boolean-like metadata values so YAML parsers keep them as strings. Do not add `metadata.source` unless explicitly requested.

## PR & Commit Guidelines

Use Conventional Commits for commit messages. Prefer the `conventional-commits` skill when creating, reviewing, or repairing commit messages.
