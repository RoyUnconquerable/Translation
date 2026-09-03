from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import common
import chat_check
import lint


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

    def test_user_critical_style_contracts(self):
        style = (self.root / "reference" / "style-guide.md").read_text(
            encoding="utf-8"
        )
        prose = " ".join(style.split())
        self.assertIn("Italics identify direct thought; they do not determine tense.", prose)
        self.assertIn("Preserve the source image or cultural referent, not Chinese grammar.", prose)
        self.assertIn("not mechanically from the source's quotation glyphs", prose)
        self.assertIn("Free indirect narration remains roman", prose)
        self.assertIn("Archaic diction is optional, not automatic", prose)

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


if __name__ == "__main__":
    unittest.main()
