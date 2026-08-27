# Nummaria Veritas

**Evidence integrity for financial AI.**

Nummaria Veritas is an evidence-integrity framework for financial AI. It evaluates whether financial claims are supported by evidence that is **temporally valid, sufficiently independent, numerically consistent and appropriately represented**, and identifies the minimum **Claim Delta (Δ)** required to make unsupported or overstated claims defensible.

## Why?

A financial claim can contain the right company, the right numbers and citations to real documents — and still be wrong.

The failure may lie not in any individual fact, but in the relationship between them:

- evidence published after the relevant point in time;
- several citations derived from the same underlying source;
- incompatible metrics or reporting periods;
- reported and adjusted measures treated as equivalent;
- guidance represented as realised performance;
- correct local facts combined into an unsupported global inference;
- missing dependencies or ignored precedence rules.

Nummaria Veritas therefore asks a stricter question than *"Can I retrieve evidence for this statement?"*

> **Given the information legitimately available at the time, does this evidence actually justify this claim?**

## Core Verification Dimensions

**Temporal validity**  
Was the evidence available at the claim's `as_of_date`?

**Evidence independence**  
Do multiple sources provide independent support, or are they derivative of the same evidence?

**Numerical consistency**  
Are values, comparisons and directions of change consistent with the underlying disclosures?

**Representational integrity**  
Are metric definitions, reporting periods, entity scope, accounting basis and epistemic status represented correctly?

**Compositional validity**  
Does the conclusion follow from the evidence when dependencies, context, precedence and constraints are considered?

**Claim Delta (Δ)**  
If the claim fails, what is the smallest semantic change that makes it defensible?

## Example

A claim may be almost entirely correct:

> Company X's reported profit increased because revenue growth offset higher costs.

The underlying documents may separately support revenue growth, higher costs and increased profit.

That does **not** necessarily establish the causal relationship expressed by *because*.

Nummaria Veritas is designed to distinguish:

**facts supported individually**

from

**the claim supported as a whole**.

The resulting Claim Delta might therefore be as small as:

`because` → `while`

rather than replacing the entire statement.

## Benchmark

The benchmark progresses from atomic financial checks toward adversarial compositional reasoning:

`Atomic → Contextual → Compositional → Adversarial → Minimal Δ`

Later cases are designed so that successful retrieval alone is insufficient: the system must reason over temporal boundaries, evidence genealogy, metric definitions, dependencies, precedence and interacting constraints.

The initial corpus uses HSBC and AstraZeneca reporting materials across FY2024 and H1 2025.

## Potential Applications

Nummaria Veritas is designed as an assurance layer between financial evidence and AI-generated conclusions.

Potential applications include:

- **Quantitative research** — detecting point-in-time leakage, invalid evidence dependencies and apparent corroboration from derivative sources before AI-derived information enters a research pipeline.
- **Investment research** — validating AI-generated equity, credit and market research against the evidence actually available at the relevant time.
- **Financial data and research platforms** — checking generated summaries, research outputs and data products before they reach downstream users.
- **Financial AI agents** — providing structured verification, correction and escalation around agent-generated financial claims.
- **Model validation and AI governance** — producing an auditable trail from claim → evidence → integrity checks → verdict → Claim Delta.

Nummaria Veritas supports two complementary modes:

**Evaluation mode** — adversarially test financial AI systems to identify systematic evidence-integrity failure modes.

**Runtime assurance mode** — evaluate individual claims before they are published, consumed by another system or used in a decision-making workflow.

```text
Financial evidence
        ↓
   AI / Agent
        ↓
Nummaria Veritas
        ↓
┌─────────────┬─────────────┬─────────────┐
│ Defensible  │ Correctable │  Escalate   │
└─────────────┴─────────────┴─────────────┘
        ↓
Research / data product / downstream system
```

## Status

🚧 **MVP under development**

Current progress:

- [x] Project architecture
- [x] Core data models
- [x] Verification taxonomy
- [x] Initial financial corpus
- [x] Golden benchmark foundation
- [x] Benchmark validation tests
- [ ] Document ingestion
- [ ] Evidence retrieval
- [ ] Temporal filtering
- [ ] Evidence-integrity analysis
- [ ] Claim verification
- [ ] Claim Delta generation
- [ ] Benchmark evaluation
- [ ] End-to-end interface

## Design Scope

The complete design principles, benchmark philosophy and MVP boundaries are documented in [`docs/project_scope.md`](docs/project_scope.md).

