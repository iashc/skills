---
name: technical-doc-rewriter
description: >-
  Rewrites technical documents so that they are clear and have one meaning,
  or reviews their wording, in English or Chinese, with rules based on
  ASD-STE100. It changes only the wording and keeps every fact. Use when the
  user asks to rewrite, polish, simplify, or clean up a README, design doc,
  runbook, API doc, guide, or similar technical text, or says that it is hard
  to read, wordy, or unclear: for example "改写这份文档", "润色一下 README",
  "这段写得太绕", "去掉翻译腔", "写得清楚简洁点", "检查一下措辞",
  "make this README clearer", or "clean up the wording". Do not use to review
  a design's content, check facts, polish marketing copy or social posts,
  translate, or change text that the user did not ask to rewrite.
license: MIT
metadata:
  author: Ash Li
  version: '2026-10-28'
---

# Technical Doc Rewriter

Make a technical document mean one thing to every reader: one word for one concept, one topic in
one sentence, a named actor for each action, and one set of requirement words. The rules follow
Part 1 of ASD-STE100 and add the typical faults of Chinese technical text: hidden verbs (`进行`),
long modifiers before a noun, missing subjects and unclear pronouns.

English and Chinese share one rule numbering. `references/rules-en.md` and
`references/rules-zh.md` give each rule with its reason, an example and a check. Open the file of
the document's language when a rule is unclear or when you need an example.

## Scope

Use this skill for text that a reader uses to understand a system, do an operation or make a
technical decision: READMEs, design documents, API references, runbooks, troubleshooting and
migration guides. Use it for commit messages, pull request descriptions, code comments and error
messages only when the user asks for this rewrite.

Do not use it for marketing copy, posts, announcements, speeches or fiction. These rules make such
text flat. If the user insists, apply the rules and say once that the text loses its tone. In a
mixed document such as release notes, apply the rules to the technical parts only.

Boundaries:

- **The content is out of date.** Point out the stale parts. Rewrite only the wording of what is
  there.
- **Only the layout is wrong.** Fix the layout only.
- **The user wants a fact check or a design review.** Say that this skill checks wording only. It
  does not compare claims with the code or judge the design.
- **Translation.** If the user wants a translation too, translate first, then apply the rules of
  the target language.

Use the rules of each part's own language; the document decides, not the conversation. A Chinese
line with English terms uses the Chinese rules.

## Tiers and precedence

- **Default tier.** Apply the core layer and the guardrails. Keep the document's own punctuation,
  spacing, quotation and date style. If the document mixes styles, use the one it uses most.
- **Strict tier.** Use it only when the user asks for "strict STE", "按 ASD-STE100" or the like.
  Apply every rule, including the convention layer and the sentence length limits.

The guardrails win over everything. Project conventions (a glossary, a style guide, `.ste.json`,
`AGENTS.md`) win over every rule in this skill.

## Guardrails (always)

- **Change the wording, not the content.** Keep every fact, condition, exception, risk and doubt.
  Do not drop a caveat to make a sentence shorter.
- **Keep the strength of each claim.** Remove an empty intensifier (`显著`, `significantly`).
  Keep a hedge that limits a claim (`较`, `约`, `基本上`, `可能`, `about`, `may`) unless the
  document gives the number. List missing evidence for the author, not in the text.
- **Do not invent facts.** Do not add a number, an actor, a date or a condition that the original
  or the code does not give. Write "[TBD: …]" / "[待补：……]" in the text only when the reader
  cannot do the task without the fact.
- **Keep what must stay.** Code, commands, command output, quotations, proper names and the user's
  own words stay exactly as they are.
- **Keep the structure.** Reorder sentences, but keep sections, headings and links unless the user
  asks for more.

## Core layer (every tier)

- 1.1 One concept, one word. Do not change words for variety.
- 1.2 One word, one meaning.
- 1.3 Use the glossary words. Name a new concept before you use it (rules file, section 10).
- 1.4 No vague words (`appropriate`, `various`, `significant`; `适当`, `相关`, `显著`). Write a
  number, a name or a condition. If you do not know the number, remove only the empty word.
- 3.1 No hidden verbs (`perform`, `carry out`; `进行`, `加以`, `予以`). Use the verb itself.
- 3.4 One set of requirement words in the whole document. Default: `must` / `should` / `can`, or
  `应` / `宜` / `可`. If the project or the user uses another set (RFC 2119, or `必须` / `建议`),
  use that set.
- 4.1 One topic in each sentence.
- 4.2 Name the actor, and write the subject when it changes. Take the actor from the document or
  the code. If neither names it, keep the original form and ask the author.
