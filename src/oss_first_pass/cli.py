from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .analyzer import analyze_repository, report_to_json
from .report import report_to_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oss-first-pass",
        description="Audit a local repository and suggest a realistic first contribution path.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Path to the repository to analyze.")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format.",
    )
    parser.add_argument(
        "--output",
        help="Optional file path to write the report to.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = build_parser()
    args = parser.parse_args(argv)

    report = analyze_repository(args.path)
    output = report_to_json(report) if args.format == "json" else report_to_markdown(report)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output, encoding="utf-8")
    else:
        print(output)

    return 0
