# Evals for technical-doc-rewriter

These files test the `technical-doc-rewriter` skill. They live outside the skill directory, so
`vpx skills add` does not install them.

## Files

- `fixtures/`: Three documents with planted faults.
  - `runbook-zh.md`: A Chinese runbook with commands, a warning after its step, and rollback steps.
  - `readme-en.md`: An English README with install, configuration and upgrade steps.
  - `design-zh.md`: A Chinese design document with performance numbers and a planned item written
    as done.
- `cases.json`: The assertions for each fixture, in addition to the common ones below.
- `trigger-cases.json`: Requests that should and should not activate the skill.
- `grade.py`: Scores rewrites. Standard library only.
- `results/<date>.md`: The result of one comparison run. `results/<date>/<run>/` holds the rewrites.

## Assertions

For each rewrite of each fixture:

1. `check.py` reports 0 hard findings.
2. `check.py --compare <fixture> <rewrite>` reports nothing lost and no new number.
3. Each warning in `cases.json` comes before the step that it applies to, and no copy of it
   follows the step.
4. Each planned item in `cases.json` is written as planned, not as done.

## Run

1. Rewrite each fixture into one directory per run, with the fixture's file name.
2. Score all runs:

   ```sh
   python3 evals/technical-doc-rewriter/grade.py <run dir>...
   ```

   The script prints one Markdown table row for each run and fixture. Exit status 1 means that an
   assertion failed.

The trigger cases are not scored by a script. Check them by hand against the `description` in
`SKILL.md`.
