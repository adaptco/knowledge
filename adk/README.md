# Artifact Development Kit (ADK) - RC0

The **ADK** is a reference implementation of the "Control Surface Contracts" standard. It provides a deterministic, secure, and rigorous way to manage software delivery artifacts, event logs, and release gates.

## What It Is
- **Validation-First**: Enforces strict JSON schemas for all artifacts and events.
- **Deterministic**: Replay logs to reconstruct state perfectly.
- **Contract-Based**: "Tooling as Contract" — the schema is the policy.

## What It Is Not
- **Autonomous Agent**: It does not make decisions; it verifies them.
- **Build Tool**: It does not compile your code; it wraps your build in evidence.

## Quick Start (Docker)

**Windows (PowerShell)**
```powershell
# Validate the contracts
.\adk.ps1 validate contracts

# Run the golden path example
.\adk.ps1 run examples/golden_path
```

**Linux / Mac**
```bash
# Validate the contracts
./adk validate contracts

# Run the golden path example
./adk run examples/golden_path
```

## Documentation
See [docs/boundary.md](docs/boundary.md) for architectural boundaries.
