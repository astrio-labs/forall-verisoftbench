# Reconciliation of reported and retained results

The manuscript's Table 1 and the retained evaluation files are different sources. This release preserves both without changing the paper or inventing missing evidence.

## Outstanding differences

| Configuration | Manuscript | Retained evidence |
| --- | --- | --- |
| Forall-Lean-Agent, Opus 5 xhigh | Rules 100 | 98 accepted records, with tasks 149 and 454 recorded as unsuccessful |
| Forall-Lean-Agent, GPT-5.6 Sol low through Codex | Rules 100 | 99 accepted records, with task 121 recorded as review exhausted |
| Claude Code, Fable 5 low | Strict 89 | 85 clean targets and 11 forbidden-dependency targets among 96 audited acceptances |

The Forall Opus xhigh snapshot's separate strict rescore is 96, matching the manuscript strict total. Its rules count remains 98 in the retained result files. The reported Sol low total of 100 is an author-confirmed manuscript result whose final additional acceptance is not present in this export's retained snapshot.

## Recovered and cumulative outcomes

Seventeen final Fable reviews say APPROVE although the original verdict parser recorded review exhaustion. Each recovered row has a successful verifier record, successful review compilation evidence, and matching proof-file and recorded SHA-256 digests. These checks support the normalized acceptance while preserving the original status.

The recovered tasks are 4, 14, 122, 123, 126, 131, 132, 136, 139, 147, 149, 150, 249, 271, 381, 444, and 450. All reached review round five.

The Forall Codex xhigh snapshot combines 96 original acceptances, successful fresh retries of tasks 140, 452, and 462, and recovered task 222. Its 100 final acceptances are cumulative. The independent-checker snapshot covers the original accepted set and has 60 acceptances among 67 judged candidates.

The unaided Codex configurations each combine 99 original tasks with recovered task 222. The low and xhigh configurations have 93 and 97 retained acceptances respectively.

## Coverage that remains unavailable

The manuscript gives unaided Fable an independent score of 60/66. A retained checker file with that total has an Opus xhigh filename and a source directory that was reused. The file does not contain candidate digests that would resolve its attribution. It is omitted from the configuration-specific checker export. The ground-truth control is also excluded from agent results.

The complete Numina evaluation has 86 successful task records. Its earlier checker snapshot covered a partial evaluation and is not attached to the final 100-task configuration. Unfinished follow-up sweeps and copied duplicate directories are also excluded.

Other manuscript strict or independent totals with no corresponding exported task-level audit remain reported values. Missing audit rows are not converted to clean verdicts. The coverage columns in [the summary](reports/summary.md) show which claims can be reconstructed from this package.
