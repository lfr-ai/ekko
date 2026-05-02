# Using Claude with GitHub Copilot in VS Code

This guide explains how to use Claude (Anthropic) as your AI coding assistant within VS Code through GitHub Copilot.

## Prerequisites

1. **GitHub Copilot Subscription**
   - GitHub Copilot Individual ($10/month) or Business/Enterprise plan
   - Model selection feature (available for Individual, Business, and Enterprise)

2. **VS Code Extensions**
   - GitHub Copilot (`github.copilot`)
   - GitHub Copilot Chat (`github.copilot-chat`)

## Setup

### 1. Enable Model Selection

1. Open VS Code Settings (`Ctrl+,` or `Cmd+,`)
2. Search for "Copilot Chat Model"
3. Select a Claude model from the Copilot Chat model picker

Optional workspace default (if supported in your Copilot version):

```json
{
   "github.copilot.chat.defaultModel": "claude-sonnet-4"
}
```

### 2. Available Claude Models

GitHub Copilot supports these Claude models:

- **Claude Sonnet family** (Recommended)
  - Most capable model
  - Best for complex reasoning and code generation
  - 200K context window
  - Fast response times

- **claude-3-opus**
  - Most powerful Claude 3 model
  - Best for very complex tasks
  - Higher cost, slower responses

- **claude-3-sonnet**
  - Balanced performance
  - Good for general coding tasks

- **claude-3-haiku**
  - Fastest model
  - Best for simple completions
  - Lower cost

### 3. Verify Configuration

1. Open GitHub Copilot Chat (click the chat icon in the sidebar or use `Ctrl+Shift+I`)
2. Ask: "What model are you?"
3. Claude should identify itself as a Claude model (or your selected model)

## Features

### 1. Inline Completions

Claude provides context-aware code completions as you type:

```python
# Start typing and Claude suggests the rest
def process_audio(
    # Claude suggests: audio: bytes, sample_rate: int) -> str:
```

### 2. Chat Interface

Use the chat panel for:

- **Code Explanation**: Select code and ask "Explain this"
- **Code Generation**: Describe what you need
- **Refactoring**: Ask to improve or refactor code
- **Debugging**: Ask about errors or bugs
- **Testing**: Ask to generate tests

**Keyboard Shortcuts**:
- `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Shift+I` (Mac): Open chat
- `Ctrl+I` or `Cmd+I`: Inline chat

### 3. Agent Customization

Claude in Copilot respects custom instructions from:

1. **Global Instructions** (`.github/copilot-instructions.md`)
2. **Agent-Specific Instructions** (`.github/agents/*.agent.md`)
3. **Chat Instructions** (`github.copilot.chat.codeGeneration.instructions`)

Our project uses all three for comprehensive customization.

### 4. Slash Commands

Use slash commands in chat for specific actions:

- `/explain` - Explain selected code
- `/fix` - Propose a fix for problems
- `/tests` - Generate unit tests
- `/help` - Show available commands
- `/clear` - Clear chat history

### 5. Context Awareness

Claude has access to:
- Your current file
- Open files in editor
- Selected code
- Project structure (via workspace context)
- Custom instructions from `.github/` directory

## Project-Specific Configuration

### Custom Instructions

Our project has specialized agents for different tasks:

1. **Backend Python Development** (`.github/agents/backend-python.agent.md`)
   - Clean Architecture enforcement
   - FastAPI best practices
   - SQLAlchemy patterns

2. **Frontend React Development** (`.github/agents/frontend-react.agent.md`)
   - React 19 patterns
   - TypeScript strict mode
   - Tailwind CSS + shadcn/ui

3. **Testing Specialist** (`.github/agents/testing-specialist.agent.md`)
   - pytest and Vitest patterns
   - Property-based testing
   - E2E with Playwright

4. **Debug Agent** (`.github/agents/debug.agent.md`)
   - Error analysis
   - Performance profiling
   - Security auditing

### Workspace Context

Claude is aware of:

```
.github/
├── copilot-instructions.md       # Global project instructions
├── agents/                        # Specialized agents
│   ├── backend-python.agent.md
│   ├── frontend-react.agent.md
│   └── testing-specialist.agent.md
├── instructions/                  # Task-specific instructions
│   ├── architecture.instructions.md
│   ├── coding-conventions.instructions.md
│   └── testing.instructions.md
└── skills/                        # Reusable skill packs
    ├── clean-architecture/
    ├── frontend-react-stack/
    └── python-conventions/
```

## Usage Examples

### Example 1: Generate a New Endpoint

**Prompt**:
```
Create a new FastAPI endpoint for submitting audio transcription requests.
Follow Clean Architecture and use the existing patterns.
```

**Claude will**:
1. Check Clean Architecture guidelines
2. Create DTO, service, and route
3. Follow project conventions (type hints, error handling, etc.)
4. Generate appropriate tests

### Example 2: Refactor Component

**Prompt**:
```
Refactor this React component to use Zustand for state management
and follow our frontend conventions.
```

**Claude will**:
1. Check React conventions
2. Create Zustand store
3. Update component to use store
4. Maintain TypeScript type safety
5. Preserve styling patterns

### Example 3: Generate Tests

**Prompt**:
```
Generate comprehensive tests for this service including unit tests,
property-based tests, and integration tests.
```

