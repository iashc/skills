# Rules for simplified technical English

The sections follow Part 1 of ASD-STE100 (Simplified Technical English), adapted for software
documents. The wording and the examples are ours. A project glossary replaces the STE dictionary
(section 10).

`references/rules-zh.md` uses the same numbers. A number means the same topic in both languages;
the details change with the language. Rules 2.3, 3.5, 4.6 and 9.7 are different in each language
or exist in only one.

## Layers

Each rule belongs to one layer. `SKILL.md` says which layers apply in which tier.

- **core**: Applies in every tier. Obey it.
- **convention**: A default for when the project has no convention of its own. A project
  convention replaces it. It applies in the strict tier, and in the default tier only when the
  project or the user asks for it.
- **strict**: Applies only in the strict tier.

The guardrails in `SKILL.md` ("Do not overdo it") apply always and win over every rule here.

Each rule gives a reason, an example and a check. The check says if `scripts/check.py` reports
the rule and at which level. All examples are invented.

## Contents

1. Words: 1.1–1.5
2. Noun phrases: 2.1–2.3
3. Verbs: 3.1–3.5
4. Sentences: 4.1–4.6
5. Procedures: 5.1–5.5
6. Descriptive text: 6.1–6.5
7. Warnings: 7.1–7.4
8. Punctuation, numbers and length: 8.1–8.9
9. Writing practices: 9.1–9.7
10. The glossary

## 1 Words

1.1 **One concept, one word.** (core)
Use the same word for the same thing or action in the whole document. Do not change words for
variety.
Why: Two words make the reader look for two things.
Example: "Create an API key. Store the token in the vault. The credential expires after 90 days."
→ "Create an API key. Store the API key in the vault. The API key expires after 90 days."
Check: Find each project concept and read every place where it occurs.

1.2 **One word, one meaning.** (core)
After a word has a meaning in the document or the glossary, do not use it for something else.
Why: The reader applies the first meaning everywhere.
Example: If "job" means a scheduled task, do not call one run of that task a "job". Call it a
"run".
Check: Compare each use with the glossary entry.

1.3 **Use the glossary words.** (core)
Use the project glossary for project concepts. Add a new concept to the glossary before you use
it. Section 10 says how to find or start a glossary.
Why: Without a shared list, each writer invents a name.
Check: Each project term in the document is in the glossary.

1.4 **No vague words.** (core)
Do not use `appropriate`, `relevant`, `various`, `significant`, `substantial`, `a number of`,
`reasonable` or `numerous`. Write a number, a name or a condition.
Hedges such as `fairly`, `somewhat`, `quite`, `basically` and `essentially` are also vague, but
they limit a claim. Replace a hedge with the number when the document gives one. Otherwise keep
it: "basically done" and "done" are different claims.
Why: A vague word looks like information but gives none. The reader needs "how many" and "which".
Example: "Set an appropriate timeout." → "Set the timeout to 30 seconds."
Example: "The new index makes queries significantly faster." → "With the new index, the median
query time went from 800 ms to 90 ms (staging, 2026-05-14)."
When you rewrite and do not know the number, remove only the empty word and keep the claim at its
strength: "makes queries significantly faster" → "makes queries faster". Tell the author which
claims have no data. Do not invent a number.
Exception: "significant" in a statistics sense. Add it to `allow` in `.ste.json`.
Check: `check.py` reports the vague words as **hard** and the hedges as **soft**.

1.5 **Verbs that say what happens.** (strict)
`handle`, `process`, `manage`, `optimize` and `deal with` only say that something happens.
Write the action.
Why: The reader cannot reproduce or test "handles errors".
Example: "The client handles rate limits." → "When the server returns 429, the client waits for
the time in `Retry-After` and sends the request again."
Exception: A general verb is correct when the details follow at once: "The parser supports three
formats: YAML, TOML and JSON."
Check: `check.py --strict` reports it as **soft**.

## 2 Noun phrases

2.1 **At most two modifiers before a noun.** (convention)
Move the other modifiers after the noun, or write a second sentence.
Why: The reader must keep all modifiers in memory before the noun arrives.
Example: "the nightly incremental compressed encrypted backup file" → "the nightly backup file.
The file is incremental, compressed and encrypted."
Check: Read each long noun phrase. For Chinese, `check.py` counts the character `的`.

2.2 **At most three nouns in a row.** (convention)
Break a longer group with a verb or a preposition.
Why: In "build cache key collision bug", the reader cannot see what modifies what.
Example: "build cache key collision bug" → "a bug where two builds get the same cache key".
Exception: A glossary term counts as one word.
Check: Read each noun group.

