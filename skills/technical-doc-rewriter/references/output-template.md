# Output templates

Write the report in the language of the user's request. Use the smallest form that answers it.

## Rewrite

Write the rewritten document in place only when the user named that file and the file is under
version control. Otherwise write a new file next to it, for example `runbook.simplified.md`. Then
report:

```markdown
## Changes

- Tier: default | strict. Project conventions used: <glossary, style guide, .ste.json, or none>.
- Rules applied: 1.4 ×4, 3.1 ×2, 5.3 ×3, 7.1 ×1 <!-- counts by rule, not a diff -->
- check.py: 0 hard, <n> convention, <n> soft. <Why each remaining item stays.>
- check.py --compare: nothing lost, no new numbers. <Or list each item and why.>

## For the author

- Claims without data: <claim> (<where>). Kept as written. Add the number and its conditions.
- Numbers without conditions: <number> (<where>).
- Actors not named: <action> (<where>). Kept as written; say who does it.
- Gaps in the content: <a missing rollback, risk or condition that the rules do not fix>.
```

Leave out "For the author" when nothing is open.

## Review only

Do not change the file. List core-rule findings first. Quote the original exactly and give a
rewrite that the author can paste.

```markdown
| Line | Rule      | Original                       | Suggested                      |
| ---- | --------- | ------------------------------ | ------------------------------ |
| 12   | 3.1 core  | The script performs a cleanup. | The script deletes old images. |
| 30   | 1.4 core  | 查询显著加快                   | 查询加快（缺数据，已列给作者） |
| 41   | 8.3 conv. | 第3步                          | 第 3 步                        |
```

End with one line: the number of core and convention findings, and the glossary that you used (or
that you found none).

## Out of scope

When the request is outside this skill (see "Scope" in `SKILL.md`), say so in one sentence and
say what you did instead, for example "I only fixed the Markdown layout; the wording is
unchanged."
