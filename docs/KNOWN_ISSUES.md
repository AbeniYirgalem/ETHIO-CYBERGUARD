# Known Issues and Limitations

Status as of 24 October 2026. Each item links to where it is tracked. Please update this file when an item is fixed.

## Open issues

| # | Issue | Status | Tracked in |
|---|-------|--------|------------|
| 1 | CI job `backend-checks` fails on Python 3.10. `requirements.txt` requires `sqlalchemy>=2.1.3`, and all SQLAlchemy 2.1.x releases require Python 3.11 or newer. | Cause confirmed from the CI log. Fix proposed: move CI and Dockerfiles to a newer Python. | Issue #55 |
| 2 | The API Dockerfiles (`apps/api/Dockerfile` and `infrastructure/docker/Dockerfile.api`) use `python:3.10-slim`, which has the same problem as item 1. | Likely cause of the `docker-checks` failure, not yet confirmed. | Issue #55 |
| 3 | The documented minimum Python version (3.10+) is wrong. The dependencies need Python 3.11+. This appears in README.md, CONTRIBUTING.md, docs/installation.md and AGENTS.md. | Documentation fix pending. | Issue #55 |
| 4 | The live demo link in the README returned a GitHub Pages 404. The `gh-pages` branch contains the built site, so the cause is the Pages source setting, which needs a repository admin. | Waiting for an admin to check Settings > Pages. | (add the issue number here) |
| 5 | The `dependency-audit` CI job fails. | Cause not yet investigated. | PR #52 checks |

## Limitations

- **Demo mode uses simulated data.** The hosted demo generates events in the browser. Real ingestion needs the full stack (API, database, collectors) running locally or in Docker.
- **Default database.** Without PostgreSQL configured, the API falls back to SQLite, which is only suitable for single-node prototypes.
- **Optional AI keys.** The AI features need an API key or a local model. Without one, they run in a limited or fallback mode.
- **Unverified numbers.** Some README figures (test count, events-per-second throughput) have not been re-verified by every team member. Pull request #52 also proposes a different test count. Please confirm any number by running the tests or benchmark before quoting it.

## Security notes

- `.env.example` previously contained example passwords and secret keys. They were replaced with `CHANGE_ME` placeholders (PR #53), but **the old values remain in the Git history**. Anyone who ever used them must rotate them.
- Never commit a real `.env` file. Generate every secret yourself:
  `python -c "import secrets; print(secrets.token_urlsafe(32))"`

## How to report a problem

Open a GitHub issue and include the exact error message, what you ran, and your Python and Node versions.
