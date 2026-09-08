# Nummaria Veritas — Project Scope

## Thesis

**Nummaria Veritas is an evidence-integrity framework for financial AI. It evaluates whether financial claims are supported by evidence that is temporally valid, sufficiently independent, numerically consistent and appropriately represented, and identifies the minimum Claim Delta (Δ) required to make unsupported or overstated claims defensible.**

The core research question is:

> **Given the information legitimately available at the time, does this evidence actually justify this claim as stated?**

Verification is not treated as a binary retrieval problem. The framework makes explicit:

- what evidence is admissible;
- what part of a claim survives;
- what fails;
- whether the failure belongs to the claim or the evidence;
- what minimum semantic correction would restore defensibility.

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
- or a necessary dependency in a reasoning chain is absent.

Nummaria Veritas evaluates the integrity of the **evidence-to-claim relationship**, rather than treating retrieval similarity as proof.

---

## Core Principles

### 1. Point-in-time validity

Evidence used to verify a claim must have been available on or before the claim's `as_of_date`.

Temporal admissibility is enforced before ranking so that later disclosures cannot improve historical evidence selection.

### 2. Evidence independence

Multiple documents do not necessarily constitute multiple independent observations.

Evidence provenance is preserved so that apparent corroboration can be distinguished from repeated or derivative support.

The current MVP uses deterministic provenance clustering based on document metadata. Richer modelling of evidence lineage or document relationships is a later extension.

### 3. Numerical consistency

Financial values must be compatible with the underlying evidence.

The numerical layer preserves distinctions such as:

- percentages;
- currencies;
- scale;
- compatible numerical representations.

Numerical equality alone is not always sufficient. Two values can look similar while referring to incompatible representations or contexts.

### 4. Representational integrity

A fact can be numerically plausible while being represented incorrectly.

Relevant distinctions include:

- reported vs adjusted/core measures;
- actual exchange rates vs constant exchange rates;
- full-year vs interim or quarterly periods;
- Group vs segment or geographic scope;
- realised performance vs guidance;
- observation vs causal interpretation.

The benchmark taxonomy covers more representational failures than the current set of standalone verifier mechanisms.

### 5. Compositional validity

Correct components do not guarantee a correct claim.

A claim may contain individually supported facts while asserting a relationship that does not follow from them.

Relevant reasoning structures include:

- dependencies;
- contextual interpretation;
- precedence;
- boundaries;
- interacting constraints;
- inferential relationships.

A missing or invalid dependency can invalidate the complete claim even when the remaining facts are correct.

### 6. Minimum Claim Delta (Δ)

When a claim is not defensible, a Claim Delta represents the smallest semantic change required to restore defensibility.

A Claim Delta may conceptually involve changing:

- a number;
- a metric;
- a reporting period;
- an entity or scope;
- temporal language;
- certainty;
- causal language;
- an unsupported inferential relationship.

Automatic Claim Delta generation is currently limited to constrained numerical corrections.

The benchmark also stores gold revised claims for broader perturbation types so that future correction mechanisms have an explicit evaluation target.

The aim is to preserve valid parts of the original claim rather than rewrite it unnecessarily.

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

For example, evidence may establish both financial facts in a causal statement while failing to establish the asserted causal relationship. In that case, the evidence supports part of the proposition rather than being neutral to it.

---

## Failure Model

### Claim-level issues

`anachronistic_claim`  
The claim could not legitimately have been made at its evaluation time because the required information was not yet available.

`numerical_inconsistency`  
A numerical value in the claim is incompatible with the admissible evidence.

`metric_mismatch`  
The claim and evidence refer to different financial metrics or incompatible metric definitions.

`period_mismatch`  
The claim and evidence refer to different reporting periods.

`entity_scope_mismatch`  
The claim asserts the wrong entity, segment, geography or reporting scope.

`forecast_as_fact`  
Guidance, expectation or forecast information is represented as realised fact.

`causal_overclaim`  
The claim asserts a causal relationship that the admissible evidence does not establish.

`compositional_invalidity`  
The individual components may be supported, but the relationship or conclusion formed from them is not.

### Evidence-level issues

`temporal_leakage`  
Evidence published after the claim's `as_of_date` is used or supplied for verification.

`evidence_redundancy`  
Multiple supporting items do not represent independent evidence because they share the same underlying provenance.

`contradictory_evidence`  
Admissible evidence contains information that conflicts with the claim.

`scope_mismatch`  
The claim may be valid, but the supplied evidence comes from an incompatible entity, segment, geography or reporting scope.

Claim issues describe problems with **what the claim asserts**. Evidence issues describe problems with **the evidence used to support it**.

For example:

- an incorrect entity scope asserted by the claim is `entity_scope_mismatch`;
- a valid Group-level claim paired only with segment-level evidence is `scope_mismatch`;
- a supported claim can still carry `evidence_redundancy` without becoming unsupported.

---

## Current Executable Verification Mechanisms

The MVP currently exposes four independently switchable verification mechanisms.

### Temporal validity

