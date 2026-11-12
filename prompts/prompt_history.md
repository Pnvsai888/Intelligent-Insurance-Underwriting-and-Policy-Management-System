# Prompt Engineering & System Evolution Log

## Iteration 1: Data Model & Synthetic Baseline
- Established 10 core relational entities with deterministic IDs (`APP-2026-XXXXXX`, etc.).
- Formulated actuarial factor rating logic ($P = \text{SI} \times \text{Base} \times M_{\text{credit}} \times M_{\text{loss}} \times M_{\text{asset}}$).
- Generated baseline scales: 3,000 Applicants, 4,000 Quotes, 2,000 Policies, 1,200 Renewals.

## Iteration 2: Edge Case Injection & Ground Truth
- Deliberately injected 5 negative scenarios ($N = 58$): unauthorized bindings, formula mismatches, capacity breaches, cancelled policy renewals, and overlapping policy periods.
- Enforced strict ground-truth isolation without operational feature leakage.

## Iteration 3: Comprehensive Validation & Multi-Format Seed Export
- Built automated test suites verifying PK uniqueness, FK constraints, and date chronology.
- Added arithmetic reconciliation auditing quote premiums against rate tables.
- Exported JSON bundles and SQL DDL/INSERT statements.

## Iteration 4: Parameterization & Architecture Modularization
- Exposed command-line flags (`--scale starter|full`, `--seed 20261022`).
- Modularized engines into eligibility, rating, authority routing, and issuance condition gates.