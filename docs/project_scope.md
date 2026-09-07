# Nummaria Veritas — Project Scope

## Thesis

**Nummaria Veritas is an evidence-integrity framework for financial AI. It evaluates whether financial claims are supported by evidence that is temporally valid, sufficiently independent, numerically consistent and appropriately represented, and identifies the minimum Claim Delta (Δ) required to make unsupported or overstated claims defensible.**

The core research question is:

> **Given the information legitimately available at the time, does this evidence actually justify this claim as stated?**

Verification is not treated as a binary retrieval problem. The framework should make explicit:

- what evidence is admissible;
- what part of a claim survives;
- what fails;
- whether the failure belongs to the claim or the evidence;
- and what minimum semantic correction would restore defensibility.

---

## Motivation

Financial claims can appear well-supported while still being invalid.

A system may retrieve genuine documents, correct entities, plausible values and closely matching terminology yet reach an indefensible conclusion because:

- evidence was unavailable at the relevant point in time;
- multiple citations derive from the same underlying disclosure;
- numerical values are incompatible;
- individually correct facts are combined incorrectly;
- metrics use incompatible definitions or accounting bases;
- periods, entities or scopes are mismatched;
- guidance is represented as realised fact;
- supported facts are transformed into an unsupported causal relationship;
- a later disclosure changes the interpretation of earlier information;
- or a necessary dependency in a reasoning chain is absent.

Nummaria Veritas therefore evaluates the integrity of the **evidence-to-claim relationship**, rather than treating retrieval similarity as proof.

---

## Core Principles

### 1. Point-in-time validity

Evidence used to verify a claim must have been available on or before the claim's `as_of_date`.

Temporal admissibility should be enforced as early as possible. In retrieval, future evidence is filtered before ranking so that later disclosures cannot improve historical evidence selection.

### 2. Evidence independence

Multiple documents do not necessarily constitute multiple independent observations.

Evidence provenance must be preserved so that apparent corroboration can be distinguished from repeated or derivative support.

The current MVP uses deterministic provenance clustering. More sophisticated evidence genealogy remains a later extension.

### 3. Numerical consistency

Numbers, directions of change, percentages, currencies, scales and comparisons must be compatible with the underlying evidence.

Numerical equality alone is insufficient when representation differs materially.

### 4. Representational integrity

A fact can be numerically plausible while being represented incorrectly.

Relevant distinctions include:

- reported vs adjusted/core measures;
- actual exchange rates vs constant exchange rates;
- full-year vs interim or quarterly periods;
- Group vs segment or geographic scope;
- realised performance vs guidance;
- observation vs causal interpretation.

Representational integrity is broader than the set of currently standalone verifier modules. Some representational failures are presently encoded through benchmark expectations and the issue ontology.

### 5. Compositional validity

Correct components do not guarantee a correct claim.

A claim may contain individually supported facts while asserting a relationship that does not follow from them.

The framework should therefore support reasoning over:

- dependencies;
- contextual interpretation;
- precedence;
- boundaries;
- interacting constraints;
- inferential relationships.

A missing or invalid intermediate dependency may invalidate the complete claim even when the remaining evidence is correct.

### 6. Minimum Claim Delta (Δ)

When a claim is not defensible, Nummaria Veritas should represent the smallest semantic change required to restore defensibility.

A Claim Delta may conceptually involve changing:

- a number;
- a metric;
- a reporting period;
- an entity or scope;
- temporal language;
- certainty;
- causal language;
- or an unsupported inferential relationship.

The current automatic generator implements constrained numerical correction. The benchmark contains gold revised claims for a broader range of perturbations so that future correction mechanisms can be evaluated against an explicit target.

The objective is to preserve as much valid information as possible rather than unnecessarily rewriting the entire claim.

---

## Verification Contract

### Verdicts

```text
supported_claim
partially_supported_claim
contradicted_claim
unsupported_claim
invalid_evidence
insufficient_evidence
```

These verdicts separate proposition failure from evidence failure.

Examples:

- `supported_claim` — admissible evidence establishes the proposition;
- `partially_supported_claim` — evidence establishes substantive parts of the proposition but not the claim as stated;
- `contradicted_claim` — admissible evidence is incompatible with the claim;
- `unsupported_claim` — admissible evidence exists but does not establish the proposition;
- `invalid_evidence` — supplied evidence is unsuitable for establishing the claim;
- `insufficient_evidence` — suitable evidence is absent or unavailable.

### Evidence stance

```text
supports
partially_supports
contradicts
neutral
```

`partially_supports` is distinct from `neutral`.

For example, evidence may establish both financial facts in a causal statement while failing to establish the asserted causal relationship. Such evidence is substantively supportive of part of the claim rather than neutral to it.

---

## Failure Model

### Claim-level issues

```text
anachronistic_claim
numerical_inconsistency
metric_mismatch
period_mismatch
entity_scope_mismatch
forecast_as_fact
causal_overclaim
compositional_invalidity
```

### Evidence-level issues

```text
temporal_leakage
evidence_redundancy
contradictory_evidence
scope_mismatch
```

The distinction is intentional.

For example:

- an incorrect entity scope asserted by the claim is a claim issue;
- a valid Group-level claim supported only by segment-level evidence is an evidence issue.

A supported claim may also carry an evidence issue such as redundancy without becoming unsupported.

---

## Current Executable Verification Mechanisms

The MVP currently exposes four independently switchable verification mechanisms:

### Temporal validity

Future evidence is excluded from admissible evidence.

### Numerical consistency

Financial numerical values are extracted and compared while preserving relevant representation such as percentage, currency and scale.

