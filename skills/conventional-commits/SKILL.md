---
name: conventional-commits
description: Commit code changes using Conventional Commits. Use when the user asks to commit, make a commit, write a commit message, fix a commit message, review a commit message, choose a commit type or scope, handle breaking changes, stage and commit, squash or amend commits, generate a changelog entry, or asks "what type should this be". Also use when the user says "commit this", "commit my changes", or "git commit".
license: MIT
metadata:
  author: Ash Li
  version: '2026-04-29'
---

# Conventional Commits

Write structured commit messages that are human-readable and machine-parseable, based on Conventional Commits 1.0.0.

## Message Format

```text
<type>[optional scope][optional !]: <subject>

[optional body]

[optional footer(s)]
```

## Types

Select one type:

- `feat`: new feature.
- `fix`: bug fix.
- `docs`: docs only.
- `style`: formatting only.
- `refactor`: restructure only.
- `perf`: performance.
- `test`: tests.
- `build`: build or deps.
- `ci`: CI.
- `chore`: maintenance.
- `revert`: revert.
- `wip`: incomplete work (non-standard; excluded from changelogs).
- `release`: release work (non-standard; excluded from changelogs).

### Choosing Between Similar Types

When the change touches multiple concerns, pick the type that best describes the primary intent:

- **feat vs refactor**: Does the change add observable behavior (new endpoint, new UI element, new config option)? Use `feat`. If behavior is unchanged from the user's perspective, use `refactor`.
- **fix vs refactor**: Does the change correct wrong behavior (bug, crash, incorrect output)? Use `fix`. If the code was working but poorly structured, use `refactor`.
- **fix vs chore**: Does the change fix a user-facing bug? Use `fix`. If it fixes a build script, updates a lockfile, or corrects a dev-only issue, use `chore`.
- **feat vs perf**: Does the change add a new capability? Use `feat`. If it makes an existing capability faster without changing its interface, use `perf`.
- **chore vs build**: Does the change modify the build system or external dependencies (webpack config, Dockerfile, package.json deps)? Use `build`. For other maintenance tasks (renaming files, updating .gitignore), use `chore`.
- **style vs refactor**: Does the change only affect whitespace, semicolons, or formatting? Use `style`. If it renames variables, extracts functions, or restructures logic (even without behavior change), use `refactor`.

When a commit genuinely spans two types, prefer splitting into separate commits. If splitting is impractical, use the higher-impact type.

## Scope

- Omit scope by default.
- Use scope when the repository has an established scope convention.
- Use scope when the user asks for one.

Use the Jira key as scope when the current branch matches `feature/[JIRA-KEY]` or `feature/[JIRA-KEY]-*`. A Jira key is an uppercase alphabetic prefix followed by a hyphen and digits (e.g., `PROJ-123`). Only the `feature/` prefix triggers scope extraction; other prefixes like `fix/` or `hotfix/` do not.

```bash
git branch --show-current
```

Branch examples:

```text
feature/PROJ-123       -> feat(PROJ-123): add passkey login
feature/PROJ-123-login -> feat(PROJ-123): add passkey login
feature/auth           -> feat: add passkey login
fix/BUG-42             -> fix: handle expired sessions  (no scope)
main, develop          -> no scope implied
```

## Subject

Use imperative form:

- Use `add`, not `added` or `adds`.
- Use lowercase except for proper nouns, acronyms, issue IDs, and user-facing names.
- Do not end with a period.
- Keep it under 72 characters.

## Body

- Omit the body by default.
- Add a body only when the user asks for one.
- Explain what and why; do not repeat the header.

## Footers

- Use footers for trailers such as issues, reviewers, and breaking changes.
- Use hyphens in footer tokens, except `BREAKING CHANGE`.

```text
Refs: #123
Reviewed-by: Name
BREAKING CHANGE: environment variables now override config files
```

## Breaking Changes

- Mark breaking changes with `!` in the header, a `BREAKING CHANGE:` footer, or both.
- When writing a new breaking-change commit message, prefer using both `!` and a `BREAKING CHANGE:` footer.
- Explain migration impact when using the footer.

```text
feat(api)!: require explicit tenant id

BREAKING CHANGE: API clients must pass tenantId on every request.
```

## Language

- Match language in subject, body, and footer values.
- Keep type, scope, and footer keys unchanged.

Detect the dominant language from the latest 10 non-merge commit subjects:

```bash
git log --no-merges -10 --pretty=%s
```

Use the dominant language when clear. If the repository has fewer than 3 non-merge commits, use English. Otherwise, use English when no dominant language is clear.

## Review

When asked to review a commit message:

1. Check format: type, scope syntax, subject case and length, body separation, footer format.
2. Check semantics: does the type match the staged diff? A `docs` commit should not contain logic changes.
3. Check breaking changes: require at least one valid marker (`!` in the header or `BREAKING CHANGE:` footer). If both are present, confirm they describe the same breaking change.
4. Report: state whether the message is valid, then list specific fixes if needed.

## Commit Workflow

### Steps

Follow these steps in order. Do not skip ahead.

1. Run `git status` to determine the working tree state.
2. Based on the `git status` output, apply the **first matching rule** below:
   - **Conflict or in-progress operation** (merge, rebase, cherry-pick, unresolved conflicts) — The repository is unstable. Committing now could produce a broken history. Tell the user and stop; do not proceed.
   - **No changes** — Nothing to commit. Tell the user and stop; do not proceed.
   - **All changes staged** — You have everything you need. Continue to step 3.
   - **Only unstaged or untracked changes** — `git diff --staged` would be empty, so you cannot write a meaningful message. Ask the user which files to stage, then **wait for their response** before continuing. You may suggest staging all if changes look related, but the user decides scope.
   - **Partially staged** — There are staged changes already, but the user may want more in this commit. Ask whether to commit staged only or stage additional changes, then **wait for their response**. Default to staged only — including unconfirmed work risks committing changes the user did not intend to share yet.
3. Stage only the files the user explicitly confirmed.
4. Run `git diff --staged` and read the full diff. `git diff --staged --stat`, `git diff --staged --name-status`, and file lists are not sufficient substitutes.
5. Select type and scope based on the staged diff content.
6. Detect language from recent commits and confirm it fits the staged diff.
7. Write the commit message (subject, optional body, optional footers).
8. Validate the message against this spec and the staged diff.
9. Commit with `git commit -m`.

### Splitting Commits

If the staged diff contains unrelated changes, suggest splitting into separate commits. Look for:

- Changes to unrelated files or modules.
- A mix of behavior changes and formatting/style changes.
- Multiple distinct purposes that would need separate subjects.

Do not force splits for small, cohesive changes even if they touch multiple files.
