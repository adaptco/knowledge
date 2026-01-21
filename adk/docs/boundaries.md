# Boundaries

## The ADK IS

* **A Validation Surface**: It accepts evidence and validates it against policy.
* **A Log**: It records what happened in an immutable ledger.
* **A Gating Mechanism**: It provides a deterministic GO/NO-GO signal.

## The ADK IS NOT

* **An Orchestrator**: It does not schedule jobs or manage resources.
* **A Build System**: It does not know how to compile C++ or transpile TS.
* **An Agent**: It does not "decide" to deploy; it "verifies" a decision to deploy.

## Security Boundary

The ADK does not execute arbitrary code from artifacts. It only parses metadata and executes pre-approved policy logic defined in the `contracts`.
