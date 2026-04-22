from __future__ import annotations

import unittest
from pathlib import Path

from oss_first_pass.analyzer import analyze_repository


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class AnalyzeRepositoryTests(unittest.TestCase):
    def test_detects_basic_contributor_signals_and_setup_gap(self) -> None:
        report = analyze_repository(FIXTURES_DIR / "repo_with_setup_gap")

        self.assertIn("tiny tool for managing examples", report.summary)
        self.assertIn("Node.js", report.inferred_stack)
        self.assertTrue(report.contributor_signals["readme"])
        self.assertTrue(report.contributor_signals["tests"])
        self.assertFalse(report.contributor_signals["contributing"])
        setup_idea = next(idea for idea in report.contribution_ideas if "setup section" in idea.title.lower())
        self.assertTrue(any("README" in reason for reason in setup_idea.chosen_because))
        self.assertTrue(any("Documentation" in area for area in report.beginner_safe_areas))

    def test_prefers_existing_test_improvements_when_tests_exist(self) -> None:
        report = analyze_repository(FIXTURES_DIR / "repo_with_tests")

        self.assertGreaterEqual(report.health_score, 50)
        test_idea = next(idea for idea in report.contribution_ideas if "sanity test" in idea.title.lower())
        self.assertTrue(any("tests" in reason.lower() for reason in test_idea.chosen_because))

    def test_handles_missing_readme_with_fallback_summary(self) -> None:
        report = analyze_repository(FIXTURES_DIR / "repo_without_readme")

        self.assertIn("No clear project summary", report.summary)
        self.assertEqual("Unknown", report.inferred_stack[0])
        self.assertEqual(3, len(report.contribution_ideas))
        self.assertTrue(all(idea.chosen_because for idea in report.contribution_ideas))


if __name__ == "__main__":
    unittest.main()
