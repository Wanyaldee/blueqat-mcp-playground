---
name: using-blueqat-mcp
description: Use when connected to the blueqat MCP server and asked to solve a problem with its quantum tools (run_circuit, run_qaoa, run_vqe, submit_hardware_job, verify_run, etc.) — covers which tool fits which problem shape, the safe call sequence for simulator vs. real-hardware (paid, non-refundable) jobs, and how to judge whether the result is an actual quantum advantage or just a technique demonstration.
---

# Using blueqat MCP

## Overview

Each blueqat MCP tool's own description already documents its parameters
well (bit ordering, tier caps, safety gates). What it doesn't tell you is
which tool to reach for given a problem's *shape*, what order to call tools
in, or whether the result is worth calling a "quantum" win. This skill
covers that layer.

## Problem Shape → Tool

| Problem shape | Recommended path | Notes |
|---|---|---|
| Pick the best subset/combination (routing, portfolio, budget matching, scheduling, frequency/graph coloring, MaxCut-style pairing) | Encode as a QUBO (minimize form) → `run_qaoa` | Start `steps`/`p` at 1-2; raise `n_starts` only if results look unstable (both are tier-capped — see below). Always pass or record `seed` for reproducibility. |
| Ground-state / lowest-energy state of a physical system (Ising models, toy Hamiltonians, an entry point for real molecular Hamiltonians) | Build the Hamiltonian as Pauli terms → `run_vqe` | Same steps/`n_starts` caveats as QAOA. |
| Unstructured search with a known "is this the answer?" test | `run_circuit` with a hand-built oracle (no dedicated Grover tool exists) | Quadratic speedup is asymptotic; a small toy circuit only demonstrates the algorithm, not a wall-clock win. |
| Provably fair / auditable randomness (lottery draws, key generation, audited Monte Carlo seeds) | `run_circuit` with only `h` gates, `output: "counts"`, then `verify_run` | The value here is *unpredictability + third-party verifiability* via the returned `run_id`, not speed. |
| State-prep / entanglement demo, teaching, sanity-checking a gate list | `run_circuit` (`counts`/`amplitude`/`statevector`/`expectation`) | Use `draw_circuit` and `circuit_info` first to catch mistakes before spending shots. |

## Safe Call Sequence

1. **Before designing**: call `sdk_info` — qubit/shot/gate/step caps differ
   by tier and change over time; don't assume prior numbers still hold.
2. **Before running**: `draw_circuit` / `circuit_info` to sanity-check the
   gate list. Exceeding a tier cap (e.g. `n_starts` above the tier's limit)
   raises `CircuitBuildError` — that's an enforced limit, not a bug to work
   around.
3. **Simulator runs** (`run_circuit`, `run_qaoa`, `run_vqe`): free, no
   confirmation needed.
4. **Hardware runs** — only when the user explicitly wants real execution,
   since it costs real, non-refundable money:
   - `list_hardware_qpus` → `get_qpu_next_window` (a real QPU has scheduled
     uptime, not always-on; a job can queue for a while).
   - Optionally `get_hardware_calibration` to check current error rates.
   - `get_pricing` / `my_usage` for cost awareness.
   - `submit_hardware_job` **with `confirm=true` only after the user has
     explicitly agreed** — this is the tool's own safety gate, and jobs
     cannot be canceled or refunded once submitted.
   - Poll `get_hardware_job_status` → `get_hardware_job_result`.
   - `verify_run` on the result so the execution can be independently
     confirmed.

## Is It Actually a Quantum Advantage?

Tool schemas won't stop you from presenting a run as a performance win it
isn't. Ask before claiming one:

- **Does the problem actually need it?** A QUBO with ≲25-30 variables is
  brute-forceable classically; larger ones are usually well handled by
  classical heuristics (simulated annealing, OR-tools, etc.). If a classical
  solver would match or beat the result for free and faster, the run is a
  **technique demonstration**, not an advantage — say so.
- **QAOA/VQE are NISQ-era heuristics with no proven general speedup** over
  the best classical heuristics at practically reachable sizes, and real
  hardware noise degrades solution quality further versus the noiseless
  simulator. Never assert "this beat classical" without actually
  benchmarking against a classical solver on the same instance.
- **Grover's quadratic speedup is real but asymptotic** — it needs large,
  fault-tolerant hardware to show up as an actual wall-clock win; a small
  demo circuit only proves the algorithm works.
- **QRNG's advantage is qualitative, not speed**: genuine hardware
  unpredictability plus `verify_run` auditability, independent of qubit
  count. Don't fold this into "quantum is faster" claims.
- **Speed/scale isn't the only axis for a real business decision.** Even
  where quantum could theoretically help, mature/proven classical
  technology often wins in production anyway: predictable cost and latency,
  no scheduled-uptime queue, no per-shot noise, existing tooling and staff
  familiarity. Recommend the boring, proven stack for an actual production
  workload unless there's a concrete, benchmarked reason not to — this
  repo's purpose is evaluating whether quantum genuinely helps, not
  advocating for it by default.
- As a sanity anchor: on this server's tiers (checked via `sdk_info`, snapshot
  2026-08-27), free tops out at 10 qubits/256 shots and paid at 20
  qubits/4000 shots for simulator runs, and 32 qubits for hardware — sizes
  that are trivially within classical reach. Default framing for runs at
  these sizes is "verifying/demonstrating the technique," not "quantum
  advantage."

## Common Mistakes

- Calling `submit_hardware_job` with `confirm=true` without the user having
  explicitly agreed to spend real money.
- Skipping `get_qpu_next_window` and being surprised a hardware job sits
  queued.
- Reporting a QAOA/VQE result as proof of quantum advantage with no
  classical baseline to compare against.
- Treating a tier-cap `CircuitBuildError` (e.g. `n_starts` too high) as a
  server bug instead of checking `sdk_info` for the current limit.
