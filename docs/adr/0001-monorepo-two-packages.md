# ADR-0001: Monorepo with two packages, and ServeConfig as the contract

- **Status:** Accepted
- **Date:** 2026-10-02

## Context

The project has two deliverables with very different audiences and dependencies:

1. A **calculator** that anyone can `pip install` to get a serving configuration
   (quantization, context length, parallel requests, TTFT/TPOT estimates) for a
   model on their hardware. It must install in seconds, so it cannot depend on
   PyTorch or CUDA.
2. An **inference server** (FastAPI) that ships as a Docker image and loads the
   model with heavy dependencies (torch, transformers).

The server must run exactly the configuration the calculator produces. If the two
sides define that configuration separately, they will drift apart.

## Decision

- One repository, organized as a **uv workspace** with two packages:
  - `packages/infercalc`: the calculator, published to PyPI. Torch-free.
  - `packages/inferserve`: the server, published as a Docker image.
- The workspace shares **one lockfile (`uv.lock`) and one `.venv`**. `inferserve`
  depends on `infercalc` through a workspace source, so local changes to the
  calculator are picked up immediately.
- **`ServeConfig` is the contract.** It is defined once, in `infercalc.schemas`,
  and carries a `schema_version`. The server imports it instead of redefining it.
- `inferserve` may import only `infercalc.schemas` and `infercalc`'s public API,
  never its internal modules.

## Consequences

- **Good:** one source of truth for the config; a single `uv sync` sets up
  everything; one CI pipeline tests both packages together; changes that touch
  both sides land in one PR.
- **Good:** the container can run the calculator itself ("auto" startup mode),
  because the calculator is already a dependency.
- **Cost:** `infercalc` must keep its dependencies light forever, since every
  server image installs it too.
- **Cost:** the calculator and server images can be released at different times,
  so the server must check `schema_version` at startup and refuse configs it
  does not understand.
- **Cost:** some tooling needs workspace-aware settings (pytest import mode,
  `mypy -p` per package, `uv sync --all-packages`).