2.3 **Hyphenate a compound modifier before a noun.** (strict)
Write "a write-ahead log", "a two-phase commit", "a 32-bit integer". After the noun, do not
hyphenate: "the log is write ahead".
Check: Read each compound modifier.

## 3 Verbs

3.1 **Do not hide the verb in a noun.** (core)
Do not use `perform`, `carry out` or `conduct`, or "make", "give" with a noun that has a verb
inside it. Use that verb.
Why: The wrapper verb adds words and buries the action.
Example: "The script performs a cleanup of old images." → "The script deletes old images."
Example: "The team made a decision to drop Python 3.7." → "The team dropped Python 3.7."
Check: `check.py` reports it as **hard**.

3.2 **Active voice; name the actor.** (strict)
Put the component or person that acts first.
Why: The actor tells the reader where to look.
Example: "Expired sessions are removed every hour." The code shows that `SessionSweeper` does
it. → "`SessionSweeper` removes expired sessions every hour."
Exception: Use the passive when the actor is unknown or does not matter: "The file was
truncated." Do not guess an actor to make a sentence active (4.2). In a procedure, the imperative
replaces both (5.2).
Check: `check.py --strict` reports it as **soft**. It does not report adjectives such as
"based", "located" or "related".

3.3 **Simple tenses for facts.** (strict)
Use the simple present for how a system works, the simple past for events and "will" for plans.
Why: "is retrying" describes a moment, not the behavior.
Example: "The agent is collecting metrics every 10 seconds." → "The agent collects metrics every
10 seconds."
Check: `check.py --strict` reports it as **soft**.

3.4 **One set of requirement words in the whole document.** (core)
The default set is:

| Word                | Meaning                      |
| ------------------- | ---------------------------- |
| must / must not     | a requirement                |
| should / should not | a recommendation             |
| can / cannot        | a permission or a capability |
| need not            | not required                 |

If the project or the user uses another set, such as RFC 2119 keywords (`MUST`, `SHOULD`, `MAY`),
use that set. Do not mix sets: "must" in one place and "make sure" or "ideally" in another tells
the reader that the strengths differ.
Why: The reader decides which instructions are optional from these words.
Example: "You must pin the version. Ideally, run the tests first. Make sure to tag the release."
→ "You must pin the version. You should run the tests first. You must tag the release."
Exception: Steps and warnings use the imperative (5.2, 7.2). "Need" as an ordinary verb is correct:
"The worker needs a token before it connects."
Check: `check.py` reports words from a second set as **hard**. Set the project choice with
`requirementWords` in `.ste.json`.

3.5 **One-word verbs.** (strict; English only)
Prefer "find" to "find out", "start" to "start up", "remove" to "get rid of". Keep a phrasal verb
that is a standard term: "log in", "roll back", "set up".
Check: Read each phrasal verb.

## 4 Sentences

4.1 **One topic in each sentence.** (core)
When a new topic starts, start a new sentence.
Why: The reader must split a long sentence and often loses its last part.
Example: "The importer reads the CSV file and validates each row, skips rows with errors and
writes them to a report, and then commits the rest in batches of 500." → "The importer reads the
CSV file and validates each row. It skips each row that has an error and writes the row to a
report. Then it commits the other rows in batches of 500."
Check: For each sentence, say its topic in a few words. If you cannot, split the sentence.

4.2 **Name the actor.** (core)
Do not start with an empty "It is …" or "There is …" when a real subject exists. Do not use a
modifier without an actor: in "After deploying, the cache is cleared", who deploys?
Why: Software text often must say if a person or a program acts.
Take the actor from the document or the code. If neither names the actor, do not guess one. Keep
the original form, and list the question for the author.
Example: "It is necessary to rotate the keys yearly." → "Rotate the keys every year."
Example: "After merging, the docs are rebuilt." The document says that a maintainer merges pull
requests and that the CI workflow builds the docs. → "After a maintainer merges a pull request, CI
rebuilds the docs."
Example: "Stale entries are purged nightly." Nothing in the document or the code says which
component purges them. → Keep the sentence. Report: "Who purges stale entries?"
Check: `check.py` reports some empty subjects as **soft**. For every verb, find the actor in the
document or the code, or list it as a question.

4.3 **Each pronoun points to one thing.** (core)
Use "it", "this", "they" and "which" only when one noun before them fits. Write "this setting",
not "this".
Why: A wrong reference gives a wrong meaning, and the reader does not notice.
Example: "The proxy forwards the request to the worker, and then it logs the result." → "The
proxy forwards the request to the worker. Then the worker logs the result."
Check: `check.py` reports a bare "This" as **soft**. Read each pronoun.

