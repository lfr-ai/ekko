#!/usr/bin/env zsh
# ==============================================================================
# install-warp.zsh — Install Warp terminal and deploy ekko settings
# ==============================================================================
# Usage: ./scripts/install/install-warp.zsh
# Platforms: Linux, macOS, WSL
# ==============================================================================

emulate -L zsh
setopt ERR_EXIT PIPE_FAIL

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------
readonly SCRIPT_DIR="${0:A:h}"
readonly PROJECT_ROOT="${SCRIPT_DIR:h:h}"
readonly WARP_SOURCE_DIR="${PROJECT_ROOT}/.warp"
readonly WARP_GPG_KEY_URL="https://releases.warp.dev/linux/keys/warp.gpg"
readonly WARP_DEB_REPO="https://releases.warp.dev/linux/deb"
readonly WARP_RPM_REPO="https://releases.warp.dev/linux/rpm/stable"

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
        MINGW*|MSYS*|CYGWIN*)
            PLATFORM="windows"
            ;;
        *)
            die "Unsupported platform: ${uname_s}"
            ;;
    esac

    info "Detected platform: ${PLATFORM}"
}

# ------------------------------------------------------------------------------
# detect_linux_distro
# ------------------------------------------------------------------------------
detect_linux_distro() {
    if [[ -f /etc/os-release ]]; then
        # shellcheck disable=SC1091
        source /etc/os-release
        DISTRO_ID="${ID}"
        DISTRO_FAMILY="${ID_LIKE:-${ID}}"
    elif command_exists lsb_release; then
        DISTRO_ID="$(lsb_release -si | tr '[:upper:]' '[:lower:]')"
        DISTRO_FAMILY="${DISTRO_ID}"
    else
        die "Cannot detect Linux distribution"
    fi

    info "Detected distro: ${DISTRO_ID} (family: ${DISTRO_FAMILY})"
}

# ------------------------------------------------------------------------------
# check_existing
# ------------------------------------------------------------------------------
check_existing() {
    if command_exists warp-terminal || command_exists warp; then
        local warp_path
        warp_path="$(command -v warp-terminal 2>/dev/null || command -v warp 2>/dev/null)"
        ok "Warp is already installed: ${warp_path}"
        return 0
    fi
    return 1
}

# ------------------------------------------------------------------------------
# install_warp_linux
# ------------------------------------------------------------------------------
install_warp_linux() {
    detect_linux_distro

    step "Installing Warp terminal on Linux (${DISTRO_ID})..."

    case "${DISTRO_ID}" in
        ubuntu|debian|linuxmint|pop|elementary)
            install_warp_apt
            ;;
        fedora|rhel|centos|rocky|alma)
            install_warp_dnf
            ;;
        arch|manjaro|endeavouros)
            install_warp_pacman
            ;;
        opensuse*|sles)
            install_warp_zypper
            ;;
        *)
            # Try to detect by family
            case "${DISTRO_FAMILY}" in
                *debian*|*ubuntu*)
                    install_warp_apt
                    ;;
                *fedora*|*rhel*)
                    install_warp_dnf
                    ;;
                *arch*)
                    install_warp_pacman
                    ;;
                *suse*)
                    install_warp_zypper
                    ;;
                *)
                    die "Unsupported Linux distribution: ${DISTRO_ID}"
                    ;;
            esac
            ;;
    esac

    ok "Warp installed successfully on Linux"
}

# --- apt-based (Debian/Ubuntu) ------------------------------------------------
install_warp_apt() {
    info "Using apt package manager..."

    # Import GPG key
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL "${WARP_GPG_KEY_URL}" | sudo gpg --dearmor -o /etc/apt/keyrings/warp.gpg

    # Add repository
    printf "deb [arch=amd64 signed-by=/etc/apt/keyrings/warp.gpg] %s stable main\n" \
        "${WARP_DEB_REPO}" | sudo tee /etc/apt/sources.list.d/warp.list >/dev/null

    # Install
    sudo apt-get update -qq
    sudo apt-get install -y warp-terminal

    ok "Warp installed via apt"
}

# --- dnf-based (Fedora/RHEL) --------------------------------------------------
install_warp_dnf() {
    info "Using dnf package manager..."

    # Import GPG key
    sudo rpm --import "${WARP_GPG_KEY_URL}"

    # Add repository
    sudo tee /etc/yum.repos.d/warp.repo >/dev/null <<REPO
[warp-terminal]
name=Warp Terminal
baseurl=${WARP_RPM_REPO}
enabled=1
gpgcheck=1
gpgkey=${WARP_GPG_KEY_URL}
REPO

    sudo dnf install -y warp-terminal

    ok "Warp installed via dnf"
}

# --- pacman-based (Arch) ------------------------------------------------------
install_warp_pacman() {
    info "Using pacman package manager..."

    if command_exists yay; then
        yay -S --noconfirm warp-terminal
    elif command_exists paru; then
        paru -S --noconfirm warp-terminal
    else
        warn "No AUR helper found. Installing yay first..."
        sudo pacman -S --needed --noconfirm base-devel git
        local tmp_dir
        tmp_dir="$(mktemp -d)"
        git clone https://aur.archlinux.org/yay.git "${tmp_dir}/yay"
        (cd "${tmp_dir}/yay" && makepkg -si --noconfirm)
        rm -rf "${tmp_dir}"
        yay -S --noconfirm warp-terminal
    fi

    ok "Warp installed via pacman/AUR"
}

