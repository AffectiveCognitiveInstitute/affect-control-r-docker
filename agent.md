# Agent Instructions

## Objective
Create a production-ready containerized runtime for R that supports ACT and BayesACT workflows, and expose a minimal Python API on top. Add CI automation to build and publish the image.

## Deliverables
- A Dockerfile (and any supporting build scripts) that:
  - Installs a stable R runtime and required OS-level dependencies.
  - Installs the R packages required for ACT and BayesACT usage.
  - Produces a runnable image with sensible defaults.
- A minimal Python API service that:
  - Provides a small, well-defined interface for invoking core R/BayesACT functionality.
  - Includes basic request validation and clear error messages.
  - Can run in the same container or as a companion container (prefer simplest).
- A GitHub Actions workflow that:
  - Builds the Docker image on pushes and tags.
  - Runs lightweight checks (lint/unit/smoke test) before publishing.
  - Pushes the image to a registry (default: GitHub Container Registry).
- Minimal documentation updates:
  - How to build and run locally.
  - How to call the Python API (1–2 examples).
  - What tags/images are published by CI.

## Operating Principles
- Prefer reproducibility and deterministic builds (pin versions where practical).
- Keep the API minimal: implement only essential endpoints, avoid overengineering.
- Favor secure defaults (non-root runtime where feasible; minimal OS packages).
- Ensure changes are easy to review (small commits, clear diffs, clear naming).

## Implementation Workflow
1. Inspect the repository structure and existing tooling (if any).
2. Draft an implementation plan (files to add/modify, build approach, CI approach).
3. Implement in small increments:
   - Container build first (R + packages).
   - Add API scaffold and one end-to-end “smoke” path.
   - Add CI build/test.
4. Validate locally:
   - Image builds cleanly.
   - R can load required packages.
   - API can execute at least one representative call.
5. Finalize docs and ensure CI passes.

## Container Requirements
- Base image: use a standard, maintained Linux distribution or a well-known R base image.
- Package installation:
  - Install required system libraries for compiling R packages when needed.
  - Install R dependencies in a way that supports caching and fast rebuilds.
- Runtime:
  - Provide a clear container entrypoint (API server or documented command).
  - Expose only required ports.
  - Use environment variables for configuration (host/port/log level).

## Python API Requirements
- Use a lightweight framework suitable for container deployment.
- Provide a small surface area, e.g.:
  - Health endpoint
  - One endpoint to run a defined R operation (or wrapper command)
- Bridge to R via a robust mechanism (one of):
  - Subprocess calls to `Rscript` with well-defined inputs/outputs, or
  - An R-to-Python bridge library if it is stable and justified
- Return structured JSON responses and clear errors.
- Include a minimal test or smoke script that can be run in CI.

## GitHub Actions Requirements
- Build on:
  - Pull requests (build + tests only)
  - Main branch pushes (build + tests)
  - Version tags/releases (build + tests + push)
- Push images to a registry using standard GitHub authentication.
- Tagging strategy:
  - `latest` for main branch (if desired)
  - semantic version tags for releases
  - commit SHA tag for traceability (optional)
- Keep workflow readable and maintainable; avoid unnecessary steps.

## Quality Gates
- The image must build without manual intervention.
- R must be able to load required packages in a non-interactive session.
- The API must start reliably and respond to a health check.
- CI must run a minimal smoke validation before publishing.

## Constraints and Assumptions
- Do not include secrets in the repo.
- Do not introduce large, unrelated dependencies.
- Keep the repository structure simple and conventional.
- If a required package is not available from CRAN, install from a reputable upstream source and document it.

## Communication
When making decisions that affect usability (entrypoint choice, API shape, tagging), document the rationale briefly in the README or in PR notes.