### Causal overclaim

A causal atomic proposition is flagged when the admissible evidence does not establish the asserted causal relationship.

Full semantic support is required to establish the causal relation; partial support of the underlying facts is not sufficient.

### Evidence independence

Supporting evidence is grouped by provenance to distinguish raw citation count from independent evidence count.

These four mechanisms are explicitly configurable so that their contribution can be tested through component ablations.

Other benchmark dimensions should not be described as standalone verifier modules until a corresponding executable boundary exists.

---

## Benchmark Philosophy

The benchmark begins with deterministic financial claims and progressively introduces cases where successful retrieval is insufficient.

The intended progression is:

```text
Atomic → Contextual → Compositional → Adversarial → Minimal Δ
```

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

---

## Perturbation Model

Benchmark perturbations are represented along two independent dimensions.

### Perturbation type — what changed?

```text
none
numerical
metric
period
scope
temporal
representation
forecast_as_fact
causal
compositional
entity
redundancy
```

### Perturbation target — where did it change?

```text
claim
evidence
evaluation_context
```

The perturbation ID is a human-readable checksum. System behaviour must be derived from explicit benchmark fields rather than parsing IDs.

Contradiction is not itself treated as a perturbation type. Contradiction is an observed relationship between a claim and appropriately aligned evidence.

---

## Current Benchmark

The MVP corpus contains public financial reporting materials from:

- HSBC;
- AstraZeneca.

Current periods include:

- FY2024;
- H1 2025.

The processed corpus preserves:

- issuer;
- document identity;
- document type;
- reporting period;
- publication date;
- page number;
- chunk identity;
- chunk text.

The current adversarial layer contains eight perturbations across claim, evidence and evaluation-context targets.

These cases include:

- temporal invalidation;
- numerical contradiction;
- representation-preserving change;
- scope-mismatched evidence;
- redundant evidence;
- forecast represented as fact;
- unsupported causal relationship;
- invalid compositional comparison.

---

## Reasoning Patterns

The benchmark is designed to test reasoning structures that cannot be reduced to surface similarity.

### Constraint propagation

A conclusion is valid only when multiple constraints hold simultaneously.

### Dependency chains

Later conclusions depend on earlier interpretations. Losing one link can invalidate the chain.

### Context-sensitive interpretation

Identical-looking values can have different meanings under different reporting definitions or contexts.

### Precedence

When multiple valid rules or disclosures apply, the system must determine which governs the claim at the relevant point in time.

### Boundary sensitivity

Evidence may be valid within one period, entity, segment or definition but invalid when transferred across that boundary.

### Locally correct, globally invalid reasoning

Every retrieved component may be individually true while the final inference remains unsupported.

These patterns are intended to prevent the benchmark from degenerating into conventional financial question answering.

---

## Evaluation Strategy

### Perturbation-invariance baseline

The naïve baseline assigns each perturbed case the verification state of its unperturbed source claim.

This tests the hypothesis that evidence integrity cannot be captured by simply preserving the source judgment across superficially related cases.

Current result:

```text
Full case exact match: 12.5%
Failure rate:          87.5%
```

### Component ablations

Each independently switchable verification mechanism is disabled while the corresponding target phenomenon is held fixed.

The experiment measures:

- full-system targeted detection;
- successful disappearance of that capability after ablation.

Current four-mechanism result:

```text
Full-system detection: 100% for each targeted mechanism
Ablation success:      100% for each targeted mechanism
```

These are component-sensitivity results over targeted cases, not estimates of general benchmark accuracy.

### Failure analysis

Failure analysis operates over the evaluation contract rather than introducing a second manually assigned failure taxonomy.

A failed benchmark case can differ along:

```text
verdict
claim_issues
evidence_issues
correction
```

This allows distinct perturbations to produce different empirical failure signatures.

---

## MVP Objective

The MVP demonstrates a pipeline that can:

1. ingest financial reporting documents while preserving provenance;
2. construct a page- and chunk-aware evidence corpus;
3. retrieve evidence under point-in-time constraints;
4. decompose claims into atomic propositions;
5. represent semantic evidence stance explicitly;
6. apply independently testable integrity checks;
7. distinguish claim-level from evidence-level failures;
8. produce interpretable atomic and parent verdicts;
9. represent and validate Claim Delta corrections;
10. automatically generate constrained numerical Claim Deltas;
11. evaluate outputs against a curated golden benchmark;
12. run adversarial baselines, ablations and failure analysis;
13. expose verification through a FastAPI service;
14. run reproducibly through a locked Python environment and Docker image.

---

## Current Boundaries

The MVP deliberately does not claim to solve every layer autonomously.

Current limitations include:

- semantic stance is supplied explicitly rather than inferred by an autonomous language model;
- dense retrieval uses LSA as a reproducible baseline;
- evidence independence uses deterministic provenance clustering;
- the standalone verifier mechanism set is smaller than the full benchmark ontology;
- automatic Claim Delta generation is currently focused on constrained numerical corrections;
- the benchmark is small and hand-labelled;
- the financial corpus covers a limited number of issuers and reporting periods.

These boundaries are intended to keep the experimental contracts explicit and testable while the system grows.

---

## Non-Goals

Nummaria Veritas is **not**:

- a generic financial RAG application;
- a binary passage-matching fact checker;
- an autonomous investment decision system;
- a claim that retrieval similarity implies evidential support.

Successful retrieval of a passage containing matching entities, terminology or numbers is not sufficient evidence that a financial claim is defensible.

The project is specifically concerned with the integrity of the path:

```text
claim → evidence → admissibility → relationship → verdict → correction
```