# --- zypper-based (openSUSE) --------------------------------------------------
install_warp_zypper() {
    info "Using zypper package manager..."

    sudo rpm --import "${WARP_GPG_KEY_URL}"
    sudo zypper addrepo -f "${WARP_RPM_REPO}" warp-terminal
    sudo zypper --non-interactive install warp-terminal

    ok "Warp installed via zypper"
}

# ------------------------------------------------------------------------------
# install_warp_macos
# ------------------------------------------------------------------------------
install_warp_macos() {
    step "Installing Warp terminal on macOS..."

    if ! command_exists brew; then
        die "Homebrew is required. Install it from https://brew.sh"
    fi

    brew install --cask warp

    ok "Warp installed successfully on macOS"
}

# ------------------------------------------------------------------------------
# install_warp_wsl
# ------------------------------------------------------------------------------
install_warp_wsl() {
    step "Installing Warp terminal on WSL..."

    if command_exists winget.exe; then
        info "Installing Warp via winget on the Windows host..."
        winget.exe install --id Warp.Warp --accept-source-agreements --accept-package-agreements || true
        ok "Warp installed via winget (Windows host)"
    elif command_exists choco.exe; then
        info "Installing Warp via Chocolatey on the Windows host..."
        choco.exe install warp --yes || true
        ok "Warp installed via Chocolatey (Windows host)"
    else
        warn "Neither winget nor choco found on Windows host."
        info "Download Warp manually from: https://www.warp.dev/download"
        info "After installing, Warp on Windows can connect to your WSL distros."
    fi
}

# ------------------------------------------------------------------------------
# deploy_settings
# ------------------------------------------------------------------------------
deploy_settings() {
    step "Deploying ekko Warp settings..."

    local warp_config_dir

    case "${PLATFORM}" in
        macos)
            warp_config_dir="${HOME}/.warp"
            ;;
        linux)
            warp_config_dir="${HOME}/.warp"
            ;;
        wsl)
            # Warp runs on Windows host; config is in Windows user profile
            local win_home
            win_home="$(cmd.exe /C 'echo %USERPROFILE%' 2>/dev/null | tr -d '\r')" || true
            if [[ -n "${win_home}" ]]; then
                # Convert Windows path to WSL path
                warp_config_dir="$(wslpath "${win_home}")/.warp"
            else
                warp_config_dir="${HOME}/.warp"
                warn "Could not detect Windows home; deploying to WSL home"
            fi
            ;;
        *)
            warp_config_dir="${HOME}/.warp"
            ;;
    esac

    info "Warp config directory: ${warp_config_dir}"

    # Deploy settings.toml
    if [[ -f "${WARP_SOURCE_DIR}/settings.toml" ]]; then
        mkdir -p "${warp_config_dir}"
        cp "${WARP_SOURCE_DIR}/settings.toml" "${warp_config_dir}/settings.toml"
        ok "Deployed settings.toml"
    fi

    # Deploy themes
    if [[ -d "${WARP_SOURCE_DIR}/themes" ]]; then
        mkdir -p "${warp_config_dir}/themes"
        cp "${WARP_SOURCE_DIR}/themes/"*.yaml "${warp_config_dir}/themes/" 2>/dev/null || true
        ok "Deployed themes"
    fi

    # Deploy workflows
    if [[ -d "${WARP_SOURCE_DIR}/workflows" ]]; then
        mkdir -p "${warp_config_dir}/workflows"
        cp "${WARP_SOURCE_DIR}/workflows/"*.yaml "${warp_config_dir}/workflows/" 2>/dev/null || true
        ok "Deployed workflows"
    fi

    # Deploy launch configurations
    if [[ -d "${WARP_SOURCE_DIR}/launch_configurations" ]]; then
        mkdir -p "${warp_config_dir}/launch_configurations"
        cp "${WARP_SOURCE_DIR}/launch_configurations/"*.yaml "${warp_config_dir}/launch_configurations/" 2>/dev/null || true
        ok "Deployed launch configurations"
    fi

    ok "All ekko Warp settings deployed to ${warp_config_dir}"
}

# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------
main() {
    printf "\n"
    info "============================================="
    info "  ekko -- Warp Terminal Installer"
    info "============================================="
    printf "\n"

    detect_platform

    if check_existing; then
        info "Skipping installation (already present)"
    else
        case "${PLATFORM}" in
            linux)   install_warp_linux  ;;
            macos)   install_warp_macos  ;;
            wsl)     install_warp_wsl    ;;
            windows)
                warn "Run this script inside WSL or install Warp directly on Windows."
                info "Download: https://www.warp.dev/download"
                ;;
        esac
    fi

    deploy_settings

    printf "\n"
    ok "Warp terminal setup complete for ekko."
    info "Restart Warp to apply the new theme and settings."
    printf "\n"
}

main "$@"
