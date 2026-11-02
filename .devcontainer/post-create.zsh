#!/usr/bin/env zsh

# Runs once after the workspace is mounted into a newly created container.
setopt err_exit no_unset pipe_fail

readonly openspec_version=1.13.2
readonly gitnexus_version=1.6.9

echo "Installing backend and frontend dependencies..."
task install

echo "Installing the Playwright Chromium browser with system dependencies..."
(cd frontend && bunx playwright install --with-deps chromium)

echo "Installing repository CLI tools..."
bun add --global \
  "@fission-ai/openspec@${openspec_version}" \
  "gitnexus@${gitnexus_version}"

echo "Verifying development toolchain..."
uv --version
task --version
node --version
bun --version
openspec --version
gitnexus --version
