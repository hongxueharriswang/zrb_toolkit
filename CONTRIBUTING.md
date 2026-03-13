

# Contributing to ZRB Toolkit

Thank you for your interest in improving the **ZRB (Zoned Role‑Based) Python Toolkit**. This project implements a complete ZRB framework across core models, storage, access engine, constraints, web integrations, CLI, validation, and examples.

This guide explains how to set up your environment, propose changes, write and run tests, follow style and design conventions, and submit pull requests (PRs). Please read it end‑to‑end before contributing.

***

## Table of Contents

1.  code-of-conduct
2.  project-scope--architecture
3.  good-first-issues--ways-to-help
4.  development-environment
5.  branching--commit-conventions
6.  coding-standards
7.  testing-strategy
8.  documentation
9.  database--migrations-storage
10. performance--benchmarks
11. security--responsible-disclosure
12. pr-checklist
13. review--merge-process
14. release-notes--changelog
15. license

***

## Code of Conduct

By participating, you agree to uphold a respectful, welcoming environment for everyone—maintainers, contributors, and users. Be kind, constructive, and collaborative. If you witness or experience unacceptable behavior, please open a confidential issue or email a maintainer.

***

## Project Scope & Architecture

ZRB Toolkit delivers a modular implementation of the **Zoned Role-Based** access model:

*   **Core (`zrb.core`)**: Pydantic models and type definitions (Users, Zones, Roles, Operations, Gamma mappings, Constraints).
*   **Storage (`zrb.storage`)**: Pluggable persistence via `Storage` interface; SQLAlchemy implementation provided.
*   **Engine (`zrb.engine`)**: Inheritance resolution, permission caching, and access decisions.
*   **Constraints (`zrb.constraints`)**: Evaluator base class, registry, and built-in evaluators (SoD, Temporal, Attribute, Context).
*   **Web (`zrb.web`)**: Django and Flask decorators/middleware.
*   **CLI (`zrb.cli`)**: `click`-based commands (init DB, import config, validate, CRUD).
*   **Validation (`zrb.validation`)**: Consistency checks across zones/roles/gamma/constraints.
*   **Utils (`zrb.utils`)**: Tree/graph helpers.
*   **Examples (`examples/`)**: End-to-end Django/Flask demos (YAML config, zone mapping, context evaluation).

> **Design goals**: correctness first, then clarity, testability, and performance; public APIs documented; private helpers isolated; clean separation of concerns between layers.

***

## Good First Issues & Ways to Help

*   **Docs**: Clarify API docstrings; add quickstarts; extend examples with new scenarios.
*   **Tests**: Add unit tests for corner cases (e.g., constraint priority, partial gamma inheritance, cache invalidation).
*   **Engine**: Implement missing methods in `InheritanceResolver`, `PermissionCache`, `AccessEngine` with tests.
*   **Storage**: Add CRUD tests; explore additional storage backends by implementing `Storage` interface.
*   **Constraints**: Contribute new evaluator types; improve evaluator coverage and benchmarks.
*   **Web**: Harden Django/Flask decorators, zone resolution, and error handling; add integration tests.
*   **CLI**: Expand import/validate commands; better messages and exit codes.

Look for issues labeled **good first issue** or **help wanted**. If unsure, open a short proposal issue before coding.

***

## Development Environment

### 1) Prerequisites

*   Python **3.10+** (project uses modern typing and Pydantic)
*   `make` (recommended) or run equivalent commands manually
*   SQLite (default for local dev) or PostgreSQL if desired

### 2) Clone & Create a Virtual Environment