4.4 **Show how sentences connect.** (strict)
Use "because", "so", "if" and "but" for cause, condition and contrast.
Example: "The queue holds 10,000 messages. Producers block." → "When the queue holds 10,000
messages, producers block."
Check: Read each pair of sentences.

4.5 **A vertical list for three or more items.** (strict)
Check: A sentence with three or more items that each have their own detail.

4.6 **Do not drop small words.** (strict; English only)
Keep "the", "a" and "that" where the sentence needs them.
Example: "Run script after updating config." → "Run the script after you update the
configuration."
Check: Read each short sentence.

## 5 Procedures

5.1 **A numbered list with one instruction in each step.** (core)
Put two actions in one step only when the reader does them together.
Why: The reader comes back to the list after each step. A second instruction in the step is easy
to skip.
Check: Count the verbs in each step.

5.2 **Start each step with an imperative verb.** (core)
Write "Open …", "Run …". Do not write "You should run …" or "The operator runs …".
Why: The verb tells the reader what to do before anything else.
Check: `check.py` reports some cases as **soft**. Read the first word of each step.

5.3 **The condition comes before the instruction.** (core)
Write "If the health check fails, roll back." Do not write "Roll back if the health check fails."
Why: A reader who reads the instruction first can act before reading the condition.
Check: `check.py` reports a trailing "if" or "unless" in a step as **soft**.

5.4 **At most 20 words in a step sentence.** (convention)
Section 8.8 says how to count.
Check: `check.py --strict` reports it.

5.5 **Keep reasons and results out of the instruction.** (strict)
Put the reason before the list. Put the result after its step, in its own sentence.
Check: Read each step.

Example for this section:

Original: "Before you upgrade, it's a good idea to export the data, and then stop the scheduler;
the new version can be installed after that, and then the schema update should be run, rolling
back with the export if it errors out."

Rewrite:

**Warning:** Export the data before you upgrade. Without the export, a failed schema update
cannot be undone.

1. Export the data: `appctl export > backup.json`.
2. Stop the scheduler: `appctl scheduler stop`.
3. Install the new version.
4. Run the schema update: `appctl schema update`.
   Result: The output ends with `schema up to date`.
5. If the schema update fails, import the export: `appctl import < backup.json`.
6. Start the scheduler: `appctl scheduler start`.

## 6 Descriptive text

6.1 **The conclusion comes first.** (core)
The first sentence of a paragraph gives the conclusion. Reasons, data and exceptions follow.
Why: Many readers read only the first sentence of each paragraph.
Example: "**A slow consumer does not block other consumers.** Each consumer has its own buffer,
and the broker drops a consumer that is 60 seconds behind."
Check: Read only the first sentences. They must give the message of the section.

6.2 **One topic in each paragraph, at most six sentences.** (strict)
Check: Count the sentences.

6.3 **At most 25 words in a descriptive sentence.** (convention)
Table cells are exempt.
Check: `check.py --strict` reports it.

6.4 **Every measured number has its conditions.** (core)
Say what was measured, under which load, on which machine, and when. Do not write a number that
nobody measured. When you rewrite a number and do not know its conditions, keep the number as it
is and list it for the author. Do not add a placeholder in the text.
Why: The reader cannot reproduce or date a number without its conditions.
Example: "Cold start takes 1.2 s." → "Cold start takes 1.2 s (M2 laptop, empty cache,
2026-04-02)."
Check: Read each number. `check.py --compare` reports numbers that a rewrite lost or added.

6.5 **Keep done apart from planned.** (core)
Give a date or "done" for finished work. Use "will", or a "Roadmap" section, for plans.
Why: A reader who takes a plan for a fact tries to use a feature that does not exist.
Example: "The service supports multi-region failover (Q3)." → "Multi-region failover is planned
for Q3."
When the original marks only part of a sentence as planned, split the sentence. The marker belongs
to the item that it follows. The split uses the author's own marker, so it is not an audit.
Example: "The exporter already supports CSV and Parquet output (planned for 2027 Q1)." → "The
exporter supports CSV output. Parquet output is planned for 2027 Q1."
If you cannot tell which part the marker applies to, keep the sentence and ask the author.
Check: Read each statement about features. Ask: is this done?

## 7 Warnings

A warning is for an operation that can do damage: data loss, an irreversible change, a wrong
result without an error, slower performance that nobody notices, production impact, or text that
goes outside the team.

7.1 **The warning comes before the step it applies to.** (core)
Why: A warning after the step comes too late.
Check: For each warning, find its step. The warning must be above it.

