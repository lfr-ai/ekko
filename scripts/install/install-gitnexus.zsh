#!/usr/bin/env zsh
# ==============================================================================
# install-gitnexus.zsh — Install GitNexus code intelligence for ekko
# ==============================================================================
# Usage: ./scripts/install/install-gitnexus.zsh
# Requires: bun (preferred) or node 20+
# ==============================================================================

emulate -L zsh
setopt ERR_EXIT PIPE_FAIL

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------
readonly SCRIPT_DIR="${0:A:h}"
readonly PROJECT_ROOT="${SCRIPT_DIR:h:h}"
readonly MIN_NODE_MAJOR=20
readonly GITNEXUS_PACKAGE="gitnexus@latest"
readonly HOOKS_DIR="${PROJECT_ROOT}/.git/hooks"

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
# verify_runtime
# ------------------------------------------------------------------------------
verify_runtime() {
    step "Verifying JavaScript runtime..."

    RUNTIME=""
    RUNNER=""

    # Prefer bun
    if command_exists bun; then
        local bun_version
        bun_version="$(bun --version 2>/dev/null)"
        ok "bun found: v${bun_version}"
        RUNTIME="bun"
        RUNNER="bunx"
        return 0
    fi

    # Fallback to node
    if command_exists node; then
        local node_version_raw
        node_version_raw="$(node --version 2>/dev/null)"
        local node_major
        node_major="${node_version_raw#v}"
        node_major="${node_major%%.*}"

        if (( node_major >= MIN_NODE_MAJOR )); then
            ok "Node.js found: ${node_version_raw} (>= ${MIN_NODE_MAJOR})"
            RUNTIME="node"
            RUNNER="npx"
            return 0
        else
            warn "Node.js ${node_version_raw} is below minimum v${MIN_NODE_MAJOR}"
        fi
    fi

    die "No suitable JavaScript runtime found. Install bun (preferred) or Node.js >= ${MIN_NODE_MAJOR}."
}

# ------------------------------------------------------------------------------
# install_gitnexus
# ------------------------------------------------------------------------------
install_gitnexus() {
    step "Installing GitNexus..."

    case "${RUNTIME}" in
        bun)
            if command_exists gitnexus; then
                ok "GitNexus is already installed globally"
                info "Updating to latest version..."
                bun install -g "${GITNEXUS_PACKAGE}" 2>/dev/null || {
                    warn "Global install update failed; will use bunx for execution"
                }
            else
                info "Installing GitNexus globally via bun..."
                bun install -g "${GITNEXUS_PACKAGE}" 2>/dev/null || {
                    warn "Global install failed; GitNexus will run via bunx"
                }
            fi
            ;;
        node)
            if command_exists gitnexus; then
                ok "GitNexus is already installed globally"
                info "Updating to latest version..."
                npm install -g "${GITNEXUS_PACKAGE}" 2>/dev/null || {
                    warn "Global install update failed; will use npx for execution"
                }
            else
                info "Installing GitNexus globally via npm..."
                npm install -g "${GITNEXUS_PACKAGE}" 2>/dev/null || {
                    warn "Global install failed; GitNexus will run via npx"
                }
            fi
            ;;
    esac

    ok "GitNexus installation step complete"
}

# ------------------------------------------------------------------------------
# configure_mcp
# ------------------------------------------------------------------------------
configure_mcp() {
    step "Configuring MCP integration..."

    info "Running GitNexus MCP setup..."

    ${RUNNER} "${GITNEXUS_PACKAGE}" setup 2>/dev/null || {
        warn "MCP setup did not complete (may require manual configuration)"
        info "Run manually: ${RUNNER} ${GITNEXUS_PACKAGE} setup"
        return 0
    }

    ok "MCP integration configured"
}

# ------------------------------------------------------------------------------
# index_repository
# ------------------------------------------------------------------------------
index_repository() {
    step "Indexing ekko repository..."

    info "Running initial code analysis (skipping embeddings)..."

    (cd "${PROJECT_ROOT}" && ${RUNNER} "${GITNEXUS_PACKAGE}" analyze . --skip-embeddings) 2>/dev/null || {
        warn "Initial indexing did not complete"
        info "Run manually: cd ${PROJECT_ROOT} && ${RUNNER} ${GITNEXUS_PACKAGE} analyze . --skip-embeddings"
        return 0
    }

    ok "Repository indexed"
}

# ------------------------------------------------------------------------------
# install_hooks
# ------------------------------------------------------------------------------
install_hooks() {
    step "Installing Git hooks for incremental indexing..."

    if [[ ! -d "${HOOKS_DIR}" ]]; then
        warn "Git hooks directory not found: ${HOOKS_DIR}"
        info "Ensure you are in a Git repository"
        return 0
    fi

    local hook_file="${HOOKS_DIR}/post-commit"
    local hook_marker="# >>> gitnexus incremental index >>>"

    # Check if hook already exists
    if [[ -f "${hook_file}" ]] && grep -qF "${hook_marker}" "${hook_file}" 2>/dev/null; then
        ok "post-commit hook already configured"
        return 0
    fi

    # Append to existing hook or create new one
    if [[ -f "${hook_file}" ]]; then
        info "Appending GitNexus hook to existing post-commit..."
    else
        info "Creating post-commit hook..."
        printf "#!/usr/bin/env sh\n" > "${hook_file}"
        chmod +x "${hook_file}"
    fi

    cat >> "${hook_file}" <<HOOK

${hook_marker}
# Incremental GitNexus indexing after each commit
if command -v ${RUNNER} >/dev/null 2>&1; then
    ${RUNNER} ${GITNEXUS_PACKAGE} analyze . --incremental --skip-embeddings >/dev/null 2>&1 &
fi
# <<< gitnexus incremental index <<<
HOOK

    ok "post-commit hook installed for incremental indexing"
}

# ------------------------------------------------------------------------------
# generate_skills
# ------------------------------------------------------------------------------
generate_skills() {
    step "Generating code intelligence skills..."

    info "Running skill generation from code analysis..."

    (cd "${PROJECT_ROOT}" && ${RUNNER} "${GITNEXUS_PACKAGE}" analyze --skills) 2>/dev/null || {
        warn "Skill generation did not complete"
        info "Run manually: cd ${PROJECT_ROOT} && ${RUNNER} ${GITNEXUS_PACKAGE} analyze --skills"
        return 0
    }

    ok "Code intelligence skills generated"
}

# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------
main() {
    printf "\n"
    info "============================================="
    info "  ekko -- GitNexus Code Intelligence Installer"
    info "============================================="
    printf "\n"

    verify_runtime
    install_gitnexus
    configure_mcp
    index_repository
    install_hooks
    generate_skills

    printf "\n"
    ok "GitNexus setup complete for ekko."
    info "Usage:"
    info "  ${RUNNER} ${GITNEXUS_PACKAGE} status        -- Check index status"
    info "  ${RUNNER} ${GITNEXUS_PACKAGE} analyze .     -- Re-index repository"
    info "  ${RUNNER} ${GITNEXUS_PACKAGE} clean         -- Clear index cache"
    printf "\n"
}

main "$@"
