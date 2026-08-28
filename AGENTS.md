# AGENTS.md — Algorithmic Trading Course

**Status:** Authoritative project entrypoint  
**Version:** 1.0  
**Date:** 2026-08-17  
**Owner:** Álvaro López Chacarra  
**Course:** Introducción al Algorithmic Trading con Python — ICAI 2026

---

## 1. Purpose

This file is the **entrypoint for any AI agent, coding agent, reviewer, or automation** working on this project.

Its job is to tell the agent:

- which sources are authoritative;
- which source governs each type of decision;
- where the code lives;
- how to resolve conflicts between documents;
- which invariants must not be broken.

Do not treat this file as a replacement for the source documents. It is a routing and governance layer.

---

## 2. Canonical project sources

### 2.1 Pedagogy — GOLDEN SOURCE

**File:**

`CONTRATO_PEDAGOGICO_ALGO_TRADING_2026.md`

This is the **golden source for all pedagogical and assessment decisions**.

It governs:

- session duration;
- classroom structure;
- presentation/exercise/test timing;
- autonomous work;
- continuous assessment;
- double sessions;
- asynchronous lessons;
- final exam;
- official grading weights;
- pedagogical invariants.

Current official grading:

| Component | Weight |
|---|---:|
| Attendance | **10%** |
| Participation | **20%** |
| Continuous exams | **40%** |
| Final exam | **30%** |
| **Total** | **100%** |

Current standard session:

```text
≈50 minutes total
→ 10 min continuous test
→ 20 min presentation
→ 20 min guided exercises
```

If another source conflicts with the pedagogical contract on any pedagogical matter, **the pedagogical contract wins**.

---

### 2.2 Infrastructure — GOLDEN SOURCE

**File:**

`ARCHITECTURE.md`

This is the **golden source for technical infrastructure and publication architecture**.

It governs:

- private/public repository topology;
- GitHub Actions;
- GitHub Pages;
- publication manifests;
- scheduled releases;
- security;
- leakage prevention;
- CI responsibilities;
- deployment;
- rollback;
- credentials;
- public/private material separation.

If another source conflicts with `ARCHITECTURE.md` on infrastructure, publication, CI, security, or repository topology, **`ARCHITECTURE.md` wins**.

Pedagogical statements duplicated inside `ARCHITECTURE.md` are mirrors for operational coherence only. The pedagogical contract remains authoritative for those points.

---

## 3. Code repository

### Current repository

`https://github.com/AlvaroChacarra/algo_trading_intro`

Public course site:

`https://alvarochacarra.github.io/algo_trading_intro/`

This repository contains the current course implementation, including:

- lesson folders;
- interactive documents;
- notebooks;
- `exchange/`;
- build tooling;
- tests;
- course framework;
- GitHub workflows;
- GitHub Pages output logic.

When the two-repository architecture is fully migrated, the authoritative source repository is expected to be:

`AlvaroChacarra/algo_trading_intro_source`

and the public distribution repository remains:

`AlvaroChacarra/algo_trading_intro`

Until that migration is complete, do not assume private/public separation has already been implemented merely because it appears in the architecture contract.

---

## 4. Source precedence

Use this order when making decisions.

### Pedagogical decisions

```text
1. CONTRATO_PEDAGOGICO_ALGO_TRADING_2026.md
2. Explicit latest user instruction
3. ARCHITECTURE.md when infrastructure affects pedagogy
4. Course plan / lesson specs
5. Existing implementation
```

### Infrastructure decisions

```text
1. ARCHITECTURE.md
2. Explicit latest user instruction
3. CONTRATO_PEDAGOGICO_ALGO_TRADING_2026.md when pedagogy constrains infrastructure
4. Existing workflows / implementation
5. Historical docs
```

### Implementation decisions

```text
1. Golden source relevant to the decision
2. Explicit latest user instruction
3. Existing tests and contracts
4. Current repository implementation
5. Historical plans/specs
```

Do not silently resolve a contradiction by guessing.

If two authoritative sources appear inconsistent:

1. identify the conflict;
2. determine which domain it belongs to;
3. apply the relevant golden source;
4. update the stale source if the task includes modifications;
5. preserve backwards compatibility where required.

---

## 5. Core pedagogical invariants

Any change to code, lessons, publishing, tests, or course flow must preserve these principles unless the pedagogical contract is explicitly changed.

### PED-01 — Session duration

Standard session duration is approximately **50 minutes**.

### PED-02 — Standard classroom split

```text
10 min → previous-content test
20 min → presentation
20 min → guided exercises
```

This is an operating target, not a rigid stopwatch rule.

### PED-03 — Autonomous consolidation

The student is expected to continue working after class.

Unfinished required content remains part of the course.

### PED-04 — Continuous tests

Each evaluated lesson normally maps to:

- 10 questions;
- A/B/C/D;
- approximately 10 minutes.

### PED-05 — No immediate testing in double sessions

If two sessions are consecutive, the second session does not test material from the first one if students have had no meaningful study time.

Pending tests are deferred to the next valid opportunity.

### PED-06 — Autonomous lessons are valid

A lesson may be partially or fully assigned for autonomous work when the pedagogical design supports it.

