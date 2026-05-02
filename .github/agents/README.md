# Agent Customization for VS Code

This document explains how to create and use custom AI agents for VS Code GitHub Copilot.

## Overview

VS Code GitHub Copilot supports custom agent instructions that help tailor AI responses to your project's specific needs, conventions, and architecture.

## Agent Structure

### File Location

Agents are Markdown files stored in:
```
.github/agents/
├── backend-python.agent.md
├── frontend-react.agent.md
├── testing-specialist.agent.md
├── debug.agent.md
└── [your-agent].agent.md
```

### File Format

```markdown
---
description: Brief description of the agent's purpose
category: backend|frontend|testing|devops|security
expertise:
  - Area of expertise 1
  - Area of expertise 2
  - Area of expertise 3
---

# Agent Name

You are an expert in [domain] specializing in [specific areas].

## Core Responsibilities

1. **Responsibility 1**
   - Sub-point
   - Sub-point

2. **Responsibility 2**
   - Sub-point
   - Sub-point

## Code Quality Standards

[Examples and patterns]

## Common Tasks

[Task descriptions and examples]

## Commands

[Relevant commands]
```

## Available Agents

### 1. Backend Python Developer

**File**: `.github/agents/backend-python.agent.md`

**Purpose**: Clean Architecture enforcement, FastAPI patterns, SQLAlchemy best practices

**Use Cases**:
- Creating new API endpoints
- Adding database repositories
- Implementing domain services
- Writing async code
- Error handling patterns

**Activation**:
```
As a backend developer following Clean Architecture:
[your request]
```

### 2. Frontend React Developer

**File**: `.github/agents/frontend-react.agent.md`

**Purpose**: React 19 patterns, TypeScript, Tailwind CSS, shadcn/ui

**Use Cases**:
- Creating React components
- Managing state (Zustand, TanStack Query)
- Styling with Tailwind CSS
- Type-safe development
- Custom hooks

**Activation**:
```
As a frontend developer using React 19:
[your request]
```

### 3. Testing Specialist

**File**: `.github/agents/testing-specialist.agent.md`

**Purpose**: Comprehensive testing strategies (unit, integration, property-based, E2E)

**Use Cases**:
- Writing unit tests
- Creating integration tests
- Property-based testing with Hypothesis/fast-check
- E2E tests with Playwright
- Test fixtures and factories

**Activation**:
```
As a testing specialist:
[your request]
```

### 4. Debug Expert

**File**: `.github/agents/debug.agent.md`

**Purpose**: Error analysis, performance profiling, security auditing

**Use Cases**:
- Debugging runtime errors
- Performance optimization
- Memory leak detection
- Security vulnerability analysis
- Log analysis

**Activation**:
```
As a debug expert:
[your request]
```

## Creating Custom Agents

### Step 1: Define Agent Purpose

Identify:
- What domain does this agent cover?
- What expertise should it have?
- What are the common tasks?
- What conventions must it follow?

### Step 2: Create Agent File

```bash
touch .github/agents/my-agent.agent.md
```

### Step 3: Write Agent Instructions

```markdown
---
description: My specialized agent description
category: my-category
expertise:
  - Skill 1
  - Skill 2
  - Skill 3
---

# My Agent Name

You are an expert in [domain].

## Core Responsibilities

1. **Primary Responsibility**
   - How to approach this
   - What patterns to use
   - What to avoid

## Code Quality Standards

### Example Pattern
\`\`\`python
# Show good example
def example():
    pass
\`\`\`

### Anti-Pattern
\`\`\`python
# Show what not to do
def bad_example():
    pass
\`\`\`

## Common Tasks

### Task 1: Description
Steps:
1. First step
2. Second step
3. Third step

### Task 2: Description
Steps:
1. First step
2. Second step

## Project Structure

Show relevant directory structure

## Commands

- Command 1: Description
- Command 2: Description
```

### Step 4: Test Agent

In VS Code Copilot Chat:
```
As a [your agent name]:
[test request]
```

Verify the agent:
- Understands domain context
- Follows project conventions
- Provides relevant examples
- Suggests appropriate patterns

### Step 5: Refine Instructions

Based on testing:
- Add more examples
- Clarify ambiguous instructions
- Add common pitfalls to avoid
- Include more code samples

## Best Practices

### 1. Be Specific

❌ Vague:
```markdown
Write good code.
```

✅ Specific:
```markdown
Use full type hints on all functions. Use `Final[type]` for constants.
Use `@dataclass(frozen=True, slots=True)` for immutable data structures.
```

### 2. Include Examples

Always show concrete examples:
```markdown
## Error Handling

✅ Good:
\`\`\`python
try:
    result = await process()
except ProcessingError as e:
    raise ServiceError("Failed to process") from e
\`\`\`

❌ Bad:
\`\`\`python
try:
    result = await process()
except:
    pass
\`\`\`
```

### 3. Reference Project Patterns

```markdown
Follow the repository pattern in `infrastructure/db/repositories/`.
Use the DI container in `composition/Container`.
```

### 4. Include File Paths

```markdown
Create entity in `backend/src/ekko/core/entities/`
Add DTO in `backend/src/ekko/application/dtos/`
```

### 5. Add Testing Requirements

```markdown
## Testing Requirements

- All new code must have tests
- Use `@pytest.mark.unit` for unit tests
- Use factory-boy for test data
- Minimum 70% coverage
```

### 6. Specify Tools and Commands

```markdown
## Commands

- Format code: `task format`
- Run tests: `task test`
- Type check: `task typecheck`
```

## Agent Composition

### Chaining Agents

You can reference multiple agents in one request:

```
As a backend developer and testing specialist:

Create a new audio processing service with comprehensive tests.
```

### Agent Specialization Levels

