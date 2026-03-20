#!/usr/bin/env bash
# Run humanql CLI with PYTHONPATH set; forwards all arguments.
set -e
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}src"
exec python -m humanql "$@"
