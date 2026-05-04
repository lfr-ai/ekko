#!/usr/bin/env zsh
# ==============================================================================
# install-zsh.zsh — Install ZSH, Oh-My-Zsh, and plugins for ekko
# ==============================================================================
# Usage: ./scripts/install/install-zsh.zsh
# Platforms: Linux, macOS, WSL
# ==============================================================================

emulate -L zsh
setopt ERR_EXIT PIPE_FAIL

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------
readonly SCRIPT_DIR="${0:A:h}"
readonly PROJECT_ROOT="${SCRIPT_DIR:h:h}"
readonly OMZ_INSTALL_URL="https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"
readonly ZSH_CUSTOM="${ZSH_CUSTOM:-${HOME}/.oh-my-zsh/custom}"

# Plugin repositories
readonly PLUGIN_AUTOSUGGESTIONS="https://github.com/zsh-users/zsh-autosuggestions.git"
readonly PLUGIN_SYNTAX_HIGHLIGHTING="https://github.com/zsh-users/zsh-syntax-highlighting.git"
readonly PLUGIN_COMPLETIONS="https://github.com/zsh-users/zsh-completions.git"
readonly PLUGIN_FZF="https://github.com/junegunn/fzf.git"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
info()  { printf "${BLUE}[INFO]${NC}  %s\n" "$1"; }
ok()    { printf "${GREEN}[OK]${NC}    %s\n" "$1"; }
warn()  { printf "${YELLOW}[WARN]${NC}  %s\n" "$1"; }
err()   { printf "${RED}[ERR]${NC}   %s\n" "$1" >&2; }
step()  { printf "${CYAN}[STEP]${NC}  %s\n" "$1"; }

die() {
    err "$1"
    exit 1
}

command_exists() {
    command -v "$1" &>/dev/null
}

# ------------------------------------------------------------------------------
# detect_platform
# ------------------------------------------------------------------------------
detect_platform() {
    local uname_s
    uname_s="$(uname -s)"

    case "${uname_s}" in
        Linux)
            if [[ -f /proc/version ]] && grep -qi microsoft /proc/version 2>/dev/null; then
                PLATFORM="wsl"
            else
                PLATFORM="linux"
            fi
            ;;
        Darwin)
            PLATFORM="macos"
            ;;
        *)
            die "Unsupported platform: ${uname_s}"
            ;;
    esac

    info "Detected platform: ${PLATFORM}"
}

# ------------------------------------------------------------------------------
# install_zsh
# ------------------------------------------------------------------------------
install_zsh() {
    step "Checking ZSH installation..."

    if command_exists zsh; then
        ok "ZSH is already installed: $(zsh --version)"
        return 0
    fi

    info "Installing ZSH..."

    case "${PLATFORM}" in
        macos)
            if command_exists brew; then
                brew install zsh
            else
                die "Homebrew is required on macOS. Install from https://brew.sh"
            fi
            ;;
        linux|wsl)
            if command_exists apt-get; then
                sudo apt-get update -qq
                sudo apt-get install -y zsh
            elif command_exists dnf; then
                sudo dnf install -y zsh
            elif command_exists pacman; then
                sudo pacman -S --noconfirm zsh
            elif command_exists zypper; then
                sudo zypper --non-interactive install zsh
            else
                die "No supported package manager found. Install ZSH manually."
            fi
            ;;
    esac

    ok "ZSH installed: $(zsh --version)"
}

# ------------------------------------------------------------------------------
# install_oh_my_zsh
# ------------------------------------------------------------------------------
install_oh_my_zsh() {
    step "Checking Oh-My-Zsh installation..."

    if [[ -d "${HOME}/.oh-my-zsh" ]]; then
        ok "Oh-My-Zsh is already installed"
        return 0
    fi

    info "Installing Oh-My-Zsh..."

    # Install non-interactively, keeping existing .zshrc
    sh -c "$(curl -fsSL ${OMZ_INSTALL_URL})" "" --unattended --keep-zshrc || true

    if [[ -d "${HOME}/.oh-my-zsh" ]]; then
        ok "Oh-My-Zsh installed successfully"
    else
        die "Oh-My-Zsh installation failed"
    fi
}

# ------------------------------------------------------------------------------
# install_plugins
# ------------------------------------------------------------------------------
install_plugins() {
    step "Installing ZSH plugins..."

    local plugins_dir="${ZSH_CUSTOM}/plugins"
    mkdir -p "${plugins_dir}"

    # zsh-autosuggestions
    if [[ -d "${plugins_dir}/zsh-autosuggestions" ]]; then
        ok "zsh-autosuggestions already installed"
    else
        info "Installing zsh-autosuggestions..."
        git clone --depth 1 "${PLUGIN_AUTOSUGGESTIONS}" "${plugins_dir}/zsh-autosuggestions"
        ok "zsh-autosuggestions installed"
    fi

    # zsh-syntax-highlighting
    if [[ -d "${plugins_dir}/zsh-syntax-highlighting" ]]; then
        ok "zsh-syntax-highlighting already installed"
    else
        info "Installing zsh-syntax-highlighting..."
        git clone --depth 1 "${PLUGIN_SYNTAX_HIGHLIGHTING}" "${plugins_dir}/zsh-syntax-highlighting"
        ok "zsh-syntax-highlighting installed"
    fi

    # zsh-completions
    if [[ -d "${plugins_dir}/zsh-completions" ]]; then
        ok "zsh-completions already installed"
    else
        info "Installing zsh-completions..."
        git clone --depth 1 "${PLUGIN_COMPLETIONS}" "${plugins_dir}/zsh-completions"
        ok "zsh-completions installed"
    fi

    # fzf
    if command_exists fzf; then
        ok "fzf already installed"
    else
        info "Installing fzf..."
        case "${PLATFORM}" in
            macos)
                if command_exists brew; then
                    brew install fzf
                    "$(brew --prefix)/opt/fzf/install" --key-bindings --completion --no-update-rc --no-bash --no-fish
                fi
                ;;
            linux|wsl)
                if command_exists apt-get; then
                    sudo apt-get install -y fzf
                elif command_exists dnf; then
                    sudo dnf install -y fzf
                elif command_exists pacman; then
                    sudo pacman -S --noconfirm fzf
                else
                    # Fallback: install from git
                    git clone --depth 1 "${PLUGIN_FZF}" "${HOME}/.fzf"
                    "${HOME}/.fzf/install" --key-bindings --completion --no-update-rc --no-bash --no-fish
                fi
                ;;
        esac
        ok "fzf installed"
    fi

    ok "All ZSH plugins installed"
}

