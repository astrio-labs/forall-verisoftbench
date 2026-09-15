# Evaluation summary

The reported columns transcribe manuscript Table 1. Retained columns are computed from this release. Missing audits are not passing audits.

## Acceptance and audit coverage

| Configuration | Reported Rules | Retained accepted / tasks | Reported Strict | Retained clean / audited | Independent accepted / judged | Checker records / eligible |
| --- | --- | --- | --- | --- | --- | --- |
| `claude_opus_xhigh` | 100 | 100/100 | 89 | unavailable | unavailable | 0/72 |
| `forall_opus_xhigh` | 100 | 98/100 | 96 | 96/98 | 69/69 | 70/72 |
| `claude_opus_low` | 99 | 99/100 | 87 | 87/99 | 62/69 | 71/72 |
| `forall_opus_low` | 100 | 100/100 | 89 | 89/100 | unavailable | 0/72 |
| `claude_fable_low` | 96 | 96/100 | 89 | 85/96 | unavailable | 0/72 |
| `forall_fable_low` | 100 | 100/100 | 89 | 89/100 | 62/70 | 72/72 |
| `numina_fable_low` | 86 | 86/100 | unavailable | unavailable | unavailable | 0/72 |
| `codex_sol_low` | 93 | 93/100 | 82 | 1/1 | unavailable | 0/72 |
| `forall_sol_low_codex` | 100 | 99/100 | 88 | 88/99 | 63/69 | 71/72 |
| `codex_sol_xhigh` | 97 | 97/100 | 86 | 1/1 | unavailable | 0/72 |
| `forall_sol_xhigh_codex` | 100 | 100/100 | 88 | 88/100 | 60/67 | 69/72 |
| `opencode_sol_low` | 67 | 67/100 | 61 | 61/67 | 42/45 | 47/72 |
| `forall_sol_low_opencode` | 70 | 70/100 | 65 | unavailable | unavailable | 0/72 |

Configuration names, models, effort, and adapters are defined in [reported_results.csv](../reported_results.csv). The denominators above have different meanings. The one-task Codex audits cover only task 222. See [reconciliation](../RECONCILIATION.md) for score differences.

## Reported resources

| Configuration | Cost USD | Input M | Cached input M | Output M | Cost / retained acceptance USD | Elapsed field coverage |
| --- | --- | --- | --- | --- | --- | --- |
| `claude_opus_xhigh` | 135 | 53.8 | 50.1 | 2.09 | 1.35 | 0/100 |
| `forall_opus_xhigh` | 111 | 45.3 | 44.0 | 1.58 | 1.13 | 100/100 |
| `claude_opus_low` | 101 | 62.94 | 58.71 | 1.18 | 1.02 | 0/100 |
| `forall_opus_low` | 118 | 132.9 | 129.4 | 0.95 | 1.18 | 100/100 |
| `claude_fable_low` | 157 | 57.98 | 53.84 | 1.11 | 1.64 | 0/100 |
| `forall_fable_low` | 350 | 178.3 | 172.6 | 1.27 | 3.50 | 100/100 |
| `numina_fable_low` | 2011 | 899.3 | 867.8 | 5.15 | 23.38 | 99/100 |
| `codex_sol_low` | 69 | 68.1 | 61.7 | 0.95 | 0.74 | 0/100 |
| `forall_sol_low_codex` | 62 | 80.7 | 75.4 | 0.54 | 0.63 | 0/100 |
| `codex_sol_xhigh` | 68 | 63.4 | 56.6 | 0.95 | 0.70 | 0/100 |
| `forall_sol_xhigh_codex` | 85 | 104.5 | 98.1 | 1.0 | 0.85 | 0/100 |
| `opencode_sol_low` | 45 | 41.9 | 37.1 | 0.54 | 0.67 | 0/100 |
| `forall_sol_low_opencode` | 33 | 26.3 | 22.3 | 0.25 | 0.47 | 100/100 |

Costs and tokens are rounded manuscript values. Cache is included in total input. The cost ratio combines reported cost with retained acceptance and is descriptive. The final-result elapsed fields have different timing scopes and are not aggregated.

## Export checks

The export contains 1,300 task records, 761 task-level axiom audits, and 400 independent-checker records.

There are 600 matching recorded candidate digests and 1,299 observed candidate files. Hashes identify artifacts and do not independently certify correctness.