### PED-07 — Final exam remains mandatory

The final exam is cumulative and carries **30%** of the final grade.

### PED-08 — Assessment weights

```text
10% attendance
20% participation
40% continuous exams
30% final exam
```

---

## 6. Core infrastructure invariants

### INF-01 — Private source is authoritative after migration

The future private repository is the source of truth.

The public repository is a generated distribution target.

### INF-02 — Default deny publication

A file is public only if explicitly authorized.

### INF-03 — No future material in public history

Future lessons, solutions, exams, answer keys, hidden validators, or private material must never be committed publicly.

### INF-04 — Fail closed

If publication eligibility is uncertain, publication stops.

### INF-05 — Public repository must be reproducible

No unique authoritative content may live only in the public repository.

### INF-06 — Secrets remain private

Cross-repository credentials and private tokens never appear in public files, logs, generated HTML, or notebooks.

---

## 7. Course architecture

The course is a single cumulative project.

Students progressively build an `exchange` package:

```text
Order
→ Fill
→ OrderBook
→ PositionTracker
→ MatchingEngine
→ Market
→ Strategy
→ Backtest
→ VWAP
→ Market Maker
→ Avellaneda-Stoikov
→ Own strategy / capstone
```

The pedagogical objective is not to teach isolated Python topics.

Python concepts should appear because they solve a concrete trading or market-structure problem.

---

## 8. Lesson model

A lesson can contain more material than fits in the classroom session.

The agent must distinguish between:

### Core presencial

What the professor should prioritize live.

### Required consolidation

Material the student must complete independently and which may be evaluated.

### Optional depth

Bonus or advanced content that should not become implicitly mandatory.

Do not assume:

```text
not covered live = not examinable
```

The correct rule is:

```text
required material = examinable
unless explicitly marked optional
```

---

## 9. Assessment model

Continuous tests are not merely grading events.

They are part of the learning mechanism:

```text
class
→ autonomous consolidation
→ retrieval practice
→ feedback
→ next lesson
```

When two lessons are taught consecutively:

```text
Lesson A
→ Lesson B
→ autonomous consolidation
→ combined assessment at next valid opportunity
```

Typical combined assessment:

```text
2 lessons
→ 20 questions
→ ≈20 minutes
```

The scheduling system must support this without forcing a one-session/one-test mapping.

---

## 10. Working with the repository

Before modifying implementation:

1. inspect the current repository state;
2. identify which golden source governs the change;
3. inspect relevant tests and build scripts;
4. preserve existing behavior unless the task explicitly changes it;
5. make the minimum coherent change;
6. run the relevant validation;
7. report any conflict between source documents and implementation.

Do not rewrite large areas of the project merely to make them stylistically cleaner.

Prefer incremental changes that preserve the course.

---

## 11. Working with lesson content

When creating or modifying a lesson:

1. preserve the cumulative project story;
2. keep the lesson connected to `exchange`;
3. identify the classroom core;
4. identify autonomous required work;
5. identify optional depth;
6. ensure the next continuous test can assess the required material;
7. avoid overloading the live 20-minute presentation;
8. prioritize conceptual understanding over topic count.

A lesson is successful if the student knows what problem is being solved, why the implementation exists, and can continue working independently.

---

## 12. Working with tests and exams

Continuous tests must normally evaluate:

- code reading;
- behavior prediction;
- conceptual understanding;
- interpretation of results;
- common mistakes;
- connections between modules.

Avoid building tests that can be passed only by memorizing wording.

The final exam is cumulative and should test integration across the course, not merely reproduce continuous-test questions.

Sensitive assessment assets remain private unless explicitly released.

---

## 13. Working with publication

Publication must be driven by explicit authorization.

Expected model after migration:

```text
algo_trading_intro_source [PRIVATE]
        |
        | validate
        | build
        | allowlist
        | course_publish.yml
        v
algo_trading_intro [PUBLIC]
        |
        | pages.yml
        v
GitHub Pages
```

The public site URL must remain stable:

`https://alvarochacarra.github.io/algo_trading_intro/`

---

## 14. Do not assume implementation equals contract

The repository can lag behind the golden sources.

Examples:

- an old document may still say “40-minute classes”;
- current workflows may still reflect the pre-migration one-repository architecture;
- lesson specs may predate the current assessment model.

When implementation and contract disagree:

> contracts define the target state; repository code defines the current state.

An agent must distinguish these two explicitly.

---

## 15. Project organization rule

For future work, treat these files as the minimum context set:

```text
AGENTS.md
ARCHITECTURE.md
CONTRATO_PEDAGOGICO_ALGO_TRADING_2026.md
```

Then inspect repository code only as needed for the task.

This prevents every new task from having to rediscover the project's governance.

---

## 16. Final rule

The project has two golden sources:

```text
PEDAGOGY
CONTRATO_PEDAGOGICO_ALGO_TRADING_2026.md

INFRASTRUCTURE
ARCHITECTURE.md
```

`AGENTS.md` is the routing layer that tells every agent how to use them.

When in doubt:

```text
pedagogical question → pedagogical contract
infrastructure question → architecture
implementation question → relevant contract + repository state
```
