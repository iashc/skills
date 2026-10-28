#!/usr/bin/env python3
"""Tests for check.py. Run: python3 -m unittest discover -s <skill dir>/scripts"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import check  # noqa: E402


def hits(text, rule_id=None, **kwargs):
    findings = check.check_text(text, **kwargs)
    return [f for f in findings if rule_id is None or f.rule == rule_id]


def run_main(argv, stdin=None):
    out, err = io.StringIO(), io.StringIO()
    old_stdin = sys.stdin
    if stdin is not None:
        sys.stdin = io.StringIO(stdin)
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = check.main(argv)
            except SystemExit as e:
                code = e.code
    finally:
        sys.stdin = old_stdin
    return code, out.getvalue(), err.getvalue()


class RuleTest(unittest.TestCase):
    def assertHit(self, text, rule_id, level=None, **kwargs):
        found = hits(text, rule_id, **kwargs)
        self.assertTrue(found, f'{rule_id} should report: {text!r}')
        if level:
            self.assertEqual(found[0].level, level)

    def assertNoHit(self, text, rule_id, **kwargs):
        found = hits(text, rule_id, **kwargs)
        self.assertFalse(found, f'{rule_id} should not report {found} in: {text!r}')


class VagueWords(RuleTest):  # 1.4
    def test_zh_hit(self):
        self.assertHit('性能有显著提升。', '1.4', 'hard')
        self.assertHit('在适当的时候清理缓存。', '1.4')
        self.assertHit('相关文档见下。', '1.4')

    def test_zh_no_hit(self):
        self.assertNoHit('p99 延迟从 120 毫秒降到 45 毫秒。', '1.4')
        self.assertNoHit('显著性水平取 0.05。', '1.4')
        self.assertNoHit('与订单相关的表会被锁住。', '1.4')
        self.assertNoHit('两个变量的相关系数是 0.8。', '1.4')

    def test_en_hit(self):
        self.assertHit('Latency improved significantly.', '1.4', 'hard')
        self.assertHit('Set the appropriate value.', '1.4')

    def test_en_no_hit(self):
        self.assertNoHit('Latency went from 120 ms to 45 ms.', '1.4')
        self.assertNoHit('The difference is statistically significant.', '1.4')

    def test_hedges_are_soft(self):
        for text in ['延迟较为稳定。', '对用户体验造成了一定程度上的影响。', '迁移基本上完成了。',
                     'The default is fairly conservative.', 'The API is basically stable.']:
            found = hits(text, '1.4')
            self.assertEqual([f.level for f in found], ['soft'], text)

    def test_allow_list(self):  # B2
        config = {'allow': ['significant', '显著']}
        self.assertNoHit('The effect is significant (p < 0.01).', '1.4', config=config)
        self.assertNoHit('两组差异显著（p < 0.01）。', '1.4', config=config)
        self.assertHit('Various services restart.', '1.4', config=config)


class HiddenVerbs(RuleTest):  # 3.1
    def test_zh_hit(self):
        self.assertHit('对日志进行压缩。', '3.1', 'hard')
        self.assertHit('实现了对 HTTP/3 的支持。', '3.1')
        self.assertHit('团队做出决定。', '3.1')

    def test_zh_no_hit(self):
        self.assertNoHit('压缩日志。', '3.1')
        self.assertNoHit('任务状态是进行中。', '3.1')
        self.assertNoHit('这个类实现了 `Reader` 接口。', '3.1')

    def test_en_hit(self):
        self.assertHit('Perform a validation of the input.', '3.1', 'hard')
        self.assertHit('We made an adjustment to the timeout.', '3.1')

    def test_en_no_hit(self):
        self.assertNoHit('Validate the input.', '3.1')
        self.assertNoHit('Read the code of conduct.', '3.1')
        self.assertNoHit('Performance is stable.', '3.1')
        self.assertNoHit('The first sentence gives the conclusion.', '3.1')
        self.assertNoHit('Do not make a sentence shorter.', '3.1')


class RequirementWords(RuleTest):  # 3.4
    def test_zh_mixed_sets(self):
        found = hits('上线前必须运行测试。\n回滚前应备份。\n发布前应通知值班人。', '3.4')
        self.assertEqual([(f.line, f.text) for f in found], [(1, '必须')])
        self.assertEqual(found[0].level, 'hard')

    def test_zh_one_set(self):
        self.assertNoHit('上线前应运行测试。\n不宜在高峰期发布。\n可跳过第 3 步。', '3.4')
        self.assertNoHit('上线前必须运行测试。\n建议先在预发环境验证。', '3.4')

    def test_zh_not_requirement_words(self):
        self.assertNoHit('应用响应变慢。\n必须先备份。\n对应的配置在这里。\n便宜的机器也可以。', '3.4')
        self.assertNoHit('评审提出建议。\n上线前应运行测试。', '3.4')

    def test_en_mixed_sets(self):
        found = hits('You must restart the service.\nMake sure that the backup exists.', '3.4')
        self.assertEqual([f.text for f in found], ['Make sure'])

    def test_en_rfc2119_is_its_own_set(self):
        self.assertNoHit('Clients MUST send the token. Servers SHOULD cache it.', '3.4')
        self.assertHit('Clients MUST send the token.\nServers should cache it.\nServers MAY retry.', '3.4')

    def test_configured_set(self):
        config = {'requirementWords': {'zh': 'bixu'}}
        found = hits('上线前应运行测试。', '3.4', config=config)
        self.assertEqual([f.text for f in found], ['应'])
        self.assertNoHit('上线前必须运行测试。', '3.4', config=config)


class Conventions(RuleTest):
    def test_filler_words(self):  # 9.4
        self.assertHit('这个功能开箱即用。', '9.4', 'convention')
        self.assertHit('It simply works.', '9.4', 'convention')
        self.assertNoHit('安装后运行 `app init`。', '9.4')
        self.assertNoHit('Run `app init` after you install it.', '9.4')

    def test_latin_and_contractions(self):  # 9.7
        self.assertHit('Use a flag, e.g. `--force`.', '9.7', 'convention')
        self.assertHit("It's ready.", '9.7')
        self.assertNoHit('Use a flag, for example `--force`.', '9.7')
        self.assertNoHit("The user’s token expires.", '9.7')

    def test_zh_punctuation(self):  # 8.1
        self.assertHit('重启服务,然后检查日志。', '8.1', 'convention')
        self.assertNoHit('重启服务，然后检查日志。', '8.1')

    def test_en_punctuation(self):  # 8.1
        self.assertHit('Restart the service。', '8.1')
        self.assertNoHit('Restart the service.', '8.1')

    def test_zh_space(self):  # 8.3
        self.assertHit('第3步', '8.3', 'convention')
        self.assertNoHit('第 3 步，CPU 占用 40%。', '8.3')
        self.assertNoHit('运行`make`后重试。', '8.3')

    def test_zh_space_off(self):  # 8.3 with "cjkLatinSpace": false
        config = {'cjkLatinSpace': False}
        self.assertHit('第 3 步', '8.3', config=config)
        self.assertNoHit('第3步', '8.3', config=config)

    def test_en_unit_space(self):  # 8.3
        self.assertHit('The timeout is 30s.', '8.3')
        self.assertNoHit('The timeout is 30 s.', '8.3')

    def test_ranges(self):  # 8.6
        self.assertHit('扩容需要 5~10 分钟。', '8.6', 'convention')
        self.assertHit('It takes 5~10 minutes.', '8.6')
        self.assertNoHit('扩容需要 5–10 分钟。', '8.6')

    def test_dates(self):  # 8.7
        self.assertHit('Released on 03/02/2026.', '8.7', 'convention')
        self.assertNoHit('Released on 2026-03-02.', '8.7')

    def test_de_count(self):  # 2.1
        self.assertHit('按用户分片的异步复制的保留 30 天的订单表', '2.1', 'convention')
        self.assertNoHit('订单表按用户分片，数据保留 30 天。', '2.1')

    def test_de_count_excludes_words(self):  # B2 regression
        self.assertNoHit('这次改动的目的是让启动的的确更快的话', '2.1')
        self.assertNoHit('有的服务的配置的目的不同', '2.1')

    def test_conventions_do_not_fail_by_default(self):  # B4
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'a.md')
            with open(path, 'w', encoding='utf-8') as f:
                f.write('重启服务,然后检查日志。\n')
            self.assertEqual(run_main([path])[0], 0)
            self.assertEqual(run_main(['--strict', path])[0], 1)


class Quotes(RuleTest):  # 8.2
    def test_mixed_styles(self):
        found = hits('写“配置”。\n再写“服务”。\n然后写 "镜像"。', '8.2')
        self.assertEqual([f.line for f in found], [3])

    def test_one_style(self):
        self.assertNoHit('写“配置”。\n再写“服务”。', '8.2')

    def test_html_attributes_do_not_count(self):  # B5
        self.assertNoHit('<a title="帮助">写“配置”</a>。\n再写“服务”。', '8.2')

    def test_json_outside_code_does_not_count(self):  # B5
        self.assertNoHit('写“配置”：\n{"name": "app", "port": 8080}\n再写“服务”。', '8.2')
        self.assertNoHit('请求体是 {"id": 1}，再写“服务”。', '8.2')

    def test_configured_style(self):
        found = hits('写“配置”。', '8.2', config={'quotes': {'zh': 'corner', 'en': 'straight'}})
        self.assertEqual(len(found), 1)


class Length(RuleTest):  # 5.4, 6.3
    def test_only_in_strict(self):
        long_line = '服务' * 30 + '。'
        self.assertNoHit(long_line, '6.3')
        self.assertHit(long_line, '6.3', 'convention', strict=True)

    def test_step_limit(self):
        step = '1. ' + '备份' * 21 + '。'
        self.assertHit(step, '5.4', strict=True)
        self.assertNoHit('1. 备份数据库。', '5.4', strict=True)

    def test_en_limit(self):
        self.assertHit(' '.join(['word'] * 26) + '.', '6.3', strict=True)
        self.assertNoHit('The service reads its configuration at startup.', '6.3', strict=True)


class SoftChecks(RuleTest):
    def test_step_imperative(self):  # 5.2
        self.assertHit('1. 需要先停止 worker。', '5.2', 'soft')
        self.assertHit('1. You should stop the worker.', '5.2')
        self.assertNoHit('1. 停止 worker。', '5.2')
        self.assertNoHit('1. Stop the worker.', '5.2')

    def test_step_condition(self):  # 5.3
        self.assertHit('1. 启动服务，如果失败则回滚。', '5.3', 'soft')
        self.assertHit('2. Restore the backup if the migration fails.', '5.3')
        self.assertNoHit('1. 如果迁移失败，用备份恢复。', '5.3')
        self.assertNoHit('2. If the migration fails, restore the backup.', '5.3')
        self.assertNoHit('3. Check if the file exists.', '5.3')
        self.assertNoHit('4. Apply the rules. If you edit the file, keep a copy.', '5.3')

    def test_pronoun(self):  # 4.3
        self.assertHit('配置已更新。这会让服务重启。', '4.3', 'soft')
        self.assertHit('The cache is cold. This makes the first request slow.', '4.3')
        self.assertNoHit('配置已更新。这一步会让服务重启。', '4.3')
        self.assertNoHit('This step makes the first request slow.', '4.3')

    def test_empty_subject(self):  # 4.2
        self.assertHit('It is necessary to restart the service.', '4.2', 'soft')
        self.assertHit('There is a bug that drops events.', '4.2')
        self.assertNoHit('Restart the service.', '4.2')

    def test_strict_only_rules(self):  # 1.5, 3.2, 3.3
        for text, rule_id in [
            ('The worker handles failed jobs.', '1.5'),
            ('优化了查询。', '1.5'),
            ('Requests are forwarded to the backend.', '3.2'),
            ('请求被网关转发。', '3.2'),
            ('The scheduler is listening to the queue.', '3.3'),
            ('调度器正在监听队列。', '3.3'),
        ]:
            self.assertNoHit(text, rule_id)
            self.assertHit(text, rule_id, 'soft', strict=True)

    def test_strict_only_rules_no_hit(self):
        for text, rule_id in [
            ('The worker retries a failed job three times.', '1.5'),
            ('The gateway forwards requests to the backend.', '3.2'),
            ('The scheduler listens to the queue.', '3.3'),
            ('The service is something else.', '3.3'),
        ]:
            self.assertNoHit(text, rule_id, strict=True)

    def test_adjectival_participles_are_not_passive(self):  # B2 regression
        for text in [
            'The price is based on usage.',
            'We are interested in the result.',
            'The data center is located in Frankfurt.',
            'The error is related to the cache.',
        ]:
            self.assertNoHit(text, '3.2', strict=True)


class LineHandling(RuleTest):
    def test_mixed_line_uses_chinese_rules(self):  # B1
        text = '调用 the client library with the retry option enabled 进行重试。'
        self.assertHit(text, '3.1')
        self.assertEqual(check.line_language(text, 'auto'), 'zh')

    def test_code_urls_and_front_matter_are_skipped(self):
        text = '---\ndescription: 进行\n---\n运行 `进行`，见 https://example.com/进行。\n```\n进行\n```\n'
        self.assertEqual(hits(text, '3.1'), [])

    def test_quoted_words_are_mentions(self):
        self.assertNoHit('不写“进行”和“显著”。', '3.1')
        self.assertNoHit('Do not write "perform".', '3.1')

    def test_quotation_continues_on_next_line(self):
        self.assertNoHit('Example: "The script performs a\ncleanup of old images." Done.', '3.1')
        self.assertNoHit('例子：“对日志\n进行压缩。”', '3.1')
        self.assertHit('Example: "unclosed\n\nPerform a cleanup.', '3.1')

    def test_ignore_comment(self):  # B3
        self.assertNoHit('对日志进行压缩。<!-- ste-ignore -->', '3.1')
        self.assertNoHit('<!-- ste-ignore -->\n\n对日志进行压缩。', '3.1')
        self.assertHit('<!-- ste-ignore -->\n第一行。\n对日志进行压缩。', '3.1')

    def test_ignore_one_rule(self):  # B3
        text = '性能显著提升，对日志进行压缩。<!-- ste-ignore 1.4 -->'
        self.assertNoHit(text, '1.4')
        self.assertHit(text, '3.1')


class Config(unittest.TestCase):  # B3
    def write(self, path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data if isinstance(data, str) else json.dumps(data))

    def test_document_directory_first_then_repository_root(self):
        with tempfile.TemporaryDirectory() as root:
            os.mkdir(os.path.join(root, '.git'))
            doc = os.path.join(root, 'docs', 'a.md')
            self.write(doc, '')
            self.write(os.path.join(root, '.ste.json'), {'allow': ['root']})
            self.assertEqual(check.load_config(doc)['allow'], ['root'])
            self.write(os.path.join(root, 'docs', '.ste.json'), {'allow': ['docs']})
            self.assertEqual(check.load_config(doc)['allow'], ['docs'])

    def test_no_config(self):
        with tempfile.TemporaryDirectory() as root:
            os.mkdir(os.path.join(root, '.git'))
            self.assertEqual(check.load_config(os.path.join(root, 'a.md')), {})

    def test_bad_config_exits_2(self):  # B7
        with tempfile.TemporaryDirectory() as root:
            os.mkdir(os.path.join(root, '.git'))
            doc = os.path.join(root, 'a.md')
            self.write(doc, '文档。')
            for bad in ['{not json', {'quote': 'curly'}, {'quotes': 'fancy'}, {'cjkLatinSpace': 'no'}]:
                self.write(os.path.join(root, '.ste.json'), bad)
                code, out, err = run_main([doc])
                self.assertEqual(code, 2, bad)
                self.assertEqual(len(err.strip().splitlines()), 1, err)


class Compare(unittest.TestCase):  # B6
    ORIGINAL = (
        '扩容需要 5~10 分钟，p99 延迟 120ms（1,000 QPS）。\n'
        '运行 `app migrate`，详见 https://example.com/runbook。\n'
        '注意：迁移会锁表。\n'
        '```sh\npg_dump app > app.sql\n```\n'
    )

    def test_identical_items_pass(self):
        rewritten = (
            '**注意：** 迁移会锁表。\n\n'
            '扩容需要 5–10 分钟。p99 延迟是 120 ms（1000 QPS）。\n\n'
            '1. 运行 `app migrate`。详见 https://example.com/runbook。\n'
            '```sh\npg_dump app > app.sql\n```\n'
        )
        result = check.compare(self.ORIGINAL, rewritten)
        self.assertEqual(result['lost'], [])
        self.assertEqual(result['added'], [])
        self.assertEqual(result['warnings'], (1, 1))

    def test_lost_and_added_items(self):
        rewritten = '扩容需要 5–10 分钟，p99 延迟 45 ms。\n运行迁移。\n'
        result = check.compare(self.ORIGINAL, rewritten)
        lost = set(result['lost'])
        added = set(result['added'])
        self.assertIn(('number', '120ms'), lost)
        self.assertIn(('code', 'app migrate'), lost)
        self.assertIn(('block', 'pg_dump app > app.sql'), lost)
        self.assertIn(('url', 'https://example.com/runbook'), lost)
        self.assertEqual(added, {('number', '45 ms')})
        self.assertEqual(result['warnings'], (1, 0))

    def test_repeated_number_is_not_new(self):
        result = check.compare('延迟为 0 时继续。', '延迟不为 0 时等待。延迟变为 0 后继续。')
        self.assertEqual(result['added'], [])

    def test_unit_added_to_same_number_is_a_change(self):
        result = check.compare('on a 4-core VM', 'on a VM with 4 cores')
        self.assertEqual((result['lost'], result['added']), ([], []))
        self.assertEqual(result['changed'], [('4', '4 cores')])

    def test_different_unit_is_lost_and_added(self):
        result = check.compare('p99 is 45 ms.', 'p99 is 45 s.')
        self.assertEqual(result['lost'], [('number', '45 ms')])
        self.assertEqual(result['added'], [('number', '45 s')])

    def test_exit_status(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = os.path.join(d, 'a.md'), os.path.join(d, 'b.md')
            with open(a, 'w', encoding='utf-8') as f:
                f.write('重试 3 次。')
            with open(b, 'w', encoding='utf-8') as f:
                f.write('重试 3 次，间隔 5 秒。')
            code, out, _ = run_main(['--compare', a, b])
            self.assertEqual(code, 1)
            self.assertIn('new number', out)
            self.assertEqual(run_main(['--compare', a, a])[0], 0)


class CommandLine(unittest.TestCase):  # B7
    def test_missing_file(self):
        code, out, err = run_main(['/no/such/file.md'])
        self.assertEqual(code, 2)
        self.assertEqual(err.strip(), 'check.py: /no/such/file.md: file not found')

    def test_not_utf8(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'a.md')
            with open(path, 'wb') as f:
                f.write('配置'.encode('gbk'))
            code, _, err = run_main([path])
            self.assertEqual(code, 2)
            self.assertIn('not UTF-8', err)

    def test_no_arguments(self):
        self.assertEqual(run_main([])[0], 2)

    def test_stdin_and_exit_status(self):
        self.assertEqual(run_main(['-'], stdin='对日志进行压缩。')[0], 1)
        self.assertEqual(run_main(['-'], stdin='压缩日志。')[0], 0)


if __name__ == '__main__':
    unittest.main()