Future evidence is excluded from admissible evidence.

### Numerical consistency

Financial numerical values are extracted and compared while preserving percentage, currency and scale semantics.

### Causal overclaim

A causal atomic proposition is flagged when admissible evidence does not establish the asserted causal relationship.

Full semantic support is required to establish the causal relation. Partial support of the underlying facts is not enough.

### Evidence independence

Supporting evidence is grouped by provenance to distinguish raw citation count from independent evidence count.

These four mechanisms are configurable so their contribution can be tested through component ablations.

Other benchmark dimensions are not treated as standalone verifier modules unless an executable boundary exists for them.

---

## Benchmark Philosophy

The benchmark starts with base financial claims and progressively introduces cases where successful retrieval is not enough.

The progression is:

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

Claims involving multiple pieces of evidence whose relationships matter:

- dependency chains;
- interacting constraints;
- evidence genealogy;
- cross-document reasoning;
- context-dependent interpretation.

A missing intermediate fact may invalidate the complete claim.

### Tier 4 — Adversarial

Claims where most or all local facts are correct but the global conclusion is not.

These cases test whether factual consistency is being confused with inferential validity.

### Tier 5 — Minimal Delta

Cases used to evaluate the smallest semantic modification required to restore defensibility.

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

Perturbation IDs are human-readable checksums. System behaviour comes from explicit benchmark fields rather than parsing the ID.

Contradiction is not a perturbation type. It is an observed relationship between a claim and appropriately aligned evidence.

---

## Current Benchmark

The corpus contains public financial reporting materials from:

**Issuers**

- HSBC
- AstraZeneca

**Reporting periods**

- FY2024
- H1 2025

The processed corpus preserves:

- issuer;
- document identity;
- document type;
- reporting period;
- publication date;
- page number;
- chunk identity;
- chunk text.

The current adversarial layer contains eight perturbations across claim, evidence and evaluation-context targets:

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

The benchmark targets reasoning structures that cannot be reduced to surface similarity.

### Constraint propagation

A conclusion is valid only when the relevant constraints hold simultaneously.

### Dependency chains

Later conclusions may depend on earlier interpretations. Losing one link can invalidate the chain.

### Context-sensitive interpretation

Identical-looking values can have different meanings under different reporting definitions or contexts.

### Precedence

When several disclosures or rules are relevant, the correct interpretation may depend on which applies at the claim's evaluation point.

### Boundary sensitivity

Evidence may be valid within one period, entity, segment or definition but invalid when transferred across that boundary.

### Locally correct, globally invalid reasoning

Every retrieved component may be individually true while the final inference remains unsupported.

These patterns keep the benchmark focused on evidence integrity rather than conventional financial question answering.

---

## Evaluation Strategy

### Perturbation-invariance baseline

The baseline assigns each perturbed case the verification state of its unperturbed source claim.

Current result:

```text
Full case exact match: 12.5%
Failure rate:          87.5%
```

Only the representation perturbation preserves the complete source judgment.

### Component ablations

Each independently switchable verification mechanism is disabled while its corresponding target phenomenon is held fixed.

The experiment measures:

- full-system targeted detection;
- disappearance of the targeted capability after ablation.

Current result:

```text
Full-system detection: 100% for each targeted mechanism
Ablation success:      100% for each targeted mechanism
```

Each current ablation is evaluated on its corresponding targeted benchmark case, so these results measure mechanism attribution rather than general benchmark accuracy.

### Failure analysis

Failure analysis uses the existing verification contract.

A failed benchmark case can differ along:

```text
verdict
claim_issues
evidence_issues
correction
```

Different perturbations can therefore produce different failure signatures without introducing a second manually defined failure taxonomy.

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
11. evaluate outputs against a curated gold benchmark;
12. run adversarial baselines, ablations and failure analysis;
13. expose verification through a FastAPI service;
14. run reproducibly through a locked Python environment and Docker image.

---

## Current Boundaries

Nummaria Veritas is a research MVP.

Current limitations include:

- semantic evidence stance is supplied explicitly rather than inferred autonomously;
- dense retrieval currently uses LSA rather than a neural embedding model;
- evidence independence relies on deterministic provenance clustering rather than richer evidence-lineage modelling;
- only four failure dimensions currently have standalone, independently ablatable verifier mechanisms: temporal validity, numerical consistency, causal overclaim and evidence independence;
- automatic Claim Delta generation is currently limited to constrained numerical corrections;
- the adversarial benchmark is small and hand-labelled, so the evaluation provides targeted coverage rather than broad statistical validation;
- the financial corpus covers two issuers and a limited set of reporting periods.

---

## Non-Goals

Nummaria Veritas is **not**:

- a generic financial RAG application;
- a binary passage-matching fact checker;
- an autonomous investment decision system;
- a claim that retrieval similarity implies evidential support.

Successful retrieval of a passage containing matching entities, terminology or numbers is not sufficient evidence that a financial claim is defensible.

The project is concerned with the integrity of the path:

```text
claim → evidence → admissibility → relationship → verdict → correction
```