# ------------------------------------------------------------------------------
# configure_zshrc
# ------------------------------------------------------------------------------
configure_zshrc() {
    step "Configuring .zshrc..."

    local zshrc="${HOME}/.zshrc"

    # Backup existing .zshrc
    if [[ -f "${zshrc}" ]]; then
        local backup="${zshrc}.backup.$(date +%Y%m%d%H%M%S)"
        cp "${zshrc}" "${backup}"
        info "Backed up existing .zshrc to ${backup}"
    fi

    # Ensure .zshrc exists
    [[ -f "${zshrc}" ]] || touch "${zshrc}"

    # -- Plugin list -----------------------------------------------------------
    local plugin_line='plugins=(git zsh-autosuggestions zsh-syntax-highlighting zsh-completions fzf docker)'

    if grep -q '^plugins=' "${zshrc}" 2>/dev/null; then
        # Replace existing plugins line
        sed -i.bak "s/^plugins=.*/${plugin_line}/" "${zshrc}"
        rm -f "${zshrc}.bak"
        ok "Updated plugins list in .zshrc"
    else
        # Append plugins line
        printf "\n# Plugins (managed by ekko install-zsh.zsh)\n%s\n" "${plugin_line}" >> "${zshrc}"
        ok "Added plugins list to .zshrc"
    fi

    # -- fpath for zsh-completions ---------------------------------------------
    local fpath_line='fpath+=${ZSH_CUSTOM:-${ZSH:-~/.oh-my-zsh}/custom}/plugins/zsh-completions/src'
    if ! grep -qF 'zsh-completions/src' "${zshrc}" 2>/dev/null; then
        # Insert before the Oh-My-Zsh source line if it exists
        if grep -q 'source.*oh-my-zsh.sh' "${zshrc}" 2>/dev/null; then
            sed -i.bak "/source.*oh-my-zsh.sh/i\\
${fpath_line}" "${zshrc}"
            rm -f "${zshrc}.bak"
        else
            printf "\n%s\n" "${fpath_line}" >> "${zshrc}"
        fi
        ok "Added zsh-completions fpath"
    fi

    # -- ekko aliases and environment ------------------------------------------
    local ekko_marker="# >>> ekko shell config >>>"
    if ! grep -qF "${ekko_marker}" "${zshrc}" 2>/dev/null; then
        cat >> "${zshrc}" <<'EKKO_CONFIG'

# >>> ekko shell config >>>
# Project environment
export EKKO_ENVIRONMENT="local"

# Aliases
alias ekko-dev="task dev"
alias ekko-test="task test"
alias ekko-lint="task lint"
alias ekko-format="task format"
alias ekko-check="task check"
alias ekko-db="task db:migrate"

# Quick navigation
alias cde="cd ${EKKO_PROJECT_ROOT:-$HOME/projects/ekko}"

# uv shell completion
if command -v uv &>/dev/null; then
    eval "$(uv generate-shell-completion zsh)"
fi

# bun shell completion
if command -v bun &>/dev/null; then
    eval "$(bun completions)"
fi

# task shell completion
if command -v task &>/dev/null; then
    eval "$(task --completion zsh)"
fi
# <<< ekko shell config <<<
EKKO_CONFIG

        ok "Added ekko aliases and completions to .zshrc"
    else
        info "ekko shell config already present in .zshrc"
    fi

    ok ".zshrc configured"
}

# ------------------------------------------------------------------------------
# set_default_shell
# ------------------------------------------------------------------------------
set_default_shell() {
    step "Setting ZSH as default shell..."

    local zsh_path
    zsh_path="$(command -v zsh)"

    if [[ "${SHELL}" == "${zsh_path}" ]]; then
        ok "ZSH is already the default shell"
        return 0
    fi

    # Ensure zsh is in /etc/shells
    if ! grep -qF "${zsh_path}" /etc/shells 2>/dev/null; then
        info "Adding ${zsh_path} to /etc/shells..."
        printf "%s\n" "${zsh_path}" | sudo tee -a /etc/shells >/dev/null
    fi

    info "Changing default shell to ZSH..."
    chsh -s "${zsh_path}" || {
        warn "Could not change default shell automatically."
        info "Run manually: chsh -s ${zsh_path}"
    }

    ok "Default shell set to ZSH"
}

# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------
main() {
    printf "\n"
    info "============================================="
    info "  ekko -- ZSH + Oh-My-Zsh Installer"
    info "============================================="
    printf "\n"

    detect_platform
    install_zsh
    install_oh_my_zsh
    install_plugins
    configure_zshrc
    set_default_shell

    printf "\n"
    ok "ZSH + Oh-My-Zsh setup complete for ekko."
    info "Restart your terminal or run: source ~/.zshrc"
    printf "\n"
}

main "$@"
