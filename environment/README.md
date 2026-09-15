# Environment references

[benchmark.json](benchmark.json) identifies the frozen upstream dataset and 11 repositories represented in the 100-task subset. The local dataset bytes matched the pinned upstream file during export.

Dependency entries are references extracted from the retained benchmark build manifests. No benchmark code, ground-truth proof, dependency source, or build patch is redistributed here.

Task 222 uses the recorded Qq recovery revision while retaining the iris-lean source commit and Lean v4.26.0. Consumers reconstructing an environment should account for that recovery and any upstream benchmark build fixes.

[evaluation.json](evaluation.json) records the manuscript's target protocols and declared execution budgets. It distinguishes samples from reviewer rounds and per-sample compiler limits from per-task compiler limits. These references document the retained evaluation and do not provide the private inference harness.
