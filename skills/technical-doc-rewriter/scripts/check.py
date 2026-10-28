#!/usr/bin/env python3
"""Check a technical document against the simplified technical writing rules.

Usage:
  check.py [--lang auto|en|zh] [--strict] FILE...      (FILE can be - for stdin)
  check.py --compare ORIGINAL REWRITTEN

Rule numbers refer to references/rules-en.md and references/rules-zh.md.

Each finding prints as `path:line: [rule level] message: text`. The levels are:
  hard        A core rule is broken. Exit status 1.
  convention  A convention default is not met. Exit status 1 only with --strict.
  soft        A place to read again. It never changes the exit status.
--strict also checks sentence length (5.4, 6.3) and the strict-only soft rules.

A line that has a Chinese character uses the Chinese rules, also when it has many
English words. A line that has Latin letters and no Chinese character uses the
English rules. The script does not check front matter, fenced code, inline code,
URLs, HTML tags and comments. Text in quotation marks is a mention, not a use, so
the wording rules do not check it.

To skip a line, put `<!-- ste-ignore -->` on it. To skip only some rules, write
`<!-- ste-ignore 1.4 3.1 -->`. A comment on a line of its own applies to the next line.

Configuration: the script reads `.ste.json` from the directory of the document. If
that file does not exist, it reads `.ste.json` from the repository root. Keys:
  "allow":            words and phrases that the wording rules accept, for example
                      ["significant", "显著"] in a statistics document.
  "quotes":           "straight", "curly" or "corner", or {"zh": ..., "en": ...}.
  "cjkLatinSpace":    true (default) or false: a space between Chinese and Latin text.
  "requirementWords": {"zh": "gbt" | "bixu", "en": "must" | "rfc2119"}.
                      gbt is 应/宜/可, bixu is 必须/建议, must is must/should/can.
Without "requirementWords", the script reports requirement words only when a
document uses more than one set.

--compare lists the numbers (with units), inline code, code blocks, URLs and
warning labels that the rewrite lost or added. An item counts once, however often
it occurs. A new number can be an invented one, so the script marks it. A number
that only gained or lost its unit ("4-core" -> "4 cores") is listed as changed.
Exit status 1 when an item or a warning label is lost, or when a number or a URL
is added.

Exit status 2: a usage error, a file that cannot be read, or a bad configuration.
Standard library only; Python 3.8 or later.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, namedtuple

Finding = namedtuple('Finding', 'line rule level message text')
Rule = namedtuple('Rule', 'rule level message pattern flags strict skip')

HARD, CONVENTION, SOFT = 'hard', 'convention', 'soft'
HAN = re.compile('[㐀-䶿一-鿿]')
H = '[㐀-䶿一-鿿]'
FULL_WIDTH = re.compile('[　-〿＀-￯]')
PH = ''  # Stands in for inline code and URLs. It is not Chinese, Latin or punctuation.
I = re.IGNORECASE


class UsageError(Exception):
    """A bad argument, file or configuration. Exit status 2."""


def rule(rule_id, level, message, pattern, flags=0, strict=False, skip=None):
    return Rule(rule_id, level, message, re.compile(pattern, flags), flags, strict, skip)


def _names_what_it_relates_to(text, m):
    # "与 X 相关" names X, so it is not vague. A bare "相关文档" is.
    if m.group(0) != '相关':
        return False
    clause = re.split(r'[，。；：、？！,;:?!]', text[: m.start()])[-1]
    return re.search(r'[与和跟同]', clause) is not None


def _code_of_conduct(text, m):
    return m.group(0).lower().startswith('conduct') and text[: m.start()].lower().endswith('of ')


ADJECTIVAL = {
    'based', 'interested', 'located', 'related', 'unrelated', 'concerned', 'involved',
    'limited', 'detailed', 'advanced', 'experienced', 'complicated', 'dedicated',
    'supposed', 'deprecated', 'pleased', 'surprised', 'tired', 'excited',
}  # fmt: skip


def _adjectival(text, m):
    return m.group(1).lower() in ADJECTIVAL


NOT_PROGRESSIVE = {
    'thing', 'nothing', 'something', 'anything', 'everything', 'string', 'missing',
    'pending', 'ongoing', 'existing', 'following', 'remaining', 'outgoing', 'incoming',
    'interesting', 'misleading', 'confusing', 'boring',
}  # fmt: skip


def _not_progressive(text, m):
    return m.group(1).lower() in NOT_PROGRESSIVE


WHETHER_VERBS = {'check', 'see', 'verify', 'determine', 'test', 'ask', 'know', 'decide', 'confirm'}


def _not_a_trailing_condition(text, m):
    if text[: m.start()].rstrip().endswith(('.', '!', '?', ':', ';')):
        return True  # The condition starts its own sentence.
    before = re.findall(r'[A-Za-z]+', text[: m.start()])
    return not before or before[-1].lower() in WHETHER_VERBS or before[-1].lower() == 'even'


PASSIVE = (
    r'\b(?:is|are|was|were|be|been|being)\s+(?:\w+ly\s+)?'
    r'(\w+ed|built|done|made|sent|written|run|set|kept|held|found|given|taken|shown|known|'
    r'seen|thrown|chosen|broken|stored|hidden)\b'
)
DATE = r'(?<![\d/])\d{1,2}/\d{1,2}/\d{2,4}(?![\d/])'

ZH_WORDS = [
    rule('1.4', HARD, '含糊词：写成数字、名称或条件',
         r'适当|若干|显著(?!性)|大幅|明显|诸多|相关(?![性系])', skip=_names_what_it_relates_to),
    rule('1.4', SOFT, '限定词：有数字就写数字；没有就保留，不要删掉',
         r'一定程度上?|较为|基本上'),
    rule('3.1', HARD, '包装动词：把后面的名词改回动词',
         r'进行(?!中)|加以|予以|[做作]出(?!来)|实现了?对[^。；，,;]{1,20}?的'),
    rule('9.4', CONVENTION, '套话：写出具体做了什么',
         r'开箱即用|无缝|一劳永逸|飞跃|极致|赋能|抓手|全方位|强大的|轻松地?|只需'),
    rule('4.3', SOFT, '句首的“这”指哪个东西？写出名词', r'(?:^|(?<=[。！？；]))\s*这(?=[会将是使让能可])'),
    rule('1.5', SOFT, '空泛动词：写出具体动作', r'处理|优化|操作|调整', strict=True),
    rule('3.2', SOFT, '被动句：写出谁做', r'被(?!动)', strict=True),
    rule('3.3', SOFT, '陈述事实不用“正在”', r'正在', strict=True),
]  # fmt: skip
ZH_STEP = [
    rule('5.2', SOFT, '步骤以动词开头，不写“需要、可以”或主语',
         r'^(?:你|您|用户|我们)|^(?:需要|可以|应该|应当)'),
    rule('5.3', SOFT, '条件写在指令前面', r'[，,；;]\s*(?:如果|若|假如|一旦)|[（(](?:如果|若|假如)'),
]  # fmt: skip
ZH_PUNCT = [
    rule('8.1', CONVENTION, '中文旁用了半角标点', rf'{H}[,;:?!]|[,;:?!]{H}|{H}\(|\){H}|{H}\.(?=\s|$)'),
    rule('8.6', CONVENTION, '范围用“–”或“到”，不用“~”', r'\d\s*[~～]\s*\d'),
    rule('8.7', CONVENTION, '日期写成 2026-03-02，不写 03/02/2026', DATE),
]  # fmt: skip

EN_WORDS = [
    rule('1.4', HARD, 'vague word: give a number, a name or a condition',
         r'\b(?:appropriate(?:ly)?|relevant|various|significant(?:ly)?|substantial(?:ly)?|'
         r'a number of|reasonabl[ey]|numerous)\b', I),
    rule('1.4', SOFT, 'hedge: give the number if you have it; otherwise keep the hedge',
         r'\b(?:fairly|quite|somewhat|basically|essentially)\b', I),
    rule('3.1', HARD, 'hidden verb: use the verb that is inside the noun',
         r'\b(?:perform(?:s|ed|ing)?|carr(?:y|ies|ied|ying) out|conduct(?:s|ed|ing)?)\b|'
         r'\b(?:make|makes|made|making) (?:an?|the) \w+(?:ion|ment)\b|'
         r'\b(?:give|gives|gave|giving) an? \w+(?:ation|ption)\b',
         I, skip=_code_of_conduct),
    rule('9.4', CONVENTION, 'filler or marketing word: state the fact',
         r'\b(?:simply|just|easily|obviously|seamless(?:ly)?|leverag(?:e|es|ed|ing)|out of the box|'
         r'under the hood|robust|powerful|cutting-edge|best-in-class|blazing(?:ly)?)\b', I),
    rule('9.7', CONVENTION, 'Latin abbreviation: write "for example", "that is", "and so on" or "through"',
         r'(?<![\w.])(?:e\.g\.|i\.e\.|etc\.|via)(?!\w)', I),
    rule('9.7', CONVENTION, 'contraction: write the full form',
         r"\b\w+(?:n['’]t|['’](?:re|ve|ll|d))\b|\b(?:it|that|there|what|here|let)['’]s\b", I),
    rule('4.2', SOFT, 'empty subject: name the actor',
         r'(?:^|(?<=[.!?]\s))(?:It is (?:necessary|important|recommended|possible|required) to|'
         r'There (?:is|are) (?:\w+ ){1,3}(?:that|which|who))\b', I),
    rule('4.3', SOFT, 'bare "this": name the thing',
         r'(?:^|(?<=[.!?]\s))This (?:is|was|means|makes|causes|lets|allows|requires|will|can)\b'),
    rule('1.5', SOFT, 'general verb: say what happens',
         r'\b(?:handle[sd]?|handling|manage[sd]?|managing|optimi[sz](?:e|es|ed|ing)|deals? with)\b',
         I, strict=True),
    rule('3.2', SOFT, 'passive voice: name the actor', PASSIVE, I, strict=True, skip=_adjectival),
    rule('3.3', SOFT, 'progressive form: use the simple tense',
         r'\b(?:is|are|was|were)\s+(?:being\s+)?(\w{2,}ing)\b', I, strict=True, skip=_not_progressive),
]  # fmt: skip
EN_STEP = [
    rule('5.2', SOFT, 'start the step with an imperative verb',
         r'^(?:you|the user|users|we)\b|^(?:should|must|need to)\b', I),
    rule('5.3', SOFT, 'put the condition before the instruction',
         r'\b(?:if|unless)\b', I, skip=_not_a_trailing_condition),
]  # fmt: skip
EN_PUNCT = [
    rule('8.1', CONVENTION, 'full-width punctuation in English text', r'[，。；：？！（）、]'),
    rule('8.3', CONVENTION, 'put a space between a number and its unit',
         r'\b\d+(?:\.\d+)?(?:ms|s|min|h|KB|MB|GB|TB|KiB|MiB|GiB|px|Hz|kHz|MHz|GHz)\b'),
    rule('8.6', CONVENTION, 'write a range with "–" or "to", not "~"', r'\d\s*[~～]\s*\d'),
    rule('8.7', CONVENTION, 'write dates as 2026-03-02 or March 2, 2026', DATE),
]  # fmt: skip

# Requirement words (3.4). "可/can" belongs to every set, so it is not counted.
REQUIREMENT_SETS = {
    'zh': [
        ('gbt', re.compile(r'(?<![响对相适反供回效呼答感报照策顺内接])应(?![该用答急付对变聘邀允届验]|运而)'
                           r'|(?<![便适事])宜(?![家人])|不必')),
        ('bixu', re.compile(r'必须|务必|(?<![舍恨怪巴免由])不得(?![不已])|应该|(?<![的和与、条些个出])建议(?![是中里])')),
    ],
    'en': [
        ('rfc2119', re.compile(r'\b(?:MUST|SHALL|SHOULD|MAY|REQUIRED|RECOMMENDED|OPTIONAL)\b')),
        ('must', re.compile(r'\b(?:[Mm]ust|[Ss]hould|[Nn]eed not)\b')),
        ('informal', re.compile(r'\b(?:needs? to|ha(?:ve|s) to|make sure|ensure that|ideally|try to|'
                                r'it is recommended|recommended to)\b', I)),
    ],
}  # fmt: skip
DEFAULT_SET = {'zh': 'gbt', 'en': 'must'}
SET_WORDS = {
    'gbt': '应/不应/宜/不宜/不必',
    'bixu': '必须/建议',
    'must': 'must/should/need not',
    'rfc2119': 'MUST/SHOULD/MAY',
    'informal': 'need to/make sure/ideally',
}
QUOTE_STYLES = {'straight': '"', 'curly': '“”', 'corner': '「」『』'}
DE_WORDS = re.compile(r'目的|的确|的话|有的|标的|的士|似的')
LIMITS = {'en': (25, 20), 'zh': (50, 40)}  # (descriptive, step)
BUILTIN_ALLOW = ['statistically significant']
IGNORE = re.compile(r'<!--\s*ste-ignore((?:\s+\d+(?:\.\d+)?)*)\s*-->')
STEP = re.compile(r'^\s*\d+(?:[.)]\s+|、\s*)')
MARKER = re.compile(r'^\s*(?:[-*+]\s+|\d+(?:[.)]\s+|、\s*)|#{1,6}\s+|>\s*)+')
FENCE = re.compile(r'^\s*(`{3,}|~{3,})')
CONFIG_KEYS = {'allow', 'quotes', 'cjkLatinSpace', 'requirementWords'}


# ---------------------------------------------------------------- configuration


def find_config(path):
    start = os.getcwd() if path == '-' else os.path.dirname(os.path.abspath(path))
    candidate = os.path.join(start, '.ste.json')
    if os.path.isfile(candidate):
        return candidate
    directory = start
    while True:
        if os.path.exists(os.path.join(directory, '.git')):
            candidate = os.path.join(directory, '.ste.json')
            return candidate if os.path.isfile(candidate) else None
        parent = os.path.dirname(directory)
        if parent == directory:
            return None
        directory = parent


def load_config(path):
    """Return the validated configuration for the document at path, or {}."""
    config_path = find_config(path)
    if config_path is None:
        return {}
    try:
        with open(config_path, encoding='utf-8-sig') as f:
            config = json.load(f)
    except (OSError, UnicodeDecodeError) as e:
        raise UsageError(f'{config_path}: cannot read the configuration ({e})')
    except ValueError as e:
        raise UsageError(f'{config_path}: not valid JSON ({e})')
    return validate_config(config, config_path)


def validate_config(config, where='.ste.json'):
    def fail(message):
        raise UsageError(f'{where}: {message}')

    if not isinstance(config, dict):
        fail('the top level must be a JSON object')
    unknown = set(config) - CONFIG_KEYS
    if unknown:
        fail(f'unknown key {sorted(unknown)[0]!r}; known keys: {", ".join(sorted(CONFIG_KEYS))}')
    allow = config.get('allow', [])
    if not isinstance(allow, list) or not all(isinstance(w, str) and w for w in allow):
        fail('"allow" must be a list of words')
    quotes = config.get('quotes')
    if quotes is not None:
        per_lang = quotes if isinstance(quotes, dict) else {'zh': quotes, 'en': quotes}
        for lang, style in per_lang.items():
            if lang not in ('zh', 'en') or style not in QUOTE_STYLES:
                fail('"quotes" must be "straight", "curly" or "corner", or {"zh": ..., "en": ...}')
        config['quotes'] = per_lang
    if not isinstance(config.get('cjkLatinSpace', True), bool):
        fail('"cjkLatinSpace" must be true or false')
    words = config.get('requirementWords', {})
    choices = {'zh': ('gbt', 'bixu'), 'en': ('must', 'rfc2119')}
    if not isinstance(words, dict) or any(
        lang not in choices or value not in choices[lang] for lang, value in words.items()
    ):
        fail('"requirementWords" must look like {"zh": "gbt" | "bixu", "en": "must" | "rfc2119"}')
    return config


# ---------------------------------------------------------------- line handling


def iter_lines(text):
    """Yield (line number, line, ignored rules) for each line of prose.

    ignored rules is None (check all), 'all', or a set of rule numbers.
    """
    lines = text.split('\n')
    start = 0
    if lines and lines[0].strip() == '---':
        for n in range(1, len(lines)):
            if lines[n].strip() in ('---', '...'):
                start = n + 1
                break
    fence = None
    in_comment = False
    pending = None
    for n in range(start, len(lines)):
        raw = lines[n]
        m = FENCE.match(raw)
        if fence:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
            continue
        if m:
            fence = m.group(1)
            continue
        if in_comment:
            if '-->' not in raw:
                continue
            raw = raw.split('-->', 1)[1]
            in_comment = False
        ignored = pending
        pending = None
        directive = IGNORE.search(raw)
        if directive:
            rules = set(directive.group(1).split()) or 'all'
            if not IGNORE.sub('', raw).strip():
                pending = rules
                continue
            ignored = rules
        if not raw.strip():
            pending = ignored
            continue
        line = re.sub(r'<!--.*?-->', '', raw)
        if '<!--' in line:
            line = line.split('<!--', 1)[0]
            in_comment = True
        yield n + 1, line, ignored


def clean(line):
    """Mask inline code and URLs; drop link targets and HTML tags."""
    line = re.sub(r'(`+)(?:(?!\1).)+?\1', PH, line)
    line = re.sub(r'\]\([^)]*\)', ']', line)
    line = re.sub(r'https?://[^\s)>\]]+', PH, line)
    return re.sub(r'</?[A-Za-z][^>\n]*>', '', line)


QUOTE_PAIRS = {'"': '"', '“': '”', '「': '」', '『': '』'}


def mask_quotes(text, lang, closing=None):
    """Mask quoted text. Return the text and the closing mark that is still open.

    A quotation can continue on the next line of the same paragraph: pass the
    returned closing mark back in for that line.
    """
    pairs = dict(QUOTE_PAIRS, **({'‘': '’'} if lang == 'zh' else {}))
    out = []
    for c in text:
        if closing:
            out.append(PH)
            if c == closing:
                closing = None
        elif c in pairs:
            out.append(PH)
            closing = pairs[c]
        else:
            out.append(c)
    return ''.join(out), closing


def mask_allowed(text, allow):
    for word in allow:
        text = re.sub(re.escape(word), lambda m: PH * len(m.group(0)), text, flags=I)
    return text


def line_language(line, forced):
    if forced != 'auto':
        return forced
    if HAN.search(line):
        return 'zh'
    if re.search(r'[A-Za-z]', line):
        return 'en'
    if FULL_WIDTH.search(line):
        return 'zh'
    return None


def strip_json(line):
    if re.match(r'^\s*(?:[\[{]|"[^"]*"\s*:)', line) and re.search(r'"[^"]*"\s*:|^\s*[\[{\]}]', line):
        return ''
    return re.sub(r'\{[^{}]*"[^"]*"\s*:[^{}]*\}', '', line)


def sentences(text, lang):
    pattern = r'[。？！；]' if lang == 'zh' else r'(?<=[.?!;])\s+'
    return [s.strip() for s in re.split(pattern, text) if s.strip()]


def sentence_length(sentence, lang):
    count = len(re.findall(r"[A-Za-z0-9_.'’+-]+", sentence)) + sentence.count(PH)
    if lang == 'zh':
        count += len(HAN.findall(sentence))
    return count


# ---------------------------------------------------------------- the check


def check_text(text, lang='auto', strict=False, config=None):
    """Return the findings for one document, sorted by line."""
    config = config or {}
    allow = BUILTIN_ALLOW + config.get('allow', [])
    spaced = config.get('cjkLatinSpace', True)
    findings = []
    requirement_hits = {'zh': [], 'en': []}
    quote_hits = {'zh': {}, 'en': {}}

    def add(n, ignored, rule_id, level, message, snippet):
        if ignored == 'all' or (ignored and rule_id in ignored):
            return
        findings.append(Finding(n, rule_id, level, message, re.sub(PH + '+', '…', snippet).strip()))

    def run(rules, n, ignored, target):
        for r in rules:
            if r.strict and not strict:
                continue
            for m in r.pattern.finditer(target):
                if r.skip and r.skip(target, m):
                    continue
                add(n, ignored, r.rule, r.level, r.message, m.group(0))

    open_quote, previous = None, 0
    for n, raw, ignored in iter_lines(text):
        if n != previous + 1:
            open_quote = None  # A blank line or a code block ends the paragraph.
        previous = n
        if re.match(r'^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)*\|?\s*$', raw):
            continue
        line = clean(raw)
        lang_n = line_language(line, lang)
        if lang_n is None:
            continue
        body = MARKER.sub('', line)
        quoted, open_quote = mask_quotes(body, lang_n, open_quote)
        bare = mask_allowed(quoted, allow)
        is_step = STEP.match(line) is not None
        zh = lang_n == 'zh'

        run(ZH_WORDS if zh else EN_WORDS, n, ignored, bare)
        if is_step:
            run(ZH_STEP if zh else EN_STEP, n, ignored, bare)
        run(ZH_PUNCT if zh else EN_PUNCT, n, ignored, line)

        if zh:
            space = rf'{H}[A-Za-z0-9]|[A-Za-z0-9]{H}' if spaced else rf'{H} +[A-Za-z0-9]|[A-Za-z0-9] +{H}'
            message = '中文和英文、数字之间加一个空格' if spaced else '项目约定中文和英文、数字之间不加空格'
            for m in re.finditer(space, line):
                add(n, ignored, '8.3', CONVENTION, message, m.group(0))
            for clause in re.split(r'[，。；：、？！,;:?!]', bare):
                if DE_WORDS.sub('', clause).count('的') > 2:
                    add(n, ignored, '2.1', CONVENTION, '一个分句里超过两个“的”，拆开写', clause[:30])

        for set_name, pattern in REQUIREMENT_SETS[lang_n]:
            for m in pattern.finditer(bare):
                if not (ignored == 'all' or (ignored and '3.4' in ignored)):
                    requirement_hits[lang_n].append((n, set_name, m.group(0)))

        prose = strip_json(line)
        if not (ignored == 'all' or (ignored and '8.2' in ignored)):
            for style, marks in QUOTE_STYLES.items():
                if any(c in prose for c in marks):
                    quote_hits[lang_n].setdefault(style, []).append(n)

        if strict and not raw.lstrip().startswith(('#', '|')):
            limit = LIMITS[lang_n][1 if is_step else 0]
            for s in sentences(body, lang_n):
                k = sentence_length(s, lang_n)
                if k > limit:
                    unit = '字' if zh else 'words'
                    add(n, ignored, '5.4' if is_step else '6.3', CONVENTION,
                        f'{k} {unit} > {limit}', s[:40] + '…')  # fmt: skip

    for lang_n, hits in requirement_hits.items():
        findings.extend(requirement_findings(lang_n, hits, config.get('requirementWords', {})))
    for lang_n, seen in quote_hits.items():
        findings.extend(quote_findings(lang_n, seen, config.get('quotes', {})))
    findings.sort(key=lambda f: (f.line, f.rule))
    return findings


def requirement_findings(lang, hits, configured):
    counts = Counter(set_name for _, set_name, _ in hits)
    keep = configured.get(lang)
    if keep is None:
        if len(counts) < 2:
            return []
        order = [DEFAULT_SET[lang]] + [s for s, _ in REQUIREMENT_SETS[lang]]
        keep = max(counts, key=lambda s: (counts[s], -order.index(s)))
        summary = ', '.join(f'{s}: {c}' for s, c in counts.most_common())
        message = f'requirement words from more than one set ({summary}); keep {SET_WORDS[keep]}'
    else:
        message = f'the project uses {SET_WORDS[keep]} for requirements'
    return [Finding(n, '3.4', HARD, message, word) for n, s, word in hits if s != keep]


def quote_findings(lang, seen, configured):
    keep = configured.get(lang)
    if keep is None:
        if len(seen) < 2:
            return []
        default = 'curly' if lang == 'zh' else 'straight'
        keep = max(seen, key=lambda s: (len(seen[s]), s == default))
        message = f'more than one quotation style ({", ".join(sorted(seen))}); keep {keep}'
    else:
        message = f'the project uses {keep} quotation marks'
    return [
        Finding(n, '8.2', CONVENTION, message, style)
        for style, lines in seen.items()
        if style != keep
        for n in lines
    ]


# ---------------------------------------------------------------- compare

UNIT = (
    r'(?:(?i:ms|µs|us|ns|s|secs?|seconds?|mins?|minutes?|h|hrs?|hours?|days?|weeks?|months?|years?|'
    r'kb|mb|gb|tb|kib|mib|gib|tib|bytes?|px|hz|khz|mhz|ghz|qps|rps|tps|req/s|ops/s|fps|cores?|'
    r'vcpus?|x)(?![A-Za-z])'
    r'|%|％|°C?|毫秒|微秒|纳秒|秒钟?|分钟|小时|天|周|个月|月|年|倍|核|字节|像素|万|亿)'
)
NUMBER = re.compile(r'(?<![\d.])(\d{4}-\d{1,2}-\d{1,2}|\d+(?:[.,:/]\d+)*)(?:\s?(' + UNIT + r'))?')
UNIT_ALIASES = {
    'sec': 's', 'second': 's', 'min': 'min', 'minute': 'min', 'hr': 'h', 'hour': 'h',
    'hrs': 'h', '秒钟': '秒', '％': '%', 'µs': 'us', 'byte': 'b',
}  # fmt: skip
WARNING_LABEL = re.compile(
    r'\[!(?:WARNING|CAUTION|DANGER)\]'
    r'|(?:警告|注意|危险|Warning|WARNING|Caution|CAUTION|Danger|DANGER)\s*\**\s*[:：]'
)


def number_key(number, unit):
    if re.fullmatch(r'\d{1,3}(?:,\d{3})+(?:\.\d+)?', number):
        number = number.replace(',', '')
    if not unit:
        return number
    unit = unit.lower()
    if len(unit) > 3 and unit.endswith('s') and unit not in ('ops/s', 'req/s'):
        unit = unit[:-1]
    return f'{number} {UNIT_ALIASES.get(unit, unit)}'


def inventory(text):
    """Count the items that a rewrite must keep."""
    items = {name: Counter() for name in ('number', 'code', 'block', 'url')}
    shown = {}
    warnings = 0
    lines = text.split('\n')
    fence, block = None, []
    for raw in lines:
        m = FENCE.match(raw)
        if fence:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                items['block']['\n'.join(b.rstrip() for b in block).strip()] += 1
                fence, block = None, []
            else:
                block.append(raw)
            continue
        if m:
            fence = m.group(1)
            continue
        line = re.sub(r'<!--.*?-->', '', raw)
        for target in re.findall(r'\]\(([^)\s]+)', line):
            items['url'][target] += 1
        line = re.sub(r'\]\([^)]*\)', ']', line)
        for url in re.findall(r'https?://[^\s)>\]`"]+', line):
            items['url'][url.rstrip('.,;:。，；：')] += 1
        line = re.sub(r'https?://[^\s)>\]`"]+', ' ', line)
        for code in re.findall(r'(`+)((?:(?!\1).)+?)\1', line):
            items['code'][code[1].strip()] += 1
        warnings += len(WARNING_LABEL.findall(line))
        line = MARKER.sub('', line.replace('`', ' '))
        line = re.sub(r'^(\d+(?:\.\d+)*\.?)\s', ' ', line) if raw.lstrip().startswith('#') else line
        for m in NUMBER.finditer(line):
            key = number_key(m.group(1), m.group(2))
            items['number'][key] += 1
            shown.setdefault(key, m.group(0).strip())
    if fence and block:
        items['block']['\n'.join(b.rstrip() for b in block).strip()] += 1
    return items, warnings, shown


def compare(original, rewritten):
    """Compare the items of two documents. An item counts once, however often it occurs."""
    before, warnings_before, shown_before = inventory(original)
    after, warnings_after, shown_after = inventory(rewritten)
    lost, added, changed = [], [], []
    for kind in ('number', 'code', 'block', 'url'):
        lost_keys = [k for k in before[kind] if k not in after[kind]]
        added_keys = [k for k in after[kind] if k not in before[kind]]
        if kind == 'number':
            # "4-core" -> "4 cores" adds a unit to the same number. That changes the form, not the
            # fact. Two different units ("45 ms" -> "45 s") stay lost and added.
            for key in list(lost_keys):
                number = key.split(' ')[0]
                match = next(
                    (a for a in added_keys if a.split(' ')[0] == number and number in (a, key)), None
                )
                if match:
                    lost_keys.remove(key)
                    added_keys.remove(match)
                    changed.append((shown_before[key], shown_after[match]))
        shown = shown_before if kind == 'number' else {}
        lost += [(kind, shown.get(k, k)) for k in lost_keys]
        shown = shown_after if kind == 'number' else {}
        added += [(kind, shown.get(k, k)) for k in added_keys]
    return {
        'lost': lost,
        'added': added,
        'changed': changed,
        'warnings': (warnings_before, warnings_after),
    }


def print_compare(result, original, rewritten):
    def show(kind, value, note=''):
        if kind == 'block':
            value = (value.splitlines() or ['(empty block)'])[0][:60] + ' …'
        print(f'  {kind:<7} {value}{note}')

    print(f'lost (in {original}, not in {rewritten}):')
    for item in result['lost']:
        show(*item)
    if not result['lost']:
        print('  none')
    print(f'added (in {rewritten}, not in {original}):')
    for kind, value in result['added']:
        note = '   <- new number: check that it is not invented' if kind == 'number' else ''
        show(kind, value, note)
    if not result['added']:
        print('  none')
    if result['changed']:
        print('changed (same number, unit added or removed; check the meaning):')
        for old, new in result['changed']:
            print(f'  number  {old} -> {new}')
    before, after = result['warnings']
    print(f'warning labels: {before} -> {after}' + (' (lost)' if after < before else ''))
    added_numbers = sum(1 for kind, _ in result['added'] if kind == 'number')
    added_urls = sum(1 for kind, _ in result['added'] if kind == 'url')
    print(
        f'-- lost {len(result["lost"])}, added numbers {added_numbers}, added URLs {added_urls}, '
        f'added other {len(result["added"]) - added_numbers - added_urls}',
        file=sys.stderr,
    )
    return 1 if result['lost'] or added_numbers or added_urls or after < before else 0


# ---------------------------------------------------------------- command line


def read(path):
    if path == '-':
        return sys.stdin.read()
    try:
        with open(path, encoding='utf-8-sig') as f:
            return f.read()
    except FileNotFoundError:
        raise UsageError(f'{path}: file not found')
    except IsADirectoryError:
        raise UsageError(f'{path}: this is a directory; give a file')
    except UnicodeDecodeError:
        raise UsageError(f'{path}: not UTF-8 text; save the file as UTF-8 and run again')
    except OSError as e:
        raise UsageError(f'{path}: cannot read the file ({e.strerror})')


def main(argv):
    parser = argparse.ArgumentParser(
        prog='check.py',
        description='Check a document against the simplified technical writing rules.',
    )
    parser.add_argument('files', nargs='*', metavar='FILE')
    parser.add_argument('--lang', choices=('auto', 'en', 'zh'), default='auto')
    parser.add_argument('--strict', action='store_true', help='fail on conventions; check length')
    parser.add_argument('--compare', nargs=2, metavar=('ORIGINAL', 'REWRITTEN'))
    args = parser.parse_args(argv)
    try:
        if args.compare:
            if args.files:
                raise UsageError('give either FILE... or --compare ORIGINAL REWRITTEN, not both')
            original, rewritten = args.compare
            return print_compare(compare(read(original), read(rewritten)), original, rewritten)
        if not args.files:
            raise UsageError('give at least one FILE (or - for stdin); see --help')
        totals = Counter()
        for path in args.files:
            text = read(path)
            for f in check_text(text, args.lang, args.strict, load_config(path)):
                totals[f.level] += 1
                print(f'{path}:{f.line}: [{f.rule} {f.level}] {f.message}' + (f': {f.text}' if f.text else ''))
    except UsageError as e:
        print(f'check.py: {e}', file=sys.stderr)
        return 2
    print(f'-- {totals[HARD]} hard, {totals[CONVENTION]} convention, {totals[SOFT]} soft', file=sys.stderr)
    return 1 if totals[HARD] or (args.strict and totals[CONVENTION]) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