```bash
git clone https://github.com/hongxueharriswang/zrb_toolkit.git
cd zrb_toolkit
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3) Install Dependencies (editable)

```bash
pip install -U pip
pip install -e ".[dev]"   # expects extras in setup.cfg/pyproject.toml (dev: pytest, coverage, black, isort, mypy, flake8, etc.)
```

> If dev extras aren’t defined yet, install individually:

```bash
pip install pydantic sqlalchemy click pytest pytest-cov black isort mypy flake8 types-PyYAML
```

### 4) Pre-commit Hooks (recommended)

```bash
pip install pre-commit
pre-commit install
# runs on each commit: black, isort, flake8, mypy (optional), trailing whitespace, EOF fixes
```

***

## Branching & Commit Conventions

*   Base branch: **`main`** (always releasable).
*   Feature branches: `feat/<topic>`, fixes: `fix/<topic>`, docs: `docs/<topic>`, tests: `test/<topic>`, chore: `chore/<topic>`.

**Conventional Commits** are encouraged:

    feat(engine): add cache invalidation by zone
    fix(storage): correct session lifecycle on constraint updates
    docs(readme): clarify Django decorator usage
    test(constraints): SoD evaluator conflict-priority edge cases

Include an issue reference when applicable: `fix: ... (closes #123)`.

***

## Coding Standards

*   **Typing**: Use precise type hints; enable `from __future__ import annotations` where appropriate.
*   **Style**:
    *   Formatter: **black**
    *   Import order: **isort**
    *   Lint: **flake8** (or ruff if configured), docstring checks encouraged
    *   Static types: **mypy** (strict on `zrb.core`, `zrb.engine`, `zrb.storage`; reasonable elsewhere)
*   **Docstrings**: Public classes and functions require docstrings (Google or NumPy style). Keep examples minimal and correct.
*   **Public API**: Avoid breaking changes; if necessary, deprecate with clear notes and tests.
*   **Errors & Returns**:
    *   `AccessEngine.decide(...)` returns `bool`; do not raise on access checks.
    *   Storage layer should raise precise exceptions for integrity errors and translate ORM errors where needed.
*   **Configuration**: Use environment variables (e.g., `ZRB_DATABASE_URL`) with safe defaults.
*   **Security**: Treat constraint logic and permission resolution as security-sensitive (avoid silent fallbacks; log denials when safe).

***

## Testing Strategy

We aim for **high coverage** in critical paths (engine, constraints, storage). Use **pytest**.

### Run Tests

```bash
pytest
pytest -q tests/engine/test_access_engine.py::test_decide_basic
```

### Coverage

```bash
pytest --cov=zrb --cov-report=term-missing
```

### Test Organization

    tests/
      core/
      storage/
      engine/
      constraints/
      web/
      cli/
      validation/
      examples/  # optional smoke tests

### What to Test

*   **Engine**:
    *   Transitive role inheritance within zone
    *   Gamma mapping aggregation, weights/priority behavior
    *   Cache TTL & invalidation (`PermissionCache`)
    *   Negative vs. positive constraints; priority/override rules
*   **Constraints**:
    *   SoD (role conflicts, self-action denies)
    *   Temporal (time windows; use injected times via context)
    *   Attribute (operators, thresholds)
    *   Context (key/value matching, partial contexts)
*   **Storage (SQLAlchemy)**:
    *   CRUD for all models
    *   Referential integrity and transaction boundaries
    *   Pagination/listing when applicable
*   **Web**:
    *   Django/Flask decorators behave as expected (403 on deny)
    *   Zone resolution stubs are configurable/overridable
*   **CLI**:
    *   `init`, `import_config`, `validate` commands with temp DBs and sample YAML

> Use factories/fixtures for quickly creating Users/Zones/Roles/Operations and in-memory SQLite for speed.

***

## Documentation

*   **Docstrings**: Keep the specification as the source of truth; ensure code docstrings match behaviors.
*   **User Docs**: Add or update READMEs in:
    *   Root `README.md`: quickstart, features, links
    *   `examples/*/README.md`: how to run examples
*   **API Docs**: If Sphinx/MkDocs is enabled, place docs in `docs/` and keep reference pages generated from docstrings.
*   **Diagrams**: Architecture and flow diagrams are welcome (keep them tool-agnostic and include sources).

***

## Database & Migrations (Storage)

*   Default dev DB: **SQLite** (`sqlite:///zrb.db`) for simplicity.
*   For production examples, support **PostgreSQL** by setting `ZRB_DATABASE_URL`.

If/when migrations are introduced (e.g., **Alembic**):

*   Migration scripts live under `alembic/`.
*   Each schema-affecting change requires a migration and backward-compatible data upgrade path.
*   Tests must pass for upgrades/downgrades (when enabled).

***

## Performance & Benchmarks

Critical paths:

*   Permission computation in `InheritanceResolver`
*   Cache behavior in `PermissionCache`
*   Constraint evaluation in the hot path of `AccessEngine.decide`

Guidelines:

*   Add micro-benchmarks for hot loops (e.g., transitive closure over roles/zones).
*   Prefer set operations and memoization; avoid N+1 storage calls.
*   Validate cache TTL/hit rates; ensure invalidation triggers on writes (role/zone/constraint updates).

***

## Security & Responsible Disclosure

*   Treat access decisions as **security-critical**. Avoid “fail open” behaviors.
*   For potential vulnerabilities (logic bypasses, privilege escalation, injection in configurables), do **not** open a public issue with details.  
    Instead, email the maintainers (see repo profile) with a minimal, reproducible report.
*   We will acknowledge reports and coordinate fixes and disclosure timelines.

***

## PR Checklist

Before opening a PR, please ensure:

*   [ ] Feature/bugfix has an associated issue or a short design proposal in the PR description.
*   [ ] Code is covered by **unit tests** (and integration tests where appropriate).
*   [ ] **`pytest`** passes locally; coverage does not regress in critical modules.
*   [ ] Code is formatted (**black**), imports sorted (**isort**), **flake8/ruff** pass, and **mypy** passes for touched packages.
*   [ ] Public APIs documented; docstrings updated; docs/READMEs adjusted as needed.
*   [ ] No secrets or credentials committed.
*   [ ] For storage or schema changes, migrations and docs are included.
*   [ ] For performance-sensitive changes, benchmarks or notes are provided.

***

## Review & Merge Process

1.  **Automated checks** run (CI: lint, type-check, tests, coverage).
2.  **Code review** by maintainers:
    *   Correctness, clarity, tests, docs, and backward compatibility.
    *   Security and performance implications for engine/constraints/storage.
3.  Changes requested (if any) → contributor updates PR.
4.  **Squash merge** with a clean, descriptive message (maintainer may edit for changelog clarity).

***

## Release Notes & Changelog

*   We maintain a `CHANGELOG.md` with notable changes grouped under versions.
*   Keep entries user-facing (features, fixes, breaking changes, deprecations, migrations).
*   PR titles and descriptions help generate accurate notes.

***

## License

By contributing, you agree that your contributions will be licensed under the repository’s license (see `LICENSE` file).

***

## Module-Specific Guidelines (Quick Reference)

*   **`zrb.core`**: Keep Pydantic models minimal and immutable where possible; validate inputs; avoid business logic beyond model-level helpers.
*   **`zrb.storage`**: Interact only through the `Storage` interface from other layers; ensure transaction safety; provide clear exception boundaries.
*   **`zrb.engine`**:
    *   `InheritanceResolver`: Cache transitive role/zone computations; avoid cycles; ensure deterministic priority resolution.
    *   `PermissionCache`: Honor TTL; expose precise invalidation methods (by role, by zone).
    *   `AccessEngine`: Enforce step order—user active → roles → permissions → constraints (negative denies, positive requires) → decision.
*   **`zrb.constraints`**: Evaluators must be **pure** functions w\.r.t. inputs; rely on `context` for time/req attributes; document required keys.
*   **`zrb.web`**: Keep framework-specific logic thin; do not embed business logic; decorators should return standard HTTP 403 on deny.
*   **`zrb.cli`**: Clear help texts and exit codes; avoid breaking changes to command flags; support YAML imports with validation.
*   **`zrb.validation`**: Emphasize structural integrity (no cycles, valid references, non-conflicting mappings); fast feedback for CI.

***

## Running Examples Locally

Each example under `examples/` shows end-to-end usage:

```bash
# Initialize DB
export ZRB_DATABASE_URL="sqlite:///zrb.db"
zrb-cli init  # or: python -m zrb.cli init

# Load sample config
zrb-cli import_config examples/university/config.yaml

# Start the example app (see the example's README)
```

If Django/Flask examples are included, follow their `README.md` for environment variables, zone mapping (subdomain/header), and running the dev server.

***

**Thank you for contributing to ZRB Toolkit!** Your expertise helps make secure, maintainable access control easier for everyone. If you have questions or want to float an idea before coding, open an issue with the tag **discussion**.
