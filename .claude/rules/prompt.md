---
paths:
  - "backend/src/ekko/ai/prompts/**/*.py"
---

# Prompt Template Rules

## Structure

- Use `Final[str]` typed constants for templates
- Organize with markdown headers: Context, Task, Output Format, Examples, Constraints
- Always specify explicit JSON output format with escaped braces `{{}}`

## Naming

```
<domain>_<action>_prompt.py
```

## Best Practices

- Clear structure with markdown headers
- Explicit output format (always JSON with schema)
- Typed input variables (TypedDict or dataclass)
- Few-shot examples for complex tasks
- Constraints stated explicitly
- Clarity over brevity

## Testing

- Test that templates render with valid inputs
- Test that correct input variables are present
- Run integration tests when prompts change

## Updating Prompts

1. Evaluate impact on existing cases first
2. Version for major changes
3. Document why the prompt was updated
4. Run integration tests with the new prompt
