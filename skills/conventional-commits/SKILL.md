---
name: conventional-commits
description: >-
  Analyze changes by purpose and domain, then create or review Conventional
  Commit messages and pull request titles. Use when the user asks to commit,
  make a commit, write or fix a commit message, review a commit message, create
  a pull request, write or review a PR title, choose a commit type or scope,
  handle breaking changes, stage and commit, squash or amend commits, generate
  a changelog entry, or asks "what type should this be". Also use when the user
  says "commit this", "commit my changes", "git commit", "create a PR",
  "提交", "写提交信息", "开个 PR", or "这个该用什么 type".
license: MIT
metadata:
  author: Ash Li
  version: '2026-11-21'
---

# Conventional Commits

Write commit messages and pull request titles that follow Conventional Commits
1.0.0, with the conventions below.

## Types

Use the standard types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`,
`test`, `build`, `ci`, `chore`, `revert`. Two non-standard types are also
allowed and are excluded from changelogs:

- `wip`: incomplete work.
- `release`: release work.

When a change spans two types, prefer splitting it. If splitting is
impractical, use the higher-impact type.

## Scope

- Omit scope by default.
- Use scope when the repository has an established scope convention, or when
  the user asks for one.

Use the Jira key as scope when the current branch (`git branch --show-current`)
matches `feature/[JIRA-KEY]` or `feature/[JIRA-KEY]-*`. A Jira key is an
uppercase alphabetic prefix, a hyphen, and digits (for example `PROJ-123`).
Only the `feature/` prefix triggers scope extraction.

```text
feature/PROJ-123       -> feat(PROJ-123): add passkey login
feature/PROJ-123-login -> feat(PROJ-123): add passkey login
feature/auth           -> feat: add passkey login
fix/BUG-42             -> fix: handle expired sessions  (no scope)
main, develop          -> no scope implied
```

## Subject, Body, and Breaking Changes

- Subject: imperative (`add`, not `added`), lowercase except proper nouns,
  acronyms, issue IDs, and user-facing names, no trailing period, under 72
  characters.
- Body: omit unless the user asks for one. When present, explain what and why
  without repeating the header.
- Breaking changes: in a new message, use both `!` in the header and a
  `BREAKING CHANGE:` footer that explains the migration impact.

## Language

Detect the dominant language from the latest 10 non-merge commit subjects:

```bash
git log --no-merges -10 --pretty=%s
```

Use the dominant language when clear. Use English when the repository has fewer
than 3 non-merge commits or no language is dominant. Use the same language in
the subject, body, and footer values. Keep type, scope, and footer keys
unchanged.

## Pull Request Titles

A pull request title uses the commit header format.

1. Read the complete pull request diff as the hosting platform computes it, for
   example `git diff <base>...HEAD`. Do not derive the title from only the
   latest commit.
2. Confirm the diff has one cohesive semantic intent. Supporting tests, docs,
   generated files, and dependency updates can belong to that intent. If the
   branch contains independent changes that one title cannot describe
   truthfully, explain the mismatch and ask whether to split before you create
   the pull request.
3. Choose the header with the commit rules. For a draft pull request, describe
   the intended completed change; do not use `wip` unless the user asks.
4. When creating, pass the title explicitly to the creation tool instead of
   relying on autofill from a branch name or commit.

- Do not append a number such as `(#123)`; the platform can add it to the merge
  commit.
- The pull request description is not a commit body. Follow the repository's
  template and summarize the change, motivation, and validation.
- Creating a pull request does not authorize rewriting, squashing, or amending
  commits. On an existing pull request, change the title only when the user
  asks.

## Review

When asked to review a commit message or a PR title, check the format, check
that the type matches the diff (a `docs` commit has no logic changes), and
require at least one breaking-change marker for a breaking change. If both
markers are present, confirm they describe the same change. State whether the
message is valid, then list specific fixes.

## Commit Workflow

A request to commit authorizes staging and committing the changes within the
scope the user named.

1. Run `git status`. Stop and tell the user when there is a conflict, an
   in-progress merge, rebase, or cherry-pick, or no changes.
2. Determine the candidate changes. Honor an explicit scope such as "staged
   changes only", named paths, or a named feature. Otherwise, consider all
   staged, unstaged, and untracked changes.
3. Read the complete candidate changes: staged and unstaged diffs and relevant
   untracked files. Stats, name-status output, and file lists are not
   substitutes.
4. Partition the changes into commit units by purpose and semantic domain. A
   domain is a coherent product capability or component, not a file or
   directory:
   - Files belong together when they implement one purpose in one domain,
     including its tests, docs, migrations, generated files, and dependency or
     lockfile updates.
   - Separate changes to different domains, and changes that can be understood,
     reverted, or reviewed independently, such as unrelated behavior,
     formatting, or maintenance.
   - One file can contain several units. Use hunk-level staging to split it.
5. Choose the path:
   - **One unit**: stage all of it and continue without asking.
   - **Several units**: present an ordered plan with the message and the files
     or hunks of each commit. Ask once, and wait for the answer before you
     change the index or commit.
   - **Ambiguous boundary**: ask only the smallest question that the content
     cannot answer.
6. For each authorized unit, stage only that unit, read the full
   `git diff --staged`, and verify that it contains the complete unit and
   nothing from another unit.
7. Write the message from the staged diff, validate it against these rules, and
   commit with `git commit -m`.
8. After all commits, run `git status` and report the commits and any remaining
   changes.

## Common Mistakes

- Asking for file-by-file confirmation of one cohesive change.
- Treating the current staging state as a commit boundary. Staged versus
  unstaged is not a semantic difference.
- Deciding to split from the number of files or directories instead of from
  purpose and domain.
- Grouping unrelated hunks because they are in the same file.
