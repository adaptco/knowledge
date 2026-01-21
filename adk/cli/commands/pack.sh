#!/bin/bash
set -e

echo "Packing contracts..."
tar -czf adk-contracts-v0.tar.gz -C /app contracts
sha256sum adk-contracts-v0.tar.gz > adk-contracts-v0.tar.gz.sha256
echo "Pack complete: adk-contracts-v0.tar.gz"
