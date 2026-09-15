# Data dictionary

All counts and verdicts come from author-retained records or the explicitly labeled manuscript table. An empty CSV cell means unavailable or inapplicable. It never means zero, failure, or an unperformed check passed.

## Reported results

`reported_results.csv` contains the 13 local configurations in manuscript Table 1. External leaderboard baselines are outside this package.

| Field | Meaning |
| --- | --- |
| `configuration_id` | Stable join key that distinguishes configurations with the same system and model |
| `system`, `model`, `effort` | System and model names as reported in the manuscript |
| `adapter` | Execution frontend, kept separate from the system name |
| `reported_rules` | Manuscript benchmark acceptance count out of 100 |
| `reported_strict` | Manuscript count excluding forbidden axiom dependencies |
| `reported_independent_accepted` | Manuscript independent-checker accepted count |
| `reported_independent_judged` | Manuscript independent-checker denominator |
| `reported_input_million` | Total input tokens in millions, including cached input |
| `reported_cached_input_million` | Cached input tokens in millions, a subset of total input |
| `reported_output_million` | Output tokens in millions |
| `reported_cost_usd` | Rounded manuscript cost in US dollars |

Reported resource values inherit the paper's accounting and rounding. They are not reconstructed from the task records in this release. Dividing reported cost by retained acceptances provides a descriptive ratio across those two sources. It is not a new measured per-task bill or a controlled efficiency comparison.

## Task records

`results.csv` has one row for every configuration and task, totaling 1,300 rows. `tasks.csv` maps each task ID to its upstream repository. Task statements and proof text are absent.

| Field | Meaning |
| --- | --- |
| `recorded_status` | Status in the original result or reviewed-result record |
| `retained_outcome` | `accepted` or `not_accepted` under the retained run's acceptance procedure |
| `evidence_basis` | `result`, `reviewed_result`, or `review_parser_recovery` |
| `attempt_scope` | Retained run, original pass, fresh retry, or recovered dependency environment |
| `review_rounds` | Round count in the final reviewed record, when available |
| `solved_on_sample` | Successful sample index from a sampling baseline, when available |
| `recorded_elapsed_seconds` | Numeric elapsed value from the retained final result |
| `recorded_proof_sha256` | Candidate digest in the retained result record, when present |
| `artifact_sha256` | SHA-256 computed from the retained candidate file during export |
| `artifact_hash_check` | `match`, `mismatch`, `unrecorded`, or `unavailable` |

The elapsed field inherits the original result's timing boundary. Depending on the producer, it describes a final verification operation or an attempt. It is not consistently end-to-end actor and reviewer runtime. The summaries report timing coverage without aggregating unlike timing scopes.

Candidate files may exist for unsuccessful tasks. A hash in such a row does not turn its outcome into an acceptance. `unrecorded` means a retained file was hashed during export but the original result lacked a digest. `unavailable` means there was no candidate file to hash. The export found 600 matching recorded digests, 699 files without a recorded digest, one unavailable artifact, and no mismatches.

## Axiom audits

`axiom_audits.csv` has one row per available task audit. `audit_snapshot` identifies a retained audit, a rescore, a result-level check, or task 222's dependency recovery.

`audit_outcome` is `clean`, `forbidden_dependency`, or `inconclusive`. Clean counts use the retained audit's explicit forbidden and inconclusive task lists. For the Opus xhigh Forall snapshot, they use its retained rescore. Clean does not mean axiom-free. The permitted foundational axioms are `propext`, `Classical.choice`, and `Quot.sound`. Forbidden dependencies include `sorryAx`, `Lean.ofReduceBool`, and `Lean.trustCompiler`.

`axioms` contains only recognized kernel axiom names, separated by `|`. `axiom_list_complete` is true when the retained text contained a complete bracketed list. Some audit records retained only the first line of a wrapped list. In those cases the explicit audit verdict remains available while the axiom list is incomplete. An empty list with `axiom_list_complete` false does not claim an axiom-free proof.

Audit coverage is separate from benchmark acceptance coverage. In particular, the two unaided Codex configurations have only the task 222 audit exported here. Their manuscript strict totals cannot be reproduced from that one-task audit.

## Independent checks

`independent_checks.csv` preserves 400 task-level checker records across six configurations. `checker_scope` distinguishes the original 96 accepted Codex xhigh tasks from cumulative results. `elapsed_seconds` is the checker's recorded runtime.

`accepted` and `rejected_axiom` are judged verdicts. `harness_module_artifact` is excluded from the judged denominator. All 72 eligible tasks remain the coverage denominator, including those without a checker record. Eligible tasks come from `clean`, `veil`, `LeanExprEvaluator`, and `VCV-io` under Lean v4.24.0 or v4.24.0-rc1.

The independent-checker records are historical snapshots with no recorded candidate digest. They are not newly executed checks. Unavailable or ambiguously attributed checker snapshots are omitted and documented in [RECONCILIATION.md](RECONCILIATION.md).

## Environment pins

`environment/benchmark.json` records the exact upstream dataset revision, dataset digest, subset definition, source repository commits, Lean toolchains, and dependency pins from the retained benchmark build configurations. It also identifies the Qq revision used to recover task 222. These are environment references, not a distribution of the patched repositories or a complete rebuild kit.

`environment/evaluation.json` records declared sample, compiler, and reviewer budgets. A null compilation limit means uncapped when the scope is `uncapped`. Other null limits mean inapplicable. Fresh retries and cumulative scoring are described separately in [RECONCILIATION.md](RECONCILIATION.md).
