---
name: conventional-commits
description: >-
  Analyze changes by purpose and domain, then create or review Conventional
  Commits. Use when the user asks to commit, make a commit, write or fix a
  commit message, review a commit message, choose a commit type or scope, handle
  breaking changes, stage and commit, squash or amend commits, generate a
  changelog entry, or asks "what type should this be". Also use when the user
  says "commit this", "commit my changes", or "git commit".
license: MIT
metadata:
  author: Ash Li
  version: '2026-08-25'
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

When the user asks to commit changes, that request authorizes staging and committing
the changes within the scope they named. Do not ask for file-by-file confirmation
unless the semantic commit boundary is genuinely ambiguous.

Follow these steps in order:

1. Run `git status` to determine the working tree state.
2. Stop and tell the user when there is a conflict or an in-progress merge,
   rebase, or cherry-pick. Stop when there are no changes.
3. Determine the candidate changes:
   - Honor an explicit scope such as "staged changes only", named paths, or a
     named feature.
   - Otherwise, consider all staged, unstaged, and untracked changes. Existing
     staging state alone is not a semantic boundary and does not require a
     question.
4. Read the complete candidate changes before deciding their commit boundaries.
   Inspect both staged and unstaged diffs and read relevant untracked files;
   stats, name-status output, and file lists are not sufficient substitutes.
5. Partition the changes into cohesive commit units by purpose and semantic
   domain. A domain is a coherent product capability or component, not a file or
   directory. Paths are evidence, but file count and directory count are not
   decision criteria:
   - Multiple files belong together when they implement one purpose in one
     module or domain, including its tests, docs, migrations, generated files,
     and dependency or lockfile updates.
   - One file may contain multiple commit units when independent changes affect
     different purposes or domains.
   - Different modules or domains are separate commit units. Also separate
     changes that can be understood, reverted, or reviewed independently,
     especially unrelated behavior, formatting, or maintenance.
6. Choose the matching path:
   - **One cohesive commit unit** — Stage the whole unit, including all related
     files or hunks, and continue without asking for confirmation.
   - **Multiple commit units** — Present an ordered split plan with the proposed
     Conventional Commit message and included files or hunks for each commit.
     Ask once whether to execute that plan, and wait for the user's response
     before changing the index or committing.
   - **Ambiguous boundary** — Ask only the smallest question needed when the
     content does not provide enough evidence to decide whether changes belong
     together.
7. For each authorized commit unit, stage only that unit and run
   `git diff --staged`. Read the full staged diff and verify that it contains the
   complete unit and no changes from another unit.
8. Select type and scope from the staged diff, detect the language from recent
   commits, and write the commit message.
9. Validate the message against this spec and the staged diff, then commit with
   `git commit -m`.
10. After all planned commits, run `git status` and report the created commits
    and any remaining changes.

### Splitting Commits

Decide whether to split from semantic intent, not from the number of changed
files, directories, or staging states. Two or more semantic domains require a
split plan and confirmation. Look for:

- Changes to different modules or domains.
- A mix of behavior changes and formatting/style changes.
- Multiple distinct purposes that would need separate subjects.

Do not split a cohesive change merely because it touches many files or combines
implementation with its supporting tests, docs, schema changes, or generated
artifacts. Conversely, consider splitting a single file when it contains
independent changes. If a safe split requires hunk-level staging, use it rather
than grouping unrelated changes by filename.
