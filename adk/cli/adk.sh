#!/bin/bash
set -e

COMMAND=$1
shift

case "$COMMAND" in
  validate)
    /app/commands/validate.sh "$@"
    ;;
  run)
    /app/commands/run_golden_path.sh "$@"
    ;;
  pack)
    /app/commands/pack.sh "$@"
    ;;
  verify)
    /app/commands/verify.sh "$@"
    ;;
  *)
    echo "Usage: adk.sh {validate|run|pack|verify} [args...]"
    exit 1
    ;;
esac
