<!--
Sync Impact Report
Version change: unversioned scaffold -> 1.0.0
Modified principles:
- Principle 1 placeholder -> I. Simplicity and Stack Discipline
- Principle 2 placeholder -> II. Validate All User Input
- Principle 3 placeholder -> III. Automated Tests for Every Feature
- Principle 4 placeholder -> IV. Specification-Driven, Verifiable Changes
- Principle 5 placeholder -> V. Minimal Dependencies and Maintainable Data
Added sections: Technology and Security Constraints; Development Workflow
Removed sections: None
Follow-up TODO: Confirm and replace the unknown original ratification date.
-->
# Finance Tracker Constitution

## Core Principles

### I. Simplicity and Stack Discipline
The backend MUST use Python 3.15, FastAPI, and SQLite. The frontend MUST use HTML and
plain JavaScript without a frontend framework. Implementations MUST prefer the simplest
design that satisfies the specification; additional frameworks or architectural layers
require a documented need.

### II. Validate All User Input
Every user-supplied value MUST be validated on the server against its required type,
format, range, and domain rules before use or persistence. Browser-side checks MAY
improve usability but MUST NOT replace server-side validation. Invalid input MUST be
rejected clearly, and database queries MUST use bound parameters.

### III. Automated Tests for Every Feature
Every feature MUST have automated pytest tests before it is considered complete. Tests
MUST verify its specified behavior and relevant invalid-input and failure cases. Changes
MUST pass the automated test suite before merge or release.

### IV. Specification-Driven, Verifiable Changes
Each feature MUST have written requirements and observable acceptance criteria before
implementation. Tests MUST provide evidence for those criteria. When behavior changes,
the specification and its tests MUST be updated together so they remain the source of
truth for the feature.

### V. Minimal Dependencies and Maintainable Data
The project MUST keep dependencies and implementation complexity to the minimum needed
by approved requirements. SQLite schema changes MUST preserve stored data or document
their migration. Dependencies MUST be checked with pip-audit, and identified risks MUST
be resolved or explicitly reviewed before release.

## Technology and Security Constraints

The application MUST use Python 3.15, FastAPI, and SQLite. Its browser interface MUST be
implemented with HTML and plain JavaScript, without a frontend framework. The backend
MUST treat all incoming values as untrusted, validate them before processing, and use
parameterized database access. Dependencies MUST remain lean and be audited with
pip-audit.

## Development Workflow

Feature work MUST start from documented requirements and acceptance criteria. Pytest
coverage MUST include each feature's expected behavior and relevant invalid-input,
error, and persistence behavior. The full automated test suite and dependency audit
MUST be run before release. Review MUST verify compliance with this constitution, and
any justified exception MUST be documented with its scope and rationale.

## Governance

This constitution governs project specifications, implementation, tests, and reviews.
Amendments MUST be proposed as explicit changes to this file, state their rationale and
impact, and receive project-owner approval before adoption. Changes MUST preserve the
constitution's heading structure and update the version and amendment date.

Versioning follows Semantic Versioning: MAJOR for incompatible governance changes,
MINOR for new principles or materially expanded requirements, and PATCH for
clarifications that do not change obligations. Every specification, implementation,
and release review MUST check compliance with this constitution.

**Version**: 1.0.0 | **Ratified**: 22.10.2026: original date unknown | **Last Amended**: 2026-10-22
