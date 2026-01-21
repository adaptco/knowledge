# Threat Model

## Assets
*   **Event Log**: Integrity must be preserved.
*   **Policy Defs**: Must not be tampered with during execution.

## Threats
*   **Log Tampering**: Mitigated by forward-chaining hashes (future feature) and append-only storage.
*   **Bypassing Gates**: Mitigated by cryptographic signatures on gate results.
*   **Malicious Artifacts**: ADK does not execute artifacts, mitigating RCE risks.
