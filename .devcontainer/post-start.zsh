#!/usr/bin/env zsh

# Runs each time the container starts.
setopt err_exit no_unset pipe_fail

# Apply the repository keybindings to the machine-scoped VS Code Server profile.
# Extensions are installed declaratively via customizations.vscode.extensions.
readonly keybindings_source=/workspace/.devcontainer/keybindings.json
readonly keybindings_target=$HOME/.vscode-server/data/Machine/keybindings.json

if [[ -f $keybindings_source ]]; then
  mkdir -p "${keybindings_target:h}"
  cp "$keybindings_source" "$keybindings_target"
fi
