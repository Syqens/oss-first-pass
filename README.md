# OSS First Pass

`OSS First Pass` is a small CLI that helps new contributors decide whether an open-source repository is a good first contribution target.

It scans a local repository and generates a contributor-focused report:

- what the project appears to do
- how it is structured
- how contributor-friendly it looks
- where a beginner can safely contribute
- three small contribution ideas
- the best first pull request

This solves a real problem for new contributors: spending too much time guessing whether a repository is healthy, approachable, and worth your first PR.

## Why this project matters

A lot of beginners open a repository and immediately hit the same questions:

- Where is the actual code?
- Is there a `CONTRIBUTING.md`?
- Are tests already set up?
- Is documentation strong enough to follow?
- What is a realistic first change that won't get rejected?

`OSS First Pass` turns that first repo scan into a repeatable, fast checklist.

## Features

- analyzes local repositories with no external API dependency
- detects common contributor signals such as:
  - `README`
  - `CONTRIBUTING`
  - `LICENSE`
  - issue templates
  - PR templates
  - CI workflows
  - test directories
- infers likely stack from common project files
- summarizes top-level structure
- generates three small, low-risk contribution ideas
- prints either Markdown or JSON output

## Quick Start

From the project root:

```powershell
C:\Users\jumax\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m oss_first_pass ..\gfi-next
```

Write the report to a file:

```powershell
C:\Users\jumax\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m oss_first_pass ..\gfi-next --output report.md
```

JSON output:

```powershell
C:\Users\jumax\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m oss_first_pass ..\gfi-next --format json
```

## Example Output

A real generated sample report from this workspace is included in [example-report.md](example-report.md).

```md
# Repository First Pass: good-first-issue

## What the project does
Good First Issue curates easy pickings from popular open-source projects so new contributors can get started quickly.

## How it is structured
- `components`: reusable UI building blocks
- `pages`: route-level views
- `gfi`: Python scripts for data collection and validation
- `data`: generated or curated repository metadata

## Beginner-safe areas
- Documentation and contributor guidance
- Small UI improvements in isolated components
- Sanity tests for scripts and data validation

## Three small contribution ideas
1. Improve data sanity tests in `gfi/test_data.py`
2. Add a clearer "local setup" section to `README.md`
3. Add a lightweight issue template for bug reports in `.github/ISSUE_TEMPLATE`

## Best first PR
Improve `gfi/test_data.py` with clearer assertions and better duplicate-entry feedback.
```

## Project Layout

```text
oss-first-pass/
  README.md
  pyproject.toml
  src/oss_first_pass/
    __init__.py
    __main__.py
    analyzer.py
    cli.py
    report.py
  tests/
    test_analyzer.py
```

## Development

Run the test suite:

```powershell
C:\Users\jumax\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover -s tests -v
```

Run the CLI against the current directory:

```powershell
$env:PYTHONPATH='src'; C:\Users\jumax\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m oss_first_pass .
```

## Portfolio Value

This is a strong portfolio mini project because it is:

- focused on a real workflow problem
- small enough to finish cleanly
- easy to demo on real repositories
- directly connected to open-source contribution work
- structured like a real tool, not a toy app
