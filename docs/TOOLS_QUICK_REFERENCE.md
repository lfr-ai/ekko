# Development Tools Quick Reference

Quick reference for all development tools configured in Ekko.

## 🚀 Quick Start

```bash
# Check all tool status
task tools:status

# Setup all tools
task tools:setup

# Generate API docs
task tools:openapi:generate
```

## 🛠️ Tools Overview

| Tool | Purpose | Command | Config File |
|------|---------|---------|-------------|
| **CodeRabbit** | AI code review | Auto on PR | `.coderabbit.yaml` |
| **OpenSpec** | API docs | `task tools:openapi:generate` | `backend/src/ekko/config/openapi_config.py` |
| **Warp** | Modern terminal | `task tools:warp:install` | `.warp/` |
| **GitNexus** | Git automation | Auto | `.gitnexus/config.yaml` |
| **Claude** | AI coding | `Ctrl+Shift+I` | `.vscode/settings.json` |
| **Agents** | Custom AI | Chat prefix | `.github/agents/*.agent.md` |

---

## 📝 CodeRabbit

### Quick Actions
```bash
# Validate config
task tools:coderabbit:validate

# Trigger manual review (in PR comment)
@coderabbitai review

# Ask question (in PR comment)
@coderabbitai What's the performance impact of this change?

# Resolve discussion (in PR comment)
@coderabbitai resolve
```

### Review Focus
- ✅ Security vulnerabilities
- ✅ Performance issues
- ✅ Clean Architecture violations
- ✅ Best practices
- ✅ Code style

### Configuration
File: `.coderabbit.yaml`

---

## 📚 OpenAPI Documentation

### Quick Commands
```bash
# Generate all docs
task tools:openapi:generate

# View in browser
task tools:openapi:view

# Check if generated
ls docs/api/
```

### Output Files
- `docs/api/openapi.json` - JSON spec
- `docs/api/openapi.yaml` - YAML spec
- `docs/api/index.html` - Interactive UI

### Live Endpoints
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- JSON: `http://localhost:8000/openapi.json`

### Configuration
File: `backend/src/ekko/config/openapi_config.py`

---

## 🖥️ Warp Terminal

### Quick Setup
```bash
# Install configurations
task tools:warp:install

# Check installation
ls ~/.warp/workflows/ekko-workflows.yaml
```

### Drive Commands
```bash
dev:all          # Start all services
test:watch       # Test watch mode
check:all        # Quality checks
db:migrate       # Run migrations
fix:all          # Auto-fix issues
```

### Common Workflows
- **Initial Setup**: Install dependencies
- **Start Development**: Run dev servers
- **Quality Gate**: Lint + test + typecheck
- **Database Migration**: Create and apply
- **Clean Repository**: Remove artifacts

### Warp AI Usage
```
# Ask in Warp AI panel
"How do I run only backend tests?"
"Start dev server with debug logging"
"Create a new database migration"
```

### Configuration
Files:
- `.warp/launch_configurations/ekko.yaml`
- `.warp/workflows/ekko-workflows.yaml`

---

## 🌳 GitNexus

### Branch Strategy
```
main (protected)
  ├── develop
  │   ├── feature/your-feature
  │   ├── bugfix/your-fix
  │   └── release/vX.Y.Z
```

### Commit Format
```
type(scope): description

Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore
Scopes: core, application, infrastructure, presentation, ai, frontend, etc.

Examples:
feat(audio): add real-time streaming support
fix(api): resolve CORS issue
docs(readme): update setup instructions
```

### Quick Commands
```bash
# Create feature branch
git checkout -b feature/audio-streaming

# Commit with convention
git commit -m "feat(audio): add streaming"

# Validate config
task tools:gitnexus:validate
```

### Auto-Labeling
- `backend/**` → `backend` label
- `frontend/**` → `frontend` label
- `docs/**` → `docs` label
- `**/*.test.*` → `tests` label

### Configuration
File: `.gitnexus/config.yaml`

---

## 🤖 Claude via GitHub Copilot

### Quick Setup
1. Install extensions: `github.copilot`, `github.copilot-chat`
2. Sign in to GitHub Copilot
3. Model already configured: `claude-3.5-sonnet`
4. Test: Open chat (`Ctrl+Shift+I`), ask "What model are you?"

### Usage

**Inline Completions**:
- Start typing → get suggestions
- `Tab` to accept
- `Esc` to reject

**Chat Interface**:
- Open: `Ctrl+Shift+I` or `Cmd+Shift+I`
- Inline: `Ctrl+I` or `Cmd+I`

**Slash Commands**:
- `/explain` - Explain selected code
- `/fix` - Propose fix
- `/tests` - Generate tests
- `/help` - Show commands

**With Context**:
1. Select code
2. Open chat
3. Ask question
4. Get context-aware response

### Configuration
File: `.vscode/settings.json`

```json
{
  "github.copilot.chat.model": "claude-3.5-sonnet"
}
```

---

## 🎭 Custom AI Agents

### Available Agents

| Agent | Prefix | Use For |
|-------|--------|---------|
| **Backend Python** | `As a backend developer:` | FastAPI, SQLAlchemy, Clean Architecture |
| **Frontend React** | `As a frontend developer:` | React, TypeScript, Tailwind |
| **Testing Specialist** | `As a testing specialist:` | pytest, Vitest, E2E tests |
| **Debug Expert** | `As a debug expert:` | Error analysis, performance |

