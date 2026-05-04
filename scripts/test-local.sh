#!/usr/bin/env bash
set -euo pipefail

# Run unit tests locally with PYTHONPATH set
PYTHONPATH=src pytest -q "$@"