**Claude will**:
1. Check testing conventions
2. Generate pytest tests with appropriate markers
3. Use factory-boy for test data
4. Include edge cases
5. Follow AAA pattern

## Best Practices

### 1. Be Specific

❌ Bad: "Add error handling"
✅ Good: "Add error handling using our custom exceptions from `ekko.core.exceptions` with proper exception chaining"

### 2. Reference Project Patterns

❌ Bad: "Create a database model"
✅ Good: "Create a SQLAlchemy model following our repository pattern in `infrastructure/db/`"

### 3. Ask for Multiple Options

```
Show me 3 different approaches to implement this feature:
1. Using CrewAI agents
2. Using LangChain chains
3. Using direct OpenAI API

Explain tradeoffs for each.
```

### 4. Iterative Refinement

Start with basic implementation, then refine:

```
1st prompt: "Create a basic audio processing service"
2nd prompt: "Add error handling and logging"
3rd prompt: "Add rate limiting and caching"
4th prompt: "Generate tests"
```

### 5. Use Context

Select relevant code before asking questions:

1. Select the code you're asking about
2. Open chat (`Ctrl+Shift+I`)
3. Ask your question
4. Claude will have the selected code as context

## Advanced Features

### 1. Multi-File Edits

Claude can suggest changes across multiple files:

```
Refactor the audio processing pipeline:
1. Split large service into smaller services
2. Update all imports
3. Update tests
4. Update DI container
```

### 2. Architecture Discussions

```
I want to add real-time collaboration features. Discuss:
1. Architecture changes needed
2. Database schema updates
3. API design
4. Frontend state management
5. Testing strategy
```

### 3. Performance Optimization

```
Analyze this code for performance issues:
[paste code]

Suggest optimizations following our conventions:
- Async where appropriate
- Proper database query optimization
- Caching strategies
```

### 4. Security Review

```
Review this authentication flow for security issues:
[paste code]

Check for:
- SQL injection
- XSS vulnerabilities
- CSRF protection
- Proper input validation
```

## Troubleshooting

### Model Not Switching

1. Restart VS Code
2. Sign out and sign in to GitHub Copilot
3. Check subscription includes model selection
4. Try setting model via command palette: "GitHub Copilot: Set Model"

### Poor Completions

1. Make sure `.github/copilot-instructions.md` is present
2. Check that custom instructions are being loaded
3. Provide more context in your prompt
4. Try rephrasing your question

### Context Not Working

1. Ensure workspace folder is correctly opened
2. Check that instruction files are in `.github/` directory
3. Verify settings.json has correct `chat.instructionsFilesLocations`

### Slow Responses

1. Try a faster model (claude-3-haiku)
2. Be more specific to reduce thinking time
3. Break complex requests into smaller pieces
4. Check your internet connection

## Keyboard Shortcuts

| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| Open chat | `Ctrl+Shift+I` | `Cmd+Shift+I` |
| Inline chat | `Ctrl+I` | `Cmd+I` |
| Accept suggestion | `Tab` | `Tab` |
| Reject suggestion | `Esc` | `Esc` |
| Next suggestion | `Alt+]` | `Option+]` |
| Previous suggestion | `Alt+[` | `Option+[` |

## Resources

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [Claude Documentation](https://docs.anthropic.com/)
- [VS Code Copilot Extension](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)
- [Anthropic Model Comparison](https://docs.anthropic.com/claude/docs/models-overview)

## Tips for This Project

1. **Always mention Clean Architecture** when working on backend code
2. **Reference existing patterns** from the codebase
3. **Ask for tests** after implementation
4. **Use agent-specific prompts**:
   - "As a backend developer..." for Python/FastAPI
   - "As a frontend developer..." for React/TypeScript
   - "As a testing specialist..." for test generation
5. **Request documentation** for complex features
6. **Ask for migration steps** when refactoring
7. **Get security review** for auth/sensitive operations
8. **Request performance analysis** for critical paths

## Examples of Great Prompts

### Backend Development
```
As a backend developer following Clean Architecture:

Create a new feature for audio streaming with these requirements:
- Stream audio from client to server
- Process in real-time with Whisper
- Store transcript in database
- Emit events via GraphQL subscription

Include:
1. Domain entities and value objects
2. Application service with use case
3. Infrastructure adapter for Whisper
4. FastAPI route with WebSocket
5. GraphQL subscription resolver
6. Unit and integration tests
7. Alembic migration

Follow all project conventions for error handling, logging, and types.
```

### Frontend Development
```
As a frontend developer using React 19 and TypeScript:

Create an audio recording component with these features:
- Visual waveform display
- Start/stop recording
- Real-time transcription display
- Error handling
- Loading states

Use:
- Zustand for recording state
- TanStack Query for API calls
- shadcn/ui for UI components
- Tailwind CSS v4 for styling
- proper TypeScript types
- React Testing Library tests

Follow our component structure and styling conventions.
```

### Testing
```
As a testing specialist:

Generate comprehensive tests for the audio processing service:

1. Unit tests:
   - Test all public methods
   - Mock external dependencies
   - Use factory-boy for test data
   - Include edge cases

2. Property-based tests:
   - Use Hypothesis
   - Test with random valid inputs
   - Verify invariants

3. Integration tests:
   - Test with real database
   - Test API endpoints
   - Test WebSocket connections

4. Performance tests:
   - Benchmark processing time
   - Memory usage tests

Follow pytest conventions with appropriate markers.
```