### Usage Examples

**Backend Development**:
```
As a backend developer following Clean Architecture:
Create a new audio processing service with repository pattern.
```

**Frontend Development**:
```
As a frontend developer using React 19:
Create an audio recording component with Zustand state management.
```

**Testing**:
```
As a testing specialist:
Generate comprehensive tests including property-based tests.
```

**Debugging**:
```
As a debug expert:
Analyze this error and suggest fixes:
[paste error]
```

### Configuration
Files: `.github/agents/*.agent.md`

---

## 📋 Common Workflows

### 1. Create New Feature

```bash
# 1. Create branch
git checkout -b feature/real-time-audio

# 2. Ask Claude
"As a backend developer:
Create real-time audio streaming service."

# 3. Implement
[Claude generates code]

# 4. Quality check
task check

# 5. Commit
git commit -m "feat(audio): add real-time streaming"

# 6. Push and create PR
git push origin feature/real-time-audio
gh pr create

# 7. CodeRabbit reviews automatically
# 8. Address feedback
# 9. Merge
```

### 2. Debug Issue

```bash
# 1. Encounter error
[Error occurs]

# 2. Ask Warp AI
"Why is SQLAlchemy session not closing?"

# 3. Ask Claude
"As a debug expert:
Analyze this session management code."

# 4. Fix and test
task test:integration

# 5. Verify
✓ Tests pass
```

### 3. Generate Documentation

```bash
# 1. Generate API docs
task tools:openapi:generate

# 2. View
task tools:openapi:view

# 3. Commit
git add docs/api/
git commit -m "docs(api): update OpenAPI specification"
```

---

## 🔍 Troubleshooting

### CodeRabbit Not Reviewing
```bash
# Check config
task tools:coderabbit:validate

# Manual trigger (PR comment)
@coderabbitai review
```

### Claude Not Active
```bash
# 1. Check model setting
# .vscode/settings.json should have:
# "github.copilot.chat.model": "claude-3.5-sonnet"

# 2. Restart VS Code
# 3. Sign out and sign in to Copilot
```

### Warp Workflows Missing
```bash
# Reinstall
task tools:warp:install

# Restart Warp
```

### OpenAPI Generation Failed
```bash
# Check dependencies
cd backend
uv sync

# Retry
task tools:openapi:generate
```

---

## 📚 Documentation

### Quick Links
- [Complete Setup](docs/TOOLS_SETUP_GUIDE.md) - 13.7KB
- [Claude Guide](docs/CLAUDE_COPILOT_GUIDE.md) - 11KB
- [Agents Guide](.github/agents/README.md) - 11.5KB
- [Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md) - 17KB

### In-File Documentation
- `.coderabbit.yaml` - Inline comments
- `.gitnexus/config.yaml` - Inline comments
- `.warp/` files - Inline comments
- `.github/agents/*.agent.md` - Detailed instructions

---

## ⚡ Keyboard Shortcuts

### VS Code
| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| Open chat | `Ctrl+Shift+I` | `Cmd+Shift+I` |
| Inline chat | `Ctrl+I` | `Cmd+I` |
| Accept suggestion | `Tab` | `Tab` |
| Reject suggestion | `Esc` | `Esc` |

### Warp
| Action | Shortcut |
|--------|----------|
| Command palette | `Ctrl+Shift+P` |
| AI assistant | `Ctrl+~` |
| Search | `Ctrl+F` |

---

## 🎯 Task Commands

### Tool Management
```bash
task tools:status                  # Check all tools
task tools:setup                   # Setup all tools
task tools:openapi:generate        # Generate API docs
task tools:openapi:view            # View API docs
task tools:coderabbit:validate     # Validate CodeRabbit
task tools:gitnexus:validate       # Validate GitNexus
task tools:warp:install            # Install Warp configs
```

### Development
```bash
task dev                           # Start all services
task dev:backend                   # Backend only
task dev:frontend                  # Frontend only
```

### Quality
```bash
task check                         # Full quality gate
task lint                          # Run linters
task typecheck                     # Type checking
task test                          # Run tests
task format                        # Format code
```

### Database
```bash
task db:migrate                    # Run migrations
task db:reset                      # Reset database
```

---

## 📞 Getting Help

### In VS Code
```
# Ask Claude
"How do I create a new API endpoint?"
"What's the Clean Architecture pattern for repositories?"
"Generate tests for this function"
```

### In Warp
```
# Ask Warp AI
"How do I run only unit tests?"
"Start development server with debug logging"
```

### In PR
```
# Ask CodeRabbit
@coderabbitai What's the performance impact?
@coderabbitai How can I improve this?
```

---

## ✅ Verification

```bash
# Quick health check
task tools:status

# Full quality check
task check

# Test everything works
task dev
# Wait for servers to start
# Visit http://localhost:8000/docs
# Visit http://localhost:5173
```

---

**Last Updated**: May 2, 2026  
**Tools Version**: 1.0.0  
**Status**: Production Ready

For detailed information, see full guides in `docs/` directory.
