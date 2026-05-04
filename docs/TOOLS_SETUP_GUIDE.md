# Ekko Development Tools Setup Guide

This guide provides comprehensive instructions for setting up all development tools for the Ekko project.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Core Development Environment](#core-development-environment)
3. [AI Coding Assistants](#ai-coding-assistants)
4. [Code Review Tools](#code-review-tools)
5. [Terminal Setup](#terminal-setup)
6. [Git Workflow Tools](#git-workflow-tools)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| Python | 3.12+ | Backend runtime | [python.org](https://python.org) |
| uv | latest | Python package manager | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js | 20+ | Frontend tooling | [nodejs.org](https://nodejs.org) |
| Bun | latest | Frontend package manager | `curl -fsSL https://bun.sh/install \| bash` |
| Task | latest | Task runner | `brew install go-task` (macOS) |
| Git | 2.40+ | Version control | [git-scm.com](https://git-scm.com) |

### Optional Software

| Tool | Purpose | Installation |
|------|---------|--------------|
| Warp | Modern terminal with AI | [warp.dev](https://www.warp.dev/) |
| VS Code | Code editor | [code.visualstudio.com](https://code.visualstudio.com/) |
| Docker | Containerization | [docker.com](https://www.docker.com/) |

---

## Core Development Environment

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/ekko.git
cd ekko
```

### 2. Install Dependencies

```bash
# Install all project dependencies
task install
```

This will:

- Install Python dependencies via `uv`
- Install frontend dependencies via `bun`
- Setup virtual environments
- Configure pre-commit hooks

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env.local

# Edit with your settings
nano .env.local
```

Required environment variables:

- `OPENAI_API_KEY` - OpenAI API key for LLM features
- `EKKO_ENVIRONMENT` - Set to `local` for development

### 4. Initialize Database

```bash
# Run database migrations
task db:migrate
```

### 5. Verify Setup

```bash
# Run full quality check
task check
```

This runs:

- ✓ Linting (ruff, biome, mypy)
- ✓ Type checking
- ✓ Unit tests
- ✓ Code complexity check

### 6. Start Development Servers

```bash
# Start both backend and frontend
task dev

# Or individually:
task dev:backend   # Backend only (port 8000)
task dev:frontend  # Frontend only (port 5173)
```

---

## AI Coding Assistants

### GitHub Copilot with Claude

#### Setup

1. **Install VS Code Extensions**

   ```bash
   code --install-extension github.copilot
   code --install-extension github.copilot-chat
   ```

2. **Sign in to GitHub Copilot**
   - Open VS Code
   - Click "Sign in to use GitHub Copilot"
   - Authenticate with your GitHub account
   - Ensure you have GitHub Copilot subscription

3. **Enable Claude Model**

   In Copilot Chat, use the model picker and select an available Claude model for your account/plan.

4. **Verify Claude is Active**
   - Open GitHub Copilot Chat (`Ctrl+Shift+I` or `Cmd+Shift+I`)
   - Ask: "What model are you?"
   - Should respond with a Claude model name

#### Features

- **Inline Completions**: Real-time code suggestions as you type
- **Chat Interface**: Ask questions about code, generate tests, explain code
- **Agent Customization**: Project-specific instructions from `.github/agents/`
- **Context Awareness**: Understands Clean Architecture patterns

#### Usage

See [docs/CLAUDE_COPILOT_GUIDE.md](../docs/CLAUDE_COPILOT_GUIDE.md) for comprehensive guide.

**Quick Examples**:

```text
# Generate endpoint
"Create a new FastAPI endpoint for audio transcription following Clean Architecture"

# Refactor code
"Refactor this service to use async/await properly"

# Generate tests
"Generate comprehensive tests for this function including edge cases"

# Explain code
"Explain how this CrewAI agent configuration works"
```

---

## Code Review Tools

### CodeRabbit (AI Code Review)

CodeRabbit provides automated AI-powered code reviews on pull requests.

#### Setup

1. **Install GitHub App**
   - Go to [coderabbit.ai](https://coderabbit.ai/)
   - Click "Install on GitHub"
   - Select your repository
   - Authorize the app

2. **Verify Configuration**

   The project includes `.coderabbit.yaml`:

   ```bash
   task tools:coderabbit:validate
   ```

3. **Configure Review Settings**

   Edit `.coderabbit.yaml` to customize:
   - Review focus areas
   - Language-specific rules
   - Auto-review triggers
   - Comment verbosity

#### Features

- ✅ Automatic PR reviews
- ✅ Security vulnerability detection
- ✅ Performance issue identification
- ✅ Clean Architecture validation
- ✅ Code style suggestions
- ✅ Test coverage analysis

#### Usage

1. Create a pull request
2. CodeRabbit automatically reviews within 1-2 minutes
3. Review comments appear in PR
4. Address feedback or ask questions
5. CodeRabbit re-reviews on updates

**Pro Tips**:

- Tag `@coderabbitai` to ask specific questions
- Use `@coderabbitai review` to trigger manual review
- Use `@coderabbitai resolve` to mark issues as resolved

---

## Terminal Setup

### Warp Terminal

Warp is a modern, AI-powered terminal with built-in workflows.

#### Installation

```bash
# macOS
brew install --cask warp

# Or download from warp.dev
```

#### Configuration

1. **Install Project Workflows**

   ```bash
   task tools:warp:install
   ```

   This copies:
   - Launch configurations
   - Workflow definitions
   - AI context settings

2. **Open Warp**

   ```bash
   warp
   ```

3. **Select Ekko Configuration**
   - Click "Launch Configurations" in Warp
   - Select "Ekko Development"
   - Terminal opens with project context

#### Features

- 🚀 **Workflows**: Pre-configured command sequences
- 🤖 **AI Command Search**: Natural language command finding
- 📝 **Command Palette**: Quick access to common tasks
- 💾 **Session Replay**: Review command history
- 🔍 **Inline Search**: Search output in real-time

#### Available Workflows

See `.warp/workflows/ekko-workflows.yaml` for complete list.

**Common Workflows**:

```bash
# In Warp command palette (Ctrl+Shift+P):
- "Start Development" → Runs task dev
- "Run All Tests" → Runs full test suite
- "Quality Gate" → Runs lint + typecheck + test
- "Database Migration" → Creates and applies migration
- "Clean Repository" → Removes all build artifacts
```

**Drive Commands** (saved shortcuts):

```bash
dev:all        # Start all services
test:watch     # Run tests in watch mode
check:all      # Run all quality checks
db:migrate     # Run database migrations
fix:all        # Auto-fix all fixable issues
```

#### AI Features

Warp's AI assistant understands the project context:

```bash
# Ask questions in Warp AI
"How do I run only the backend tests?"
→ Suggests: cd backend && uv run pytest

"Start the development server with debug logging"
→ Suggests: LOG_LEVEL=DEBUG task dev

"Create a new database migration"
→ Suggests: cd backend && uv run alembic revision --autogenerate -m "description"
```

---

## Git Workflow Tools

### GitNexus

GitNexus provides advanced Git workflow automation.

#### Configuration

The project includes `.gitnexus/config.json` with:

- Branch protection rules
- Auto-labeling
- PR templates
- Release automation
- Commit conventions

#### Verify Setup

```bash
task tools:gitnexus:validate
```

#### Features

**Branch Management**:

- `feature/*` - Feature branches (auto-delete on merge)
- `bugfix/*` - Bug fix branches
- `release/*` - Release branches
- Automatic branch protection

**Commit Conventions**:

- Enforces Conventional Commits format
- Validates commit messages
- Auto-generates changelogs

**PR Automation**:

- Auto-assigns reviewers based on file paths
- Auto-labels based on changes
- Requires status checks before merge
- Blocks merge on test failures

**Release Management**:

- Semantic versioning (semver)
- Automatic changelog generation
- Draft releases for review
- Pre-release support (alpha, beta, rc)

#### Usage

**Creating Feature Branch**:

```bash
git checkout main
git pull
git checkout -b feature/audio-streaming
```

**Committing Changes**:

```bash
# Format: type(scope): description
git commit -m "feat(audio): add real-time streaming support"
git commit -m "fix(api): resolve CORS issue in health endpoint"
git commit -m "docs(readme): update installation instructions"
```

**Valid Commit Types**:

- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Code style (formatting)
- `refactor` - Code refactoring
- `perf` - Performance improvement
- `test` - Adding/updating tests
- `build` - Build system changes
- `ci` - CI configuration
- `chore` - Other changes

---

## OpenAPI Documentation

### Generate API Documentation

```bash
# Generate OpenAPI specs (JSON, YAML, HTML)
task tools:openapi:generate

# View in browser
task tools:openapi:view
```

This creates:

- `docs/api/openapi.json` - JSON specification
- `docs/api/openapi.yaml` - YAML specification
- `docs/api/index.html` - Interactive Swagger UI

### Configuration

See `backend/src/ekko/config/openapi_config.py` for:

- API metadata
- Server configurations
- Tag definitions
- Response examples
- Security schemes

### Integration

The OpenAPI spec is automatically served by FastAPI:

- JSON: `http://localhost:8000/openapi.json`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Verification

### Check All Tools

```bash
# Check status of all configured tools
task tools:status
```

Expected output:

```text
=== Tool Configuration Status ===

CodeRabbit:
  ✓ Configured (.coderabbit.yaml)

GitNexus:
   ✓ Configured (.gitnexus/config.json)

OpenAPI:
  ✓ Generated (docs/api/)

Warp:
  ✓ Project configs present

VS Code:
  ✓ Configured (.vscode/settings.json)
  ✓ Claude via GitHub Copilot configured
```

### Run Quality Checks

```bash
# Full quality gate
task check
```

This verifies:

- ✓ Code linting (Python + TypeScript)
- ✓ Type checking (mypy + tsc)
- ✓ Unit tests
- ✓ Code complexity (xenon)
- ✓ Architecture boundaries

### Test Development Workflow

```bash
# Start development
task dev

# In another terminal, run tests
task test

# Format and lint
task format
task lint

# Generate OpenAPI docs
task tools:openapi:generate
```

---

## Troubleshooting

### GitHub Copilot Issues

**Issue**: Copilot not suggesting Claude completions

**Solution**:

1. Verify subscription includes model selection
2. Restart VS Code
3. Open Copilot Chat and confirm a Claude model is selected in the model picker
4. Sign out and sign in to GitHub Copilot

**Issue**: Agent instructions not working

**Solution**:

1. Verify `.github/copilot-instructions.md` exists
2. Check `chat.instructionsFilesLocations` in settings
3. Restart VS Code to reload instructions

### CodeRabbit Issues

**Issue**: CodeRabbit not reviewing PRs

**Solution**:

1. Verify GitHub App is installed
2. Check repository permissions
3. Ensure `.coderabbit.yaml` is valid YAML
4. Try manual trigger: comment `@coderabbitai review` on PR

### Warp Issues

**Issue**: Warp workflows not appearing

**Solution**:

1. Run `task tools:warp:install` to copy configs
2. Restart Warp terminal
3. Check `~/.warp/workflows/` for ekko-workflows.yaml
4. Verify YAML syntax

**Issue**: Warp AI not understanding project context

**Solution**:

1. Ensure `.warp/launch_configurations/ekko.yaml` is loaded
2. Use "Launch Configurations" → "Ekko Development"
3. Check AI context section in config file

### GitNexus Issues

**Issue**: Branch protection not working

**Solution**:

1. Verify `.gitnexus/config.json` is valid
2. Check GitHub repository settings
3. Ensure branch protection rules are enabled
4. Verify you have admin permissions

### Build Issues

**Issue**: Dependencies not installing

**Solution**:

```bash
# Backend
cd backend
uv sync --reinstall

# Frontend
cd frontend
rm -rf node_modules
bun install
```

**Issue**: Database migrations failing

**Solution**:

```bash
# Reset database
rm backend/ekko.db
task db:migrate
```

**Issue**: Tests failing

**Solution**:

```bash
# Clear caches
rm -rf backend/.pytest_cache
rm -rf backend/.ruff_cache
rm -rf backend/.mypy_cache

# Run tests with verbose output
cd backend
uv run pytest -v
```

---

## Additional Resources

### Documentation

- [Claude + Copilot Guide](../docs/CLAUDE_COPILOT_GUIDE.md)
- [Clean Architecture](../.github/skills/clean-architecture/SKILL.md)
- [Python Conventions](../.github/skills/python-conventions/SKILL.md)
- [Frontend Stack](../.github/skills/frontend-react-stack/SKILL.md)
- [Testing Conventions](../.github/skills/testing-conventions/SKILL.md)

### External Links

- [GitHub Copilot Docs](https://docs.github.com/en/copilot)
- [CodeRabbit Docs](https://docs.coderabbit.ai/)
- [Warp Terminal Docs](https://docs.warp.dev/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React 19 Docs](https://react.dev/)

### Getting Help

- **GitHub Discussions**: Ask questions in project discussions
- **GitHub Issues**: Report bugs or request features
- **Copilot Chat**: Ask `@github.copilot` questions in VS Code
- **Warp AI**: Ask questions in Warp terminal's AI assistant

---

## Next Steps

After completing this setup:

1. ✅ Read [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines
2. ✅ Review [ARCHITECTURE.md](../docs/ARCHITECTURE.md) for system design
3. ✅ Explore [.github/agents/](../.github/agents/) for specialized AI agents
4. ✅ Run `task --list` to see all available commands
5. ✅ Start coding! Use `task dev` to begin development

---

**Happy coding! 🚀**

For questions or issues, open a GitHub issue or discussion.
