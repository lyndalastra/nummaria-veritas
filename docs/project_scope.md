# Nummaria Veritas — Project Scope

## Thesis

**Nummaria Veritas is an evidence-integrity framework for financial AI. It evaluates whether financial claims are supported by evidence that is temporally valid, sufficiently independent, numerically consistent and appropriately represented, and identifies the minimum Claim Delta (Δ) required to make unsupported or overstated claims defensible.**

Verification is not binary. The framework should explain what survives, what fails, why it fails, and the minimum semantic correction required to make the claim defensible.

## Motivation

Financial claims can appear well-supported while still being invalid.

A system may retrieve the correct documents, numbers and terminology yet reach an indefensible conclusion because:

- evidence was unavailable at the relevant point in time;
- multiple sources are derivative rather than independent;
- individually correct facts are combined incorrectly;
- metrics use incompatible definitions or accounting bases;
- periods, entities or scopes are mismatched;
- guidance is represented as realised fact;
- correlation or management attribution is converted into causation;
- a later disclosure supersedes or changes the interpretation of earlier information;
- a necessary link in a reasoning chain is missing.

Nummaria Veritas is designed to evaluate the integrity of the **evidence-to-claim relationship**, rather than merely retrieve passages that resemble a claim.

## Core Principles

### 1. Point-in-time validity

Evidence used to verify a claim must have been available on or before the claim's `as_of_date`.

Future information must not leak into historical verification.

### 2. Evidence independence

Multiple documents do not necessarily constitute multiple independent observations.

The framework should distinguish genuinely independent evidence from duplicated, syndicated, summarised or derivative evidence.

### 3. Numerical consistency

Numbers, directions of change, calculations and comparisons must be internally consistent with the underlying evidence.

### 4. Representational integrity

A fact can be numerically correct while being represented incorrectly.

The framework must preserve distinctions such as:

- reported vs adjusted/core measures;
- actual exchange rates vs constant exchange rates;
- full-year vs interim or quarterly periods;
- Group vs segment or geographic scope;
- realised performance vs guidance;
- observation vs causal interpretation.

### 5. Compositional validity

Correct components do not guarantee a correct claim.

The framework must evaluate how evidence is combined, including dependencies, contextual interpretation, precedence, boundaries and interacting constraints.

A missing or invalid intermediate dependency may invalidate a conclusion even when the remaining evidence is correct.

### 6. Minimum Claim Delta (Δ)

When a claim is not defensible, Nummaria Veritas should identify the smallest semantic change required to make it defensible.

A Claim Delta may involve changing:

- a number;
- a metric;
- a reporting period;
- an entity or scope;
- temporal language;
- certainty;
- causal language;
- or an unsupported inferential relationship.

The objective is not to rewrite the claim unnecessarily, but to preserve as much valid information as possible.

## Failure Model

### Claim-level issues

- `anachronistic_claim`
- `numerical_inconsistency`
- `metric_mismatch`
- `period_mismatch`
- `entity_scope_mismatch`
- `forecast_as_fact`
- `causal_overclaim`

### Evidence-level issues

- `temporal_leakage`
- `evidence_redundancy`
- `contradictory_evidence`

The taxonomy is expected to evolve as more complex benchmark cases are introduced.

## Benchmark Philosophy

The initial benchmark contains deliberately simple claims. These cases provide deterministic tests for the core verification machinery.

They are not the intended ceiling of the system.

Benchmark difficulty should progressively increase.

### Tier 1 — Atomic

Single-fact verification:

- numerical errors;
- direction-of-change errors;
- metric mismatches;
- period mismatches.

### Tier 2 — Contextual

Claims requiring interpretation of:

- metric definitions;
- accounting basis;
- entity scope;
- reporting boundaries;
- temporal availability;
- precedence or superseding disclosures.

### Tier 3 — Compositional

Claims requiring multiple pieces of evidence whose relationships matter:

- dependency chains;
- interacting constraints;
- evidence genealogy;
- cross-document reasoning;
- context-dependent interpretation.

A missing intermediate fact may invalidate the complete claim.

### Tier 4 — Adversarial

Claims where most or all local facts are correct but the global conclusion is not.

These cases test whether the system distinguishes factual consistency from inferential validity.

### Tier 5 — Minimal Delta

Cases designed to evaluate whether the framework can identify the smallest semantic modification required to restore defensibility.

## Reasoning Patterns

The benchmark should eventually test reasoning structures inspired by difficult evaluation domains encountered during prior AI evaluation work.

These include:

**Constraint propagation** — a conclusion is valid only when multiple constraints hold simultaneously.

**Dependency chains** — later conclusions depend on earlier interpretations; losing one link breaks the chain.

**Context-sensitive interpretation** — identical-looking values or symbols can have different meanings depending on their surrounding rules.

**Precedence** — when multiple valid rules or disclosures apply, the system must determine which governs.

**Boundary sensitivity** — evidence may be valid within one period, entity, segment or definition but invalid when transferred across boundaries.

**Locally correct, globally invalid reasoning** — every retrieved component may be individually true while the final inference remains unsupported.

These patterns are intended to prevent the benchmark from degenerating into simple financial question answering.

## MVP Corpus

Initial companies:

- HSBC
- AstraZeneca

Initial reporting periods:

- FY2024
- H1 2025

The corpus will initially use annual/interim results, results announcements and presentations, with additional earnings materials and reporting periods added as the framework develops.

## MVP Objective

The MVP should demonstrate an end-to-end pipeline that can:

1. ingest financial reporting documents while preserving provenance;
2. retrieve evidence relevant to a claim;
3. enforce point-in-time evidence availability;
4. assess claim and evidence integrity;
5. distinguish supporting from contradictory evidence;
6. identify relevant failure modes;
7. produce an interpretable verdict;
8. generate a minimum Claim Delta where correction is required;
9. evaluate system outputs against a curated golden benchmark.

## Non-Goal

Nummaria Veritas is **not** intended to be a generic financial RAG application or a binary fact-checking system.

Successful retrieval of a passage containing matching entities, terminology or numbers is not sufficient evidence that a claim is defensible.