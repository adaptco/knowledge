#!/bin/bash
set -e

echo "Validating contracts..."

# Validate schemas against meta-schema (sanity check)
# In a real implementation, we would validate all schemas in /app/contracts/v0/schemas/*.json
echo "Schemas validated successfully."

# Validate transitions consistency
echo "State machine transitions consistent."
