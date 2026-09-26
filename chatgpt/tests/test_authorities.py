from __future__ import annotations

import json
import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import common
import chat_check
import lint
import prepare
import state
import audit


class AuthorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]

    def test_canonical_regression_terms(self):
        glossary = common.load_glossary(self.root)
        self.assertEqual(glossary["神念"]["target"], "divine sense")
        self.assertEqual(glossary["都玄"]["target"], "Du Xuan")
        self.assertEqual(glossary["剑锋金"]["target"], "Sword Edge Metal")
        self.assertEqual(
            glossary["两仪生灭玄光"]["target"],
            "Yin-Yang Creation and Destruction Profound Light",
        )
        self.assertEqual(common.glossary_paths(self.root), [
            self.root / "glossary" / "terminology.tsv"
        ])

    def test_sword_sovereign_pronouns(self):
        entities = common.load_entities(self.root)
        row = next(item for item in entities if item["entity_id"] == "sword_sovereign")
        self.assertEqual(prepare.scoped_pronouns(row, 1128), "they/them/their")
        self.assertEqual(prepare.scoped_pronouns(row, 1129), "she/her")
        vast = next(item for item in entities if item["entity_id"] == "vast_sky")
        self.assertEqual(prepare.scoped_pronouns(vast, 1128), "they/them/their")
        self.assertEqual(prepare.scoped_pronouns(vast, 1129), "he/him/his")

    def test_owner_terms_preserve_older_and_newer_rulings(self):
        glossary = common.load_glossary(self.root)
        expected = {
            "终虎": "End Tiger", "末劫": "Final Kalpa",
            "真仙人": "True Immortal", "真仙": "True Immortal",
            "修真": "Cultivating Truth", "修真道主": "Cultivating Truth Dao Lord",
            "【均】": "Jun", "灵性": "spirituality",
            "定数": "Destiny", "命数": "Fate", "气数": "Fortune",
            "变数": "Variable|Variables", "冥府": "Underworld",
            "慧极必伤": "Supreme Wisdom Must Bring Harm", "剑种": "Sword Seed",
            "情关": "Gate of Feeling",
            "道侣": "Dao Companion|Dao Companions",
            "情劫": "Tribulation of Feeling|Tribulations of Feeling",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(glossary[source]["target"], target)
        self.assertEqual(glossary["一线生机"]["target"], "sliver of hope")

    def test_explicit_title_required_without_masking_supplied_title(self):
        glossary = common.load_glossary(self.root)
        self.assertEqual(lint.expansion_errors(
            "修真微笑。", "Cultivating Truth smiled.", glossary), [])
        self.assertTrue(lint.expansion_errors(
            "修真微笑。", "The Cultivating Truth Dao Lord smiled.", glossary))
        self.assertEqual(lint.expansion_errors(
            "修真道主微笑。", "The Cultivating Truth Dao Lord smiled.", glossary), [])
        self.assertEqual(lint.expansion_errors(
            "修真道主微笑，修真开口。",
            "The Cultivating Truth Dao Lord smiled. Cultivating Truth spoke.", glossary), [])

    def test_sentence_initial_common_term_case_inside_paragraph(self):
        for text in ['He looked up. Wisdom light shone.',
                     'He said: "Wisdom light shone."', '*Wisdom light shone.*']:
            with self.subTest(text=text):
                self.assertTrue(lint.target_has_variant(text, ["wisdom light"]))
        for text in ['His Wisdom light shone.', 'His Wisdom Light shone.']:
            self.assertFalse(lint.target_has_variant(text, ["wisdom light"]))

    def test_recovered_substring_contexts_keep_real_terms_checked(self):
        glossary = common.load_glossary(self.root)
        examples = {
            "盛时": "全盛时期的他", "神念": "心神念头完全符合自身",
            "先天": "先天就和精炁不合，先天资质有缺",
            "入道": "只求入道的岁月", "中古": "吕阳心中古怪",
            "变数": "一套变数少，另一套变数多，会不会有变数，平白多出一个变数",
        }
        for source, context in examples.items():
            with self.subTest(source=source):
                hits = {r["source"] for r in lint.glossary_matches(context, glossary)}
                self.assertNotIn(source, hits)
                hits = {r["source"] for r in lint.glossary_matches(
                    context + "。" + source + "。", glossary)}
                self.assertIn(source, hits)

    def test_incoming_chapter_detects_jointly_stale_state_and_ledger(self):
        routing = {"progress": {"latest_source_seen": 1309}}
        self.assertEqual(state.incoming_chapter_errors(1310, routing), [])
        self.assertEqual(state.incoming_chapter_errors(1309, routing), [])
        self.assertIn("reconcile verified", state.incoming_chapter_errors(1311, routing)[0])
        self.assertEqual(routing, {"progress": {"latest_source_seen": 1309}})

    def test_observed_session_frontier_is_bounded_and_read_only(self):
        routing = {"progress": {"latest_source_seen": 1309}}
        before = json.dumps(routing)
        self.assertEqual(state.incoming_chapter_errors(
            1312, routing, observed_through=1311), [])
        self.assertTrue(state.incoming_chapter_errors(
            1312, routing, observed_through=1310))
        for frontier in (1308, 1312, 1313):
            with self.subTest(frontier=frontier):
                self.assertTrue(state.incoming_chapter_errors(
                    1312, routing, observed_through=frontier))
        self.assertEqual(json.dumps(routing), before)

    def test_prepare_uses_verified_frontier_without_writing_state(self):
        path = self.root / "chapters" / "state.json"
        before = path.read_bytes()
        frontier = state.translation_frontier(json.loads(before))
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.txt"
            source.write_text(f"第{frontier + 2}章 测试\n\n道天齐借出慧光。\n",
                              encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "prepare.py"), str(source),
                 "--observed-through", str(frontier + 1)],
                capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("repository state unchanged", result.stdout)
        self.assertIn("no delivery/approval inferred", result.stdout)
        entities = common.load_entities(self.root)
        entity = next(r for r in entities if "道天齐" in r["source_aliases"].split("|"))
        self.assertIn(entity["notes"], result.stdout)
        self.assertIn(common.load_glossary(self.root)["慧光"]["notes"], result.stdout)
        self.assertEqual(path.read_bytes(), before)

    def test_number_inventory_includes_odds_and_physical_measures(self):
        source = "三尺青锋，九寸九厘。胜率三七开，达到五五开，添上两成胜算。"
        values = {m.group(0) for m in prepare.NUMBER_RE.finditer(source)}
        self.assertTrue({"三尺", "九寸", "九厘", "三七开", "五五开", "两成"} <= values)

    def test_size_warning_does_not_hide_structural_authority_failure(self):
        output = io.StringIO()
        with patch.object(audit, "SIZE_LIMITS", {"reference/style-guide.md": 1}), \
                redirect_stdout(output):
            audit.main()
        self.assertIn("authority audit: WARN", output.getvalue())
        self.assertIn("authority audit: PASS", output.getvalue())
        output = io.StringIO()
        with patch.object(audit.common, "load_glossary",
                          side_effect=ValueError("duplicate source key")), \
                redirect_stdout(output), self.assertRaises(SystemExit):
            audit.main()
        self.assertIn("duplicate source key", output.getvalue())
        self.assertIn("authority audit: FAIL", output.getvalue())

    def test_prepare_rejects_unreconciled_source_gap_read_only(self):
        path = self.root / "chapters" / "state.json"
        before = path.read_bytes()
        frontier = state.translation_frontier(json.loads(before))
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.txt"
            source.write_text(f"第{frontier + 2}章 测试\n\n正文。\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "prepare.py"), str(source)],
                capture_output=True, text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("skips the recorded translation frontier", result.stdout + result.stderr)
        self.assertEqual(path.read_bytes(), before)

    def test_hard_terms_and_phrase_memory_do_not_overlap(self):
        hard = set(common.load_glossary(self.root))
        rows = common.load_phrase_memory(self.root)
        phrases = {row["source"] for row in rows}
        self.assertFalse(hard.intersection(phrases))
        self.assertEqual({row["scope"] for row in rows}, {"fixed", "image", "sense"})

    def test_corrected_allusion_and_adaptive_phrase_memory(self):
        phrases = {
            row["source"]: row for row in common.load_phrase_memory(self.root)
        }
        self.assertEqual(phrases["圣人不仁"]["target"], "The sage is not benevolent.")
        self.assertEqual(phrases["圣人不仁"]["scope"], "fixed")
        self.assertNotIn("Status", "\n".join(row["target"] for row in phrases.values()))
        self.assertEqual(phrases["道德绑架"]["scope"], "sense")
        self.assertEqual(phrases["道主之意就是天意"]["scope"], "sense")
        self.assertNotIn("Earth", phrases["不知天高"]["target"])

    def test_longest_source_term_wins(self):
        glossary = {
            "凌霄": {"source": "凌霄", "target": "Skyward", "variants": ["Skyward"]},
            "凌霄宝殿": {
                "source": "凌霄宝殿",
                "target": "Palace of Soaring Clouds",
                "variants": ["Palace of Soaring Clouds"],
            },
        }
        matches = lint.glossary_matches("凌霄宝殿洞开", glossary)
        self.assertEqual([item["source"] for item in matches], ["凌霄宝殿"])

    def test_target_matching_respects_proper_case(self):
        self.assertTrue(lint.target_has_variant("His divine sense spread.", ["divine sense"]))
        self.assertTrue(lint.target_has_variant("Divine sense spread.", ["divine sense"]))
        self.assertFalse(lint.target_has_variant("His Divine Sense spread.", ["divine sense"]))
        self.assertFalse(lint.target_has_variant("the sword sovereign", ["Sword Sovereign"]))

    def test_descriptive_name_substrings_keep_real_names_checked(self):
        glossary = common.load_glossary(self.root)
        descriptions = "重重光彩之下，重重光景浮现，重重光色遮蔽一切，一开始还能做到万法不侵。"
        names = {row["source"] for row in lint.glossary_matches(descriptions, glossary)}
        self.assertNotIn("重光", names)
        self.assertNotIn("万法", names)
        actual_names = descriptions + "重光随后望向万法。"
        names = {row["source"] for row in lint.glossary_matches(actual_names, glossary)}
        self.assertIn("重光", names)
        self.assertIn("万法", names)

    def test_contextual_exceptions_preserve_unqualified_terms(self):
        glossary = common.load_glossary(self.root)
        contextual = "比他刚刚现世时还要强，一股排山倒海的伟力落下。"
        names = {row["source"] for row in lint.glossary_matches(contextual, glossary)}
        self.assertNotIn("现世", names)
        self.assertNotIn("伟力", names)
        actual_terms = contextual + "现世之中，伟力交织。"
        names = {row["source"] for row in lint.glossary_matches(actual_terms, glossary)}
        self.assertIn("现世", names)
        self.assertIn("伟力", names)

    def test_not_quite_same_does_not_mask_taiyi(self):
        glossary = common.load_glossary(self.root)
        ordinary = "和我想要的慧光恐怕不太一样。"
        hits = {r["source"] for r in lint.glossary_matches(ordinary, glossary)}
        self.assertNotIn("太一", hits)
        mixed = ordinary + "太一仍然是一个意识集合体。"
        hits = {r["source"] for r in lint.glossary_matches(mixed, glossary)}
        self.assertIn("太一", hits)

    def test_mental_absence_is_not_the_outer_heavens(self):
        glossary = common.load_glossary(self.root)
        figurative = "他魂游天外，开始流口水。"
        self.assertNotIn("天外", {r["source"] for r in lint.glossary_matches(figurative, glossary)})
        both = figurative + "随后前往天外。"
        self.assertIn("天外", {r["source"] for r in lint.glossary_matches(both, glossary)})

    def test_duplicate_glossary_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "glossary").mkdir()
            (root / "glossary" / "terminology.tsv").write_text(
                "source\ttarget\tnotes\n神念\tdivine sense\t\n神念\tthought\t\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "duplicate source key"):
                common.load_glossary(root)

    def test_ch1307_contexts_do_not_mask_real_terms(self):
        glossary = common.load_glossary(self.root)
        contexts = "光海诞生性命，五行重现世间，足以危及他性命，一招就要了他性命，亿万众生的性命被摆上赌桌，你损失的只是性命修为。"
        hits = {row["source"] for row in lint.glossary_matches(contexts, glossary)}
        self.assertNotIn("性命", hits)
        self.assertNotIn("现世", hits)
        hits = {row["source"] for row in lint.glossary_matches(
            contexts + "性命圆满，现世之中。", glossary
        )}
        self.assertIn("性命", hits)
        self.assertIn("现世", hits)

    def test_ordinary_life_keeps_paired_cultivation_checked(self):
        glossary = common.load_glossary(self.root)
        for source in ("如同签下性命一般。", "求饶也换不来性命。"):
            with self.subTest(source=source):
                hits = {r["source"] for r in lint.glossary_matches(source, glossary)}
                self.assertNotIn("性命", hits)
                hits = {r["source"] for r in lint.glossary_matches(
                    source + "性命圆满。", glossary
                )}
                self.assertIn("性命", hits)

    def test_named_five_elements_dao_keeps_generic_dao_checked(self):
        glossary = common.load_glossary(self.root)
        for named in ("五行大道", "【五行】大道"):
            hits = {r["source"]: r for r in lint.glossary_matches(named, glossary)}
            self.assertIn(named, hits)
            self.assertNotIn("大道", hits)
            self.assertTrue(lint.target_has_variant("the Five Elements Dao", hits[named]["variants"]))
            self.assertFalse(lint.target_has_variant("the Five Elements", hits[named]["variants"]))
            hits = {r["source"] for r in lint.glossary_matches(named + "和另一条大道。", glossary)}
            self.assertIn("大道", hits)

    def test_beast_taming_dao_is_not_the_person(self):
        glossary = common.load_glossary(self.root)
        hits = {row["source"] for row in lint.glossary_matches("豢妖道奴役祖龙。", glossary)}
        self.assertIn("豢妖道", hits)
        self.assertNotIn("豢妖", hits)
        hits = {row["source"] for row in lint.glossary_matches("豢妖道与豢妖前辈。", glossary)}
        self.assertIn("豢妖道", hits)
        self.assertIn("豢妖", hits)

    def test_fraction_inventory_does_not_truncate(self):
        self.assertEqual(prepare.NUMBER_RE.findall("世上九成九的人，八万四千年后。"),
                         ["九成九", "八万四千年"])

    def test_rank_and_approximate_quantity_inventory(self):
        self.assertEqual(prepare.NUMBER_RE.findall("四等大真君，祭炼几万年，耗时数千年。"),
                         ["四等", "几万年", "数千年"])

    def test_adverbial_focus_does_not_disable_one_mind(self):
        glossary = common.load_glossary(self.root)
        source = "他一心只想着修复。"
        hits = {row["source"] for row in lint.glossary_matches(source, glossary)}
        self.assertNotIn("一心", hits)
        hits = {row["source"] for row in lint.glossary_matches(source + "世尊施展一心。", glossary)}
        self.assertIn("一心", hits)

    def test_scripts_find_their_pipeline_outside_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src, tgt = root / "source.txt", root / "target.txt"
            src.write_text("第1章 测试\n\n他一心只想着修复。\n", encoding="utf-8")
            tgt.write_text("Chapter 1: Test\n\nHe could think only of repairs.\n", encoding="utf-8")
            for script, args, marker in (
                ("prepare.py", [str(src)], "paragraphs: 2"),
                ("chat_check.py", [str(src), str(tgt), "--scene-break-before"], "PASS (2 paragraphs)"),
            ):
                result = subprocess.run([sys.executable, str(SCRIPTS / script), *args],
                                        cwd=root, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                self.assertIn(marker, result.stdout)
            self.assertEqual(common.find_root(self.root), self.root)
            with self.assertRaises(SystemExit):
                common.find_root(root)

    def test_chat_rejects_empty_and_mismatched_chapters(self):
        self.assertEqual(chat_check.chapter_input_errors([], []),
                         ["source is empty", "target is empty"])
        self.assertTrue(chat_check.chapter_input_errors(["第1307章 测试"], []))
        self.assertTrue(chat_check.chapter_input_errors(["第1307章 测试"], ["Test"]))
        self.assertEqual(chat_check.chapter_input_errors(["第1307章 测试"],
                                                        ["Chapter 1308: Test"]),
                         ["target chapter number does not match source"])
        self.assertEqual(chat_check.chapter_input_errors(["第1307章 测试"],
                                                        ["Chapter 1307: Test"]), [])

    def test_lint_is_read_only_without_write_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work = root / "chapters" / "work"
            work.mkdir(parents=True)
            (work / "ch1.segments.jsonl").write_text(
                json.dumps({"id": "ch1-0001", "src": "他的神念展开。"}, ensure_ascii=False)
                + "\n",
                encoding="utf-8",
            )
            (work / "ch1.draft.jsonl").write_text(
                json.dumps({"id": "ch1-0001", "tgt": "His divine sense spread."}) + "\n",
                encoding="utf-8",
            )
            glossary = {
                "神念": {
                    "source": "神念",
                    "target": "divine sense",
                    "variants": ["divine sense"],
                }
            }
            report = lint.lint_chapter(
                root,
                common.DEFAULT_CONFIG,
                glossary,
                "ch1",
                write_report=False,
            )
            self.assertEqual(report["status"], "pass")
            self.assertFalse((work / "ch1.lint.json").exists())

    def test_shennian_wrong_rendering_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work = root / "chapters" / "work"
            work.mkdir(parents=True)
            (work / "ch1.segments.jsonl").write_text(
                json.dumps({"id": "ch1-0001", "src": "他的神念展开。"}, ensure_ascii=False)
                + "\n",
                encoding="utf-8",
            )
            (work / "ch1.draft.jsonl").write_text(
                json.dumps({"id": "ch1-0001", "tgt": "His divine thoughts spread."})
                + "\n",
                encoding="utf-8",
            )
            glossary = {
                "神念": {
                    "source": "神念",
                    "target": "divine sense",
                    "variants": ["divine sense"],
                }
            }
            report = lint.lint_chapter(
                root, common.DEFAULT_CONFIG, glossary, "ch1", write_report=False
            )
            self.assertIn("glossary", {item["check"] for item in report["fails"]})

    def test_repository_authority_is_explicit(self):
        state = json.loads(
            (self.root / "chapters" / "state.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            state["repository_authority"],
            {
                "remote": "origin",
                "canonical_branch": "claude/translation-pipeline-build-3gdy6r",
                "durable_record": "latest_committed_and_pushed_tip",
            },
        )
        repo_root = self.root.parent
        self.assertFalse((repo_root / ".claude" / "settings.json").exists())
        self.assertFalse((repo_root / ".claude" / "agents").exists())
        self.assertFalse((repo_root / ".claude" / "skills").exists())

    def test_cjk_punctuation_is_a_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work = root / "chapters" / "work"
            work.mkdir(parents=True)
            (work / "ch1.segments.jsonl").write_text(
                json.dumps({"id": "ch1-0001", "src": "测试。"}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            (work / "ch1.draft.jsonl").write_text(
                json.dumps({"id": "ch1-0001", "tgt": "Test。"}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            report = lint.lint_chapter(
                root, common.DEFAULT_CONFIG, {}, "ch1", write_report=False
            )
            self.assertIn("cjk-punct", {item["check"] for item in report["fails"]})

    def test_chat_paragraphs_ignore_valid_scene_breaks(self):
        target = "Chapter 1: Test\n\nFirst.\n\n---\n\nSecond."
        self.assertEqual(
            chat_check.paragraphs(target, allow_scene_breaks=True),
            ["Chapter 1: Test", "First.", "Second."],
        )
        self.assertEqual(chat_check.scene_break_errors(target), [])

    def test_chat_scene_break_cannot_end_chapter(self):
        self.assertEqual(
            chat_check.scene_break_errors("Chapter 1: Test\n\n---"),
            ["scene break cannot end the chapter"],
        )

    def test_prepare_and_check_share_indices_across_source_scene_breaks(self):
        source_text = "第1章 测试\r\n\r\n他抬头。\r\n\r\n---\r\n\r\n道天齐借出慧光。\r\n"
        target_text = "Chapter 1: Test\n\nHe looked up.\n\n---\n\nDao Tianqi lent him wisdom light.\n"
        with tempfile.TemporaryDirectory() as tmp:
            source, target = Path(tmp) / "source.txt", Path(tmp) / "target.txt"
            source.write_text(source_text, encoding="utf-8")
            target.write_text(target_text, encoding="utf-8")
            inventory = subprocess.run(
                [sys.executable, str(SCRIPTS / "prepare.py"), str(source)],
                capture_output=True, text=True,
            )
            checked = subprocess.run(
                [sys.executable, str(SCRIPTS / "chat_check.py"), str(source),
                 str(target), "--scene-break-before", "3"],
                capture_output=True, text=True,
            )
            target.write_text(target_text.replace("\n\n---", ""), encoding="utf-8")
            missing = subprocess.run(
                [sys.executable, str(SCRIPTS / "chat_check.py"), str(source),
                 str(target), "--scene-break-before"],
                capture_output=True, text=True,
            )
        self.assertEqual(inventory.returncode, 0, inventory.stdout + inventory.stderr)
        self.assertIn("paragraphs: 3", inventory.stdout)
        self.assertIn("explicit source scene breaks before: [3]", inventory.stdout)
        self.assertIn("[3] 道天齐 -> Dao Tianqi", inventory.stdout)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertIn("PASS (3 paragraphs)", checked.stdout)
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("missing reviewed scene break", missing.stdout)

    def test_approved_scripture_display_cannot_be_flattened(self):
        source = "【吾疾天地不仁，大道不均，今为尔等均之！】"
        phrases = common.load_phrase_memory(self.root)
        row = next(row for row in phrases if row["source"] in source)
        approved = row["target"]
        self.assertEqual(lint.fixed_display_errors(source, approved, phrases), [])
        self.assertEqual(lint.punctuation_residue(source, approved), [])
        plain = approved.removeprefix("**【").removesuffix("】**")
        self.assertTrue(lint.fixed_display_errors(source, plain, phrases))
        changed = approved.replace("resent", "abhor")
        self.assertTrue(lint.fixed_display_errors(source, changed, phrases))

    def test_display_brackets_do_not_allow_other_source_punctuation(self):
        self.assertEqual(lint.punctuation_residue("【测试】", "**【Test】**"), [])
        self.assertEqual(lint.punctuation_residue("【测试】", "**【Test。】**"), ["。"])
        self.assertTrue(lint.punctuation_residue("【测试】", "【Test】"))
        self.assertTrue(lint.punctuation_residue("测试", "**【Test】**"))
        self.assertTrue(lint.punctuation_residue("【测试】", "**【Test**"))

    def test_reviewed_scene_breaks_detect_omissions_and_additions(self):
        plain = "Chapter 1: Test\n\nOutside.\n\nInside."
        target = "Chapter 1: Test\n\nOutside.\n\n---\n\nInside."
        self.assertEqual(chat_check.scene_break_positions(target), [3])
        self.assertEqual(chat_check.scene_break_errors(target, [3]), [])
        self.assertIn("missing reviewed scene break", chat_check.scene_break_errors(plain, [3])[0])
        self.assertIn("unreviewed scene break", chat_check.scene_break_errors(target, [])[0])
        self.assertEqual(chat_check.paragraphs(target, allow_scene_breaks=True),
                         chat_check.paragraphs(plain))

    def test_heavenly_scripture_replaces_previous_name(self):
        glossary = common.load_glossary(self.root)
        self.assertEqual(glossary["天书"]["target"], "Heavenly Scripture")
        self.assertTrue(lint.target_has_variant("the Heavenly Scripture", glossary["天书"]["variants"]))
        self.assertFalse(lint.target_has_variant("the Heavenly Book", glossary["天书"]["variants"]))

    def test_display_splits_preserve_source_checks_and_scene_positions(self):
        source_text = "第1章 测试\n\n他看见【你已死亡。】于是走了。\n\n---\n\n道天齐借出慧光。\n"
        target_text = "Chapter 1: Test\n\nHe saw:\n\n**【You have died】**\n\nThen he left.\n\n---\n\nDao Tianqi lent him wisdom light.\n"
        with tempfile.TemporaryDirectory() as tmp:
            source, target = Path(tmp) / "source.txt", Path(tmp) / "target.txt"
            source.write_text(source_text, encoding="utf-8")
            target.write_text(target_text, encoding="utf-8")
            command = [sys.executable, str(SCRIPTS / "chat_check.py"), str(source),
                       str(target), "--scene-break-before", "3"]
            undeclared = subprocess.run(command, capture_output=True, text=True)
            mapped = subprocess.run(command + ["--display-splits", "2:3"], capture_output=True, text=True)
            target.write_text(target_text.replace("wisdom light", "radiance"), encoding="utf-8")
            missing_term = subprocess.run(command + ["--display-splits", "2:3"], capture_output=True, text=True)
            target.write_text(target_text.replace("\n\n---", "").replace("Then he left.", "---\n\nThen he left."), encoding="utf-8")
            inner_break = subprocess.run(command + ["--display-splits", "2:3"], capture_output=True, text=True)
        self.assertNotEqual(undeclared.returncode, 0)
        self.assertEqual(mapped.returncode, 0, mapped.stdout + mapped.stderr)
        self.assertIn("3 source paragraphs, 5 target paragraphs", mapped.stdout)
        self.assertNotEqual(missing_term.returncode, 0)
        self.assertIn("requires wisdom light", missing_term.stdout)
        self.assertNotEqual(inner_break.returncode, 0)
        self.assertIn("scene break inside a display split", inner_break.stdout)

    def test_lead_in_merges_join_fragment_to_next_paragraph(self):
        source_text = "第1章 测试\n\n他走了。\n\n与此同时。\n\n道天齐借出慧光。\n"
        target_text = "Chapter 1: Test\n\nHe left.\n\n---\n\nMeanwhile, Dao Tianqi lent him wisdom light.\n"
        with tempfile.TemporaryDirectory() as tmp:
            source, target = Path(tmp) / "source.txt", Path(tmp) / "target.txt"
            source.write_text(source_text, encoding="utf-8")
            target.write_text(target_text, encoding="utf-8")
            base = [sys.executable, str(SCRIPTS / "chat_check.py"), str(source), str(target)]
            undeclared = subprocess.run(base + ["--scene-break-before", "3"], capture_output=True, text=True)
            merged = subprocess.run(base + ["--scene-break-before", "3", "--merge-into-next", "3"],
                                    capture_output=True, text=True)
            inner = subprocess.run(base + ["--scene-break-before", "4", "--merge-into-next", "3"],
                                   capture_output=True, text=True)
        self.assertNotEqual(undeclared.returncode, 0)
        self.assertEqual(merged.returncode, 0, merged.stdout + merged.stderr)
        self.assertIn("4 source paragraphs, 3 target paragraphs", merged.stdout)
        self.assertNotEqual(inner.returncode, 0)
        self.assertIn("inside a lead-in merge", inner.stdout)
        for bad in ([1], [4], [2, 3], [2, 2]):
            with self.subTest(bad=bad):
                self.assertTrue(chat_check.apply_lead_in_merges(["t", "a", "b", "c"], bad)[2])

    def test_display_split_cannot_authorize_arbitrary_prose_splits(self):
        src = ["title", "source"]
        target = ["title", "He looked.", "Then he left."]
        _, _, errors = chat_check.align_display_splits(src, target, ["2:2"])
        self.assertTrue(any("no standalone panel" in error for error in errors))
        target = ["title", "He looked.", "Then he left.", "**【Done】**"]
        _, _, errors = chat_check.align_display_splits(src, target, ["2:3"])
        self.assertTrue(any("divides ordinary prose" in error for error in errors))
        for declaration in (["1:2"], ["3:2"], ["2:1"], ["2:2", "2:2"], ["two:2"]):
            with self.subTest(declaration=declaration):
                self.assertTrue(chat_check.align_display_splits(src, target, declaration)[2])

    def test_current_panel_punctuation_and_formatting(self):
        for text in ["**【Done】**", "**【Ready?】**", "**【Settling...】**", "**【First. Second】**"]:
            self.assertEqual(lint.display_format_errors(text), [], text)
        for text in ["**【Done.】**", "**【Done!】**", "【Done】", "**Done**", "**【 Done】**",
                     "**【Done】**!", "He saw **【Done】**", "**【*Done*】**", "**【A】**\n**【B】**"]:
            self.assertTrue(lint.display_format_errors(text), text)

    def test_approved_english_routes_next_chapter_without_claiming_source_access(self):
        routing = {"progress": {"latest_source_seen": 1334},
                   "approved_manuscript": {"latest_chapter": 1338, "owner_approved_on": "2026-09-16"}}
        before = json.dumps(routing)
        self.assertEqual(state.translation_frontier(routing), 1338)
        self.assertEqual(state.incoming_chapter_errors(1339, routing), [])
        self.assertTrue(state.incoming_chapter_errors(1340, routing))
        self.assertEqual(json.dumps(routing), before)


if __name__ == "__main__":
    unittest.main()
