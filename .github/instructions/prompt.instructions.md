---
description: Prompt template standards for LLM interactions
applyTo: "**/prompts/**/*.py"
---

# Prompt Template Instructions

LLM prompt templates follow structured patterns for consistency and maintainability.

## Structure

```python
from typing import Final

# Template constant
ANALYSIS_PROMPT_TEMPLATE: Final[str] = """
You are a domain expert.

## Context
Input Data: {input_data}
Configuration: {config}

## Task
Analyze the provided information and determine:
1. Primary classification
2. Confidence level
3. Key findings

## Output Format
Provide your analysis in JSON format:
{{
  "classification": "category",
  "confidence": 0.0-1.0,
  "findings": [],
  "reasoning": "explanation"
}}

## Analysis
"""
```

## Best Practices

### 1. Clear Structure
Use markdown headers to organize prompt sections:
- **Context**: Background information
- **Task**: What the AI should do
- **Output Format**: Expected response structure
- **Examples**: Few-shot learning (if applicable)

### 2. Explicit Output Format
Always specify expected output format:
```python
## Output Format
Respond with JSON only, no explanation:
{{
  "field1": "value",
  "field2": ["array", "of", "values"]
}}
```

### 3. Input Variables
Make variables explicit and typed:
```python
from typing import TypedDict

class AnalysisInput(TypedDict):
    input_data: str
    config: str
```

### 4. Few-Shot Examples
Include examples for complex tasks:
```python
## Examples

Input: "Data point A with value 42"
Output: {{"classification": "category_a", "confidence": 0.95}}

Input: "Ambiguous data point B"
Output: {{"classification": "unknown", "confidence": 0.3}}
```

### 5. Constraints
Specify constraints clearly:
```python
## Constraints
- Confidence must be between 0.0 and 1.0
- findings must be an array (empty if none found)
- reasoning must be a single paragraph
```

## Template Naming

```
<domain>_<action>_prompt.py

Examples:
- analysis_prompt.py
- classification_prompt.py
- extraction_prompt.py
```

## Testing Prompts

```python
import pytest

def test_prompt_renders_with_valid_inputs():
    "Prompt template renders with valid inputs."
    result = template.format(
        input_data="Sample input",
        config="Default config"
    )
    assert "Sample input" in result

def test_prompt_has_correct_variables():
    "Prompt template has correct input variables."
    assert set(template.input_variables) == {"input_data", "config"}
```

## Version Control

When updating prompts:
1. **Test First**: Evaluate impact on existing cases
2. **Version**: Consider versioning for major changes
3. **Document**: Explain why the prompt was updated
4. **Validate**: Run integration tests with new prompt

## Prompt Optimization

### Clarity Over Brevity
```python
# Good: Clear and explicit
"""
Analyze the document and extract the relevant date.
If multiple dates are present, choose the earliest relevant date.
If no clear date is found, return null.
"""

# Bad: Terse and ambiguous
"""
Find the date from the document.
"""
```

### Structured Output
```python
# Good: Structured and parseable
"""
Output JSON:
{{"date": "YYYY-MM-DD", "confidence": 0.0-1.0}}
"""

# Bad: Unstructured
"""
Tell me the date.
"""
```

### Context Windows
- Keep prompts concise for token efficiency
- Put most important context first
- Trim irrelevant information from inputs

## Example: Complete Prompt Template

```python
from typing import Final

ANOMALY_DETECTION_PROMPT_TEMPLATE: Final[str] = """
You are a data anomaly detection specialist.

## Context
Record ID: {record_id}
Data Source: {data_source}
Historical Records: {history}

## Task
Analyze the provided information and identify potential anomalies.

## Anomaly Indicators to Check
1. Inconsistent dates or timeline
2. Repeated patterns suggesting duplication
3. Values outside expected ranges
4. Missing or incomplete data
5. Logical contradictions

## Output Format
Provide analysis in JSON format:
{{
  "anomaly_risk": "low" | "medium" | "high",
  "confidence": 0.0-1.0,
  "indicators": [
    {{
      "type": "indicator_type",
      "description": "what was found",
      "severity": "low" | "medium" | "high"
    }}
  ],
  "reasoning": "overall assessment"
}}

## Guidelines
- Be conservative: only flag clear indicators
- Provide specific evidence for each indicator
- Include confidence score based on evidence strength

## Analysis
"""
```
