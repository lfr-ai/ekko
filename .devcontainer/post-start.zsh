#!/usr/bin/env zsh

setopt err_exit no_unset pipe_fail

local readonly kb="/workspace/.devcontainer/keybindings.json"
local readonly kb_target="${HOME}/.vscode-server/data/Machine/keybindings.json"
[[ -f "${kb}" ]] && { mkdir -p "${kb_target:h}"; cp "${kb}" "${kb_target}"; }

local readonly ext_file="/workspace/.devcontainer/extensions.json"
local -a code_servers=("${HOME}"/.vscode-server/bin/*/bin/code-server(Nom))
[[ ${#code_servers} -eq 0 || ! -f "${ext_file}" ]] && exit 0

local readonly cs="${code_servers[1]}"
local -a exts=("${(f)$(python3 -c "import json,sys;[print(e) for e in json.load(sys.stdin) if isinstance(e,str)]" < "${ext_file}")}")

for ext in $exts; do
  [[ -z "${ext}" ]] && continue
  "${cs}" --install-extension "${ext}" --force &>/dev/null \
    || "${cs}" --install-extension "${ext}" --force &>/dev/null || true
done

# Ensure OpenSpec CLI is available for spec-driven workflow in the container.
if ! command -v openspec &>/dev/null; then
  npm install -g @fission-ai/openspec@latest &>/dev/null || true
fi

# Soft check for GitNexus CLI.
if ! command -v gitnexus &>/dev/null; then
  print -P "%F{yellow}[devcontainer]%f gitnexus CLI not found; install it to enable local graph analysis."
fi