1. **General Agent**: Broad domain (backend, frontend)
2. **Specialized Agent**: Specific area (testing, security)
3. **Task-Specific Agent**: Single purpose (migrations, deployment)

### Example Hierarchy

```
Backend Development (General)
├── Database Expert (Specialized)
│   └── Migration Specialist (Task-Specific)
├── API Design (Specialized)
└── Performance Optimization (Specialized)
```

## Agent Configuration

### Global Settings

In `.vscode/settings.json`:

```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "text": "Follow Clean Architecture principles"
    },
    {
      "text": "Use Python 3.12+ features"
    }
  ]
}
```

### Project Instructions

In `.github/copilot-instructions.md`:

```markdown
# Project Instructions

All agents must:
1. Follow Clean Architecture
2. Use type hints
3. Write tests
4. Document code
```

### Agent-Specific Instructions

In `.github/agents/*.agent.md`:

Detailed, domain-specific instructions for each agent.

## Advanced Techniques

### 1. Context Injection

Include project-specific context:

```markdown
## Project Context

This project uses:
- Clean Architecture with strict layer boundaries
- FastAPI for REST API
- SQLAlchemy 2.0+ for database
- CrewAI for multi-agent AI systems
```

### 2. Pattern Library

Include reusable patterns:

```markdown
## Common Patterns

### Repository Pattern
\`\`\`python
class UserRepository(Protocol):
    async def get_by_id(self, user_id: str) -> User | None: ...
    async def save(self, user: User) -> None: ...
\`\`\`
```

### 3. Decision Trees

Guide decision-making:

```markdown
## When to Use

Use Zustand when:
- State is needed across multiple unrelated components
- State updates are frequent
- You need devtools integration

Use React Context when:
- State is limited to a component subtree
- Updates are infrequent
- You want built-in React solution
```

### 4. Anti-Patterns

Explicitly call out what to avoid:

```markdown
## Anti-Patterns

❌ Never import from infrastructure in core:
\`\`\`python
# core/entities/user.py
from ekko.infrastructure.db.models import UserModel  # WRONG
\`\`\`

✅ Use protocols instead:
\`\`\`python
# core/interfaces/repositories.py
class UserRepository(Protocol):
    async def save(self, user: User) -> None: ...
\`\`\`
```

### 5. Troubleshooting Guides

Include common issues and solutions:

```markdown
## Troubleshooting

**Issue**: Circular imports

**Solution**:
1. Check dependency direction (should point inward)
2. Use `from __future__ import annotations`
3. Move imports inside functions if needed
```

## Testing Agents

### 1. Verification Checklist

- [ ] Agent responds with domain expertise
- [ ] Follows project conventions
- [ ] Provides working code examples
- [ ] Suggests appropriate patterns
- [ ] Includes tests in responses
- [ ] References correct file paths
- [ ] Uses correct tool commands

### 2. Test Scenarios

Create test prompts for each agent:

```
# Backend Agent Test
As a backend developer:
Create a new repository for managing user sessions.

Expected:
- Protocol definition in core/interfaces/
- Implementation in infrastructure/db/repositories/
- Tests in tests/unit/infrastructure/
- Proper type hints
- Async methods
```

### 3. Regression Testing

Keep a log of prompts and expected behaviors:

```
tests/agent-tests/
├── backend-agent-tests.md
├── frontend-agent-tests.md
└── testing-agent-tests.md
```

## Maintenance

### 1. Regular Updates

Review and update agents when:
- Project conventions change
- New patterns are established
- Common mistakes are identified
- New tools are added
- Architecture evolves

### 2. Feedback Loop

Track agent effectiveness:
- Which agents are used most?
- What types of mistakes do agents make?
- What instructions need clarification?
- What examples are missing?

### 3. Version Control

Use Git to track agent changes:

```bash
git log .github/agents/backend-python.agent.md
```

### 4. Documentation

Document agent updates in changelog:

```markdown
## Agent Updates

### 2026-05-02

**Backend Agent**:
- Added SQLAlchemy 2.0 patterns
- Updated async/await examples
- Added migration workflow

**Frontend Agent**:
- Updated to React 19 patterns
- Added Zustand examples
- Improved TypeScript patterns
```

## Resources

### Official Documentation

- [GitHub Copilot Docs](https://docs.github.com/en/copilot)
- [VS Code Copilot](https://code.visualstudio.com/docs/copilot/overview)
- [Copilot Chat](https://docs.github.com/en/copilot/github-copilot-chat)

### Project Documentation

- [Claude + Copilot Guide](../docs/CLAUDE_COPILOT_GUIDE.md)
- [Tools Setup Guide](../docs/TOOLS_SETUP_GUIDE.md)
- [Python Conventions](../skills/python-conventions/SKILL.md)
- [Clean Architecture](../skills/clean-architecture/SKILL.md)

### Example Agents

- [Backend Python](.//backend-python.agent.md)
- [Frontend React](./frontend-react.agent.md)
- [Testing Specialist](./testing-specialist.agent.md)
- [Debug Expert](./debug.agent.md)

## Tips

1. **Start Simple**: Begin with basic instructions, add detail over time
2. **Use Real Examples**: Include actual code from your project
3. **Be Consistent**: Use the same terminology across agents
4. **Test Thoroughly**: Verify agents work as expected
5. **Iterate**: Refine based on usage and feedback
6. **Document Everything**: Clear documentation helps everyone
7. **Version Control**: Track changes to understand evolution
8. **Share Knowledge**: Learn from other projects' agents

## Conclusion

Custom agents make AI assistants more effective by:
- Understanding project context
- Following established patterns
- Respecting conventions
- Providing consistent guidance
- Reducing cognitive load

Invest time in creating quality agents—it pays dividends in development velocity and code quality.

---

For questions or suggestions, open a GitHub issue or discussion.