- 4.3 Each pronoun points to one thing.
- 5.1 Procedures are numbered lists with one instruction in each step.
- 5.2 Each step starts with an imperative verb.
- 5.3 The condition comes before the instruction.
- 6.1 The conclusion comes first in each paragraph.
- 6.4 Every measured number keeps its conditions.
- 6.5 Keep what is done apart from what is planned. When the original marks part of a sentence
  as planned (a date, a quarter, "planned", `预计`), split that part into its own sentence. The
  marker belongs to the item that it follows. If that is unclear, keep the sentence and ask.
- 7.1 A warning comes before the step it applies to.
- 7.2 A warning gives the instruction first, then the risk.
- 7.4 Two levels: Warning / 警告 (data loss, irreversible, silent wrong result, production
  impact, external publication) and Caution / 注意 (slow, rework, long wait).

## Convention layer (strict tier, or when the project asks)

- 8.1–8.9 ASCII punctuation in English and full-width punctuation in Chinese, one quotation style,
  a space between Chinese and Latin text and between a number and its unit, `5–10` (not `5~10`),
  ISO dates.
- 2.1 At most two modifiers (two `的`) before a noun. 2.2 At most three nouns in a row.
- 5.4 Step sentences: at most 20 words or 40 characters. 6.3 Descriptive sentences: at most 25
  words or 50 characters.
- 9.4 No filler or marketing words (`seamless`, `simply`; `开箱即用`, `赋能`).
- 9.7 English only: no contractions, no `e.g.`, `i.e.`, `etc.` or `via`.

## Strict-only rules

- 1.5 Verbs say what happens (not `handle`, `处理`). 2.3 Hyphens (EN) / 的地得 (ZH).
- 3.2 Active voice, with the limit of 4.2. 3.3 Simple tenses; no `正在`. 3.5 One-word verbs (EN).
- 4.4 Show cause and contrast. 4.5 Lists for three or more items. 4.6 Keep articles (EN).
- 5.5 Reasons before the steps, results after them. 6.2 One topic, at most six sentences in a
  paragraph. 7.3 One risk in each warning.
- 9.1 One form for each term. 9.2 Code names in backticks. 9.3 Official names; define
  abbreviations. 9.5 "You" and "we". 9.6 References the reader can find.

## Workflow

1. **Check the scope and the tier** (see above).
2. **Find the project conventions.** Look for a glossary, a style guide and `.ste.json` (rules
   file, section 10). Note the requirement words and the quotation style that the project uses.
3. **Rewrite.** Apply the layers of the tier. If you edit the file in place, keep a copy of the
   original for step 6.
4. **Run the check.** `python3 <skill dir>/scripts/check.py <file>`. Add `--strict` in the strict
   tier, and `--lang en` or `--lang zh` to force a language.
5. **Fix and run again** until the check reports 0 `hard`. Read each `convention` and `soft`
   finding, and keep it when you have a reason. A `hard` finding can stay only for a technical
   term or a project requirement: mark the line with `<!-- ste-ignore 1.4 -->` and say why in the
   report.
6. **Compare the facts.** `python3 <skill dir>/scripts/check.py --compare <original> <rewritten>`
   lists the numbers, code, code blocks, URLs and warning labels that the rewrite lost or added.
   Restore each lost item. Remove each added number unless the user gave it to you. Read each
   `changed` number. Run it again until nothing is lost and no number is new.
7. **Deliver.** Follow `references/output-template.md`.

For a review without a rewrite, do steps 1, 2 and 4 on the original, then use the review
template. If Python 3.8 or later is not available, do the checks by reading, and say so in the
report.

## `.ste.json`

The check script reads `.ste.json` from the document's directory, then from the repository root.
Write this file only when the user asks you to record a convention.

```json
{
  "allow": ["significant", "显著"],
  "quotes": { "zh": "curly", "en": "straight" },
  "cjkLatinSpace": true,
  "requirementWords": { "zh": "gbt", "en": "must" }
}
```

`gbt` is `应` / `宜` / `可`, `bixu` is `必须` / `建议`, `must` is `must` / `should` / `can`, and
`rfc2119` is `MUST` / `SHOULD` / `MAY`.

## Common mistakes

- Applying the rules to marketing text, or to a commit message that nobody asked you to rewrite.
- Deleting a hedge to clear a finding: "延迟较高" → "延迟高" makes the claim stronger.
- Making a passive sentence active with a guessed actor.
- Replacing a correct technical term to obey 1.4 or 9.4.
- Changing the punctuation or spacing in the default tier when the project has no rule for it.
- Treating every `convention` or `soft` finding as a defect.
