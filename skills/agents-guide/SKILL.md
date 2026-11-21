---
name: agents-guide
description: >-
  Create, update, review, shorten, migrate, and organize AGENTS.md and
  CLAUDE.md files. Use when the user asks to write a repository guide for
  coding agents, add or change project instructions, refresh outdated
  instructions, fix inaccurate setup/build/test guidance, split guidance for
  subprojects, packages, apps, or services into nested AGENTS.md files, or make
  existing AGENTS.md/CLAUDE.md content clearer and less noisy: for example
  "写一份 AGENTS.md", "精简 CLAUDE.md", "加一条项目指令", "更新 agent 指令".
license: MIT
metadata:
  author: Ash Li
  version: '2026-11-21'
---

# Agents Guide

Maintain `AGENTS.md` and `CLAUDE.md` as concise onboarding documents for coding
agents. Treat `AGENTS.md` as the source of truth; when `CLAUDE.md` is needed,
make it a symlink to `AGENTS.md` instead of maintaining duplicate content.

## Principles

- Explain WHAT the project is, WHY important parts exist, and HOW agents should
  work safely.
- Keep root guidance short. Every line loads into every session, so keep only
  instructions that apply to most tasks in that directory scope.
- Add a line only for a real problem: a repeated correction, a convention agents
  cannot infer, or an explicit user request. Derive each line from repository
  evidence or the user, not from a template.
- Put task-specific or subsystem-specific details in clearly named docs and
  point to them with a brief "read when..." description.
- Link to authoritative files, commands, or docs instead of pasting snippets or
  generated inventories that go stale.
- Route each instruction to the mechanism that fits it:
  - A rule that a formatter, linter, hook, or CI check can enforce: name the
    tool or command instead of restating the rule.
  - A multi-step workflow that only some tasks need: suggest a skill.
  - Anything else that applies to most tasks: the guide.
- Do not put secrets, credentials, connection strings, or vulnerability details
  in a guide. Treat it as public.

## Workflow

1. Classify the request: create or refresh a guide, add or change one
   instruction, review or shorten, migrate between `CLAUDE.md` and `AGENTS.md`,
   or split guidance across subprojects.
2. Discover only the facts the request needs: existing `AGENTS.md` and
   `CLAUDE.md`, README files, package manifests, task runners, CI workflows, and
   docs that define setup, build, lint, typecheck, and test commands. Inspect
   the repository shape before adding nested `AGENTS.md` files.
3. Choose the narrowest edit:
   - For one instruction, update the nearest applicable guide and leave
     unrelated sections alone.
   - Put repository-wide guidance in the root `AGENTS.md`. Put subproject
     guidance in the nearest nested `AGENTS.md`, and align nested boundaries
     with real subprojects.
   - For a new guide, do not fill out a template. Omit empty categories. If the
     only clear request is one instruction, create the smallest valid
     `AGENTS.md` that contains it.
4. Remove stale commands, duplicated content, tool-output dumps, broad
   behavioral patches, and style rules already enforced by tools.
5. Validate before finishing:
   - Check that listed commands and paths exist or are documented conventions.
     Copy commands from authoritative files.
   - Preserve explicit user instructions. If they conflict with repository
     facts, surface the conflict instead of silently overriding them. Resolve
     conflicts between guides by user intent, then by directory specificity.
   - For revisions, confirm the guide is clearer and more generally applicable
     than the version it replaces.

## Migration

Use `AGENTS.md` as the canonical file whenever both names are involved.

- If only `CLAUDE.md` exists, move its still-valid, broadly applicable content
  into `AGENTS.md`, then replace `CLAUDE.md` with a relative symlink to
  `AGENTS.md`.
- If both files exist, compare them first. Merge only useful, non-duplicative,
  still-valid `CLAUDE.md` content into `AGENTS.md`; then replace `CLAUDE.md`
  with a relative symlink to `AGENTS.md`.
- If `CLAUDE.md` is already a symlink, verify it points to the intended
  `AGENTS.md` and update only when the target is wrong.
- Do not delete a regular `CLAUDE.md` until its relevant content has been
  preserved in `AGENTS.md`.

For files in the same directory, after preserving content and removing the
regular `CLAUDE.md`, create the symlink with:

```bash
ln -s AGENTS.md CLAUDE.md
```

## Writing Style

- Write in the language of the repository's existing docs, such as the README
  and other guides. Use English when the repository has no docs.
- Use imperative or direct rule form, for example "Run `vp run format` before
  finishing".
- Prefer short bullets over paragraphs.
- Keep rationale out unless it changes how an agent should behave.
- Avoid "always" and "never" unless the user explicitly requests them or
  repository evidence makes the rule necessary.
