from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import common
import chat_check
import lint
import prepare


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
        self.assertEqual(row["pronouns"], "She/Her")

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
        descriptions = "重重光彩之下，重重光景浮现，一开始还能做到万法不侵。"
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
        contexts = "光海诞生性命，五行重现世间，足以危及他性命。"
        hits = {row["source"] for row in lint.glossary_matches(contexts, glossary)}
        self.assertNotIn("性命", hits)
        self.assertNotIn("现世", hits)
        hits = {row["source"] for row in lint.glossary_matches(
            contexts + "性命圆满，现世之中。", glossary
        )}
        self.assertIn("性命", hits)
        self.assertIn("现世", hits)

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


if __name__ == "__main__":
    unittest.main()
