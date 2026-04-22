from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


STACK_HINTS = {
    "package.json": "Node.js",
    "bun.lockb": "Bun",
    "pyproject.toml": "Python",
    "requirements.txt": "Python",
    "Cargo.toml": "Rust",
    "go.mod": "Go",
    "pom.xml": "Java",
    "build.gradle": "Java/Kotlin",
    "build.gradle.kts": "Kotlin",
    "Gemfile": "Ruby",
    "composer.json": "PHP",
}

STRUCTURE_HINTS = {
    "src": "application source code",
    "app": "application code",
    "components": "reusable UI building blocks",
    "pages": "route-level pages or views",
    "layouts": "shared page layouts",
    "composables": "reusable app logic",
    "lib": "shared library code",
    "gfi": "scripts or backend helpers",
    "scripts": "automation and helper scripts",
    "tests": "automated tests",
    "test": "automated tests",
    "docs": "project documentation",
    "data": "generated or curated project data",
    "public": "static public assets",
    "assets": "images, styles, or supporting assets",
}

SETUP_HEADING_PATTERN = re.compile(
    r"^\s{0,3}#{1,6}\s+(installation|install|setup|getting started|development|usage|run)\b",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass
class ContributionIdea:
    title: str
    why_it_matters: str
    likely_files: list[str]
    risk: str = "low"


@dataclass
class RepoReport:
    repository_name: str
    repository_path: str
    summary: str
    inferred_stack: list[str]
    health_score: int
    health_label: str
    contributor_signals: dict[str, bool]
    structure: list[str]
    beginner_safe_areas: list[str]
    contribution_ideas: list[ContributionIdea]
    best_first_pr: str

    def to_dict(self) -> dict:
        data = asdict(self)
        data["contribution_ideas"] = [asdict(item) for item in self.contribution_ideas]
        return data


def analyze_repository(repo_path: str | Path) -> RepoReport:
    root = Path(repo_path).resolve()
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Repository path not found: {root}")

    contributor_signals = {
        "readme": _first_existing(root, ["README.md", "README.rst", "README.txt"]) is not None,
        "contributing": _first_existing(
            root,
            ["CONTRIBUTING.md", ".github/CONTRIBUTING.md", "docs/CONTRIBUTING.md"],
        )
        is not None,
        "license": _first_existing(root, ["LICENSE", "LICENSE.md", "LICENSE.txt"]) is not None,
        "code_of_conduct": _first_existing(
            root,
            ["CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"],
        )
        is not None,
        "issue_templates": (root / ".github" / "ISSUE_TEMPLATE").exists(),
        "pr_template": _first_existing(
            root,
            [".github/PULL_REQUEST_TEMPLATE.md", "PULL_REQUEST_TEMPLATE.md"],
        )
        is not None,
        "ci_workflows": (root / ".github" / "workflows").exists(),
        "tests": _has_tests(root),
        "docs_dir": (root / "docs").exists(),
    }

    readme_path = _first_existing(root, ["README.md", "README.rst", "README.txt"])
    readme_text = _read_text(readme_path) if readme_path else ""
    summary = _summarize_project(readme_text) or "No clear project summary found in the README."
    inferred_stack = _detect_stack(root)
    structure = _describe_structure(root)
    beginner_safe_areas = _beginner_safe_areas(root, contributor_signals, inferred_stack)
    contribution_ideas = _build_contribution_ideas(root, contributor_signals, readme_text, inferred_stack)
    best_first_pr = contribution_ideas[0].title if contribution_ideas else "Review the README and tests for the smallest safe cleanup."

    health_score = _health_score(contributor_signals, readme_text)
    health_label = _health_label(health_score)

    return RepoReport(
        repository_name=root.name,
        repository_path=str(root),
        summary=summary,
        inferred_stack=inferred_stack,
        health_score=health_score,
        health_label=health_label,
        contributor_signals=contributor_signals,
        structure=structure,
        beginner_safe_areas=beginner_safe_areas,
        contribution_ideas=contribution_ideas[:3],
        best_first_pr=best_first_pr,
    )


def report_to_json(report: RepoReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def _first_existing(root: Path, candidates: list[str]) -> Path | None:
    for candidate in candidates:
        candidate_path = root / candidate
        if candidate_path.exists():
            return candidate_path
    return None


def _read_text(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def _summarize_project(readme_text: str) -> str:
    lines = [line.strip() for line in readme_text.splitlines()]
    cleaned: list[str] = []
    for line in lines:
        if not line:
            if cleaned:
                break
            continue
        if line.startswith("#") or line.startswith("!["):
            continue
        if line.startswith("<") or line.endswith(">"):
            continue
        if line.lower().startswith("welcome"):
            continue
        if line.startswith("[!") or line.startswith(">"):
            continue
        cleaned.append(line)
    return " ".join(cleaned[:3]).strip()


def _detect_stack(root: Path) -> list[str]:
    detected = [label for filename, label in STACK_HINTS.items() if (root / filename).exists()]
    return detected or ["Unknown"]


def _has_tests(root: Path) -> bool:
    if any((root / name).exists() for name in ("tests", "test")):
        return True

    patterns = (
        "**/test_*.py",
        "**/*_test.py",
        "**/*.spec.ts",
        "**/*.test.ts",
        "**/*.spec.js",
        "**/*.test.js",
    )
    for pattern in patterns:
        if any(root.glob(pattern)):
            return True
    return False


def _describe_structure(root: Path) -> list[str]:
    descriptions = []
    for child in sorted(root.iterdir(), key=lambda item: item.name.lower()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if child.name in STRUCTURE_HINTS:
            descriptions.append(f"`{child.name}`: {STRUCTURE_HINTS[child.name]}")
        elif len(descriptions) < 6:
            descriptions.append(f"`{child.name}`: project directory")
        if len(descriptions) >= 8:
            break
    return descriptions


def _beginner_safe_areas(root: Path, signals: dict[str, bool], stack: list[str]) -> list[str]:
    areas: list[str] = []
    if signals["readme"] or signals["contributing"] or signals["docs_dir"]:
        areas.append("Documentation and contributor guidance")
    if signals["tests"]:
        areas.append("Small tests and validation checks")
    if any((root / name).exists() for name in ("components", "pages", "layouts", "composables")):
        areas.append("Isolated UI improvements in single components or pages")
    if any((root / name).exists() for name in ("scripts", "gfi", "data")):
        areas.append("Small tooling or data-quality fixes")
    if not areas:
        areas.append("README improvements and lightweight project hygiene")
    return areas[:4]


def _build_contribution_ideas(
    root: Path,
    signals: dict[str, bool],
    readme_text: str,
    stack: list[str],
) -> list[ContributionIdea]:
    ideas: list[ContributionIdea] = []
    readme_has_setup = bool(SETUP_HEADING_PATTERN.search(readme_text))

    if not signals["contributing"]:
        ideas.append(
            ContributionIdea(
                title="Add a contributor guide with setup and PR expectations",
                why_it_matters="A clear CONTRIBUTING guide reduces friction for first-time contributors and leads to cleaner pull requests.",
                likely_files=["CONTRIBUTING.md", ".github/CONTRIBUTING.md"],
            )
        )

    if signals["readme"] and not readme_has_setup:
        ideas.append(
            ContributionIdea(
                title="Add a clearer local setup section to the README",
                why_it_matters="Strong setup instructions are one of the fastest ways to help new contributors become productive.",
                likely_files=["README.md"],
            )
        )

    if signals["tests"]:
        test_target = "tests/" if (root / "tests").exists() else "test/"
        ideas.append(
            ContributionIdea(
                title="Add or tighten a small sanity test around one helper path",
                why_it_matters="Small tests are usually low-risk and help maintainers trust future changes more quickly.",
                likely_files=[test_target],
            )
        )
    else:
        ideas.append(
            ContributionIdea(
                title="Add a lightweight smoke test for one critical path",
                why_it_matters="A single smoke test can catch obvious regressions and improve contributor confidence without a large refactor.",
                likely_files=["tests/", "test/"],
            )
        )

    if not signals["issue_templates"]:
        ideas.append(
            ContributionIdea(
                title="Add basic issue templates for bug reports and feature requests",
                why_it_matters="Templates improve issue quality and make triage easier for maintainers.",
                likely_files=[".github/ISSUE_TEMPLATE/"],
            )
        )

    if not signals["pr_template"]:
        ideas.append(
            ContributionIdea(
                title="Add a lightweight pull request template",
                why_it_matters="A PR template nudges contributors to explain scope, testing, and rationale up front.",
                likely_files=[".github/PULL_REQUEST_TEMPLATE.md"],
            )
        )

    if not signals["ci_workflows"] and ("Node.js" in stack or "Python" in stack):
        ideas.append(
            ContributionIdea(
                title="Add a minimal CI smoke workflow",
                why_it_matters="A basic workflow for linting or tests gives contributors fast feedback before review.",
                likely_files=[".github/workflows/"],
                risk="medium",
            )
        )

    if signals["readme"] and signals["contributing"] and signals["tests"]:
        ideas.append(
            ContributionIdea(
                title="Document how to run the existing tests locally",
                why_it_matters="Matching the documented developer workflow to the real test commands lowers the cost of contribution.",
                likely_files=["README.md", "CONTRIBUTING.md"],
            )
        )

    while len(ideas) < 3:
        ideas.append(
            ContributionIdea(
                title="Tighten a small documentation gap in the main setup flow",
                why_it_matters="Tiny documentation fixes are low-risk and often get reviewed quickly when they remove real confusion.",
                likely_files=["README.md"],
            )
        )

    return _dedupe_ideas(ideas)


def _dedupe_ideas(ideas: list[ContributionIdea]) -> list[ContributionIdea]:
    seen: set[str] = set()
    unique: list[ContributionIdea] = []
    for idea in ideas:
        key = idea.title.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(idea)
    return unique


def _health_score(signals: dict[str, bool], readme_text: str) -> int:
    score = 0
    weights = {
        "readme": 20,
        "contributing": 15,
        "license": 10,
        "code_of_conduct": 10,
        "issue_templates": 10,
        "pr_template": 5,
        "ci_workflows": 10,
        "tests": 10,
        "docs_dir": 5,
    }
    for key, weight in weights.items():
        if signals[key]:
            score += weight
    if SETUP_HEADING_PATTERN.search(readme_text):
        score += 5
    return min(score, 100)


def _health_label(score: int) -> str:
    if score >= 80:
        return "strong"
    if score >= 60:
        return "promising"
    if score >= 40:
        return "mixed"
    return "rough"