7.2 **The instruction first, then the risk.** (core)
The first sentence says what to do or not to do. The next sentence says what happens if the
reader does not obey. Give numbers when you have them.
Why: A reader who reads one sentence must get the instruction, not the background.
Example: "Because `DROP SCHEMA ... CASCADE` deletes every dependent table without asking, which
could cause data loss, it is recommended to avoid it." → "**Warning:** Do not run `DROP SCHEMA
... CASCADE` on a shared database. It deletes every dependent table without a prompt."
Check: Read the first sentence of each warning.

7.3 **One risk in each warning.** (strict)
Write two warnings for two risks.

7.4 **Two levels: Warning and Caution.** (core)
**Warning:** data loss, an irreversible change, a wrong result without an error, production
impact, text that goes outside the team.
**Caution:** slower operation, work to do again, a long wait.
Start each one with "**Warning:**" or "**Caution:**" in its own paragraph. If the project uses
other labels or admonitions (`> [!WARNING]`), use those.
Check: `check.py --compare` counts the labels before and after a rewrite.

## 8 Punctuation, numbers and length

All rules in this section are conventions. A project style guide replaces them.

8.1 **ASCII punctuation in English text.** (convention)
Check: `check.py` reports full-width punctuation in an English line.

8.2 **One quotation style in a document.** (convention)
If the project has no rule, keep the style that the document uses most.
Check: `check.py` counts quotation marks in body text. It ignores code, HTML attributes and JSON.
Set the style with `quotes` in `.ste.json`.

8.3 **A space between a number and its unit.** (convention)
Write "40 ms", "2 GB". Do not put a space before "%".
Check: `check.py` reports common units.

8.4 **Numerals for counts and measurements.** (convention)
Write "3 retries", "step 4". Write the word when it is not a count: "one of the replicas".

8.5 **Unit symbols with numbers.** (convention)
Write "40 ms", "500 req/s". Without a number, write the word: "milliseconds".

8.6 **Ranges with an en dash or "to".** (convention)
Write "5–10 seconds" or "5 to 10 seconds", not `5~10`.
Check: `check.py` reports "~" between numbers.

8.7 **Dates that cannot be misread.** (convention)
Use ISO dates (2026-03-02) in tables and parentheses, and "March 2, 2026" in text. Do not write
"03/02/2026".
Check: `check.py` reports the slash form.

8.8 **How to count length.** (convention)
A word is a group of characters between spaces. A code span and a number with its unit each count
as one word. A sentence ends at ".", "?", "!" or ";". The limits are in 5.4 and 6.3.

8.9 **Clear lists and no "and/or".** (convention)
End list items that are full sentences with a period. Instead of "and/or", say which one.

## 9 Writing practices

9.1 **One spelling and case for each term.** (strict; 1.1 covers it in the default tier)
Write "log in" (verb) and "login" (noun) the same way in the whole document.

9.2 **Code names in backticks, exactly as in the code.** (strict)
Files, functions, types, commands, flags, environment variables: `loadConfig`, `--dry-run`,
`NODE_ENV`.

9.3 **Official names; define abbreviations at first use.** (strict)
Write PostgreSQL, GitHub, macOS. Write "Content Security Policy (CSP)" the first time.

9.4 **No idioms, filler or marketing words for facts.** (convention)
Do not write `seamless`, `leverage`, `out of the box`, `under the hood`, `robust`, `powerful`,
`simply`, `just`, `easily` or `obviously`. Say what happens and how much.
Why: These words give no information. "Simply" and "just" also tell a reader with a problem that
the problem is their fault.
Check: `check.py` reports them.

9.5 **"You" for the reader, "we" for project decisions.** (strict)

9.6 **References that the reader can find.** (strict)
Give the file and line, or the file and section: "`router.go`, line 88".

9.7 **No contractions or Latin abbreviations.** (convention; English only)
Write "do not", "it is", "for example", "that is", "and so on", "through".
Why: They are harder for readers whose first language is not English, and for translation tools.
Check: `check.py` reports them.

## 10 The glossary

The glossary is the source for 1.1–1.3 and 9.1. Before you write, look for one:

- files with "glossary", "terms" or "terminology" in the name;
- a terms section in `STYLE.md`, `CONTRIBUTING.md` or a writing guide;
- naming rules in `AGENTS.md`, `CLAUDE.md` or the README.

If you find one, use it. When it conflicts with these rules, the project wins.

If there is none:

1. Before you write, list the project concepts in the text, from the code and the documents.
2. Choose one word for each concept. Prefer the name in the code, then the most frequent word.
3. After you write, give the list to the author:

| Term    | Meaning                                    | Do not use               |
| ------- | ------------------------------------------ | ------------------------ |
| release | a tagged version published to the registry | deploy (for this)        |
| deploy  | putting a release on the servers           | release, ship (for this) |
