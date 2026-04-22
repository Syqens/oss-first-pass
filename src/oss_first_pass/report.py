from __future__ import annotations

from .analyzer import RepoReport


def report_to_markdown(report: RepoReport) -> str:
    lines = [
        f"# Repository First Pass: {report.repository_name}",
        "",
        "## What the project does",
        report.summary,
        "",
        "## Contribution Readiness",
        f"- Health score: **{report.health_score}/100** ({report.health_label})",
    ]

    for signal, value in report.contributor_signals.items():
        label = signal.replace("_", " ")
        lines.append(f"- {label}: {'yes' if value else 'no'}")

    lines.extend(
        [
            "",
            "## Inferred Stack",
            f"- {', '.join(report.inferred_stack)}",
            "",
            "## How it is structured",
        ]
    )

    for item in report.structure or ["- No obvious top-level structure detected."]:
        if item.startswith("`"):
            lines.append(f"- {item}")
        else:
            lines.append(item)

    lines.extend(["", "## Where a beginner can safely contribute"])
    for area in report.beginner_safe_areas:
        lines.append(f"- {area}")

    lines.extend(["", "## Three small contribution ideas"])
    for index, idea in enumerate(report.contribution_ideas, start=1):
        lines.append(f"{index}. {idea.title}")
        lines.append(f"Why it matters: {idea.why_it_matters}")
        lines.append(f"Likely files: {', '.join(idea.likely_files)}")
        lines.append(f"Risk: {idea.risk}")

    lines.extend(["", "## Best first PR", report.best_first_pr])
    return "\n".join(lines)
