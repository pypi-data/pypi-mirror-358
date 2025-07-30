# Tool Usage Patterns

General guidance for effective tool utilization and interaction patterns.

## Tool Selection Principles

- **Use the most appropriate tool for each task**
- **Understand tool capabilities and limitations before use**
- **Prefer specialized tools over generic ones when available**
- **Consider the context and requirements of the specific situation**

## Interaction Patterns

### JSON Format for Tool Calls
When using tools, structure requests in the proper JSON format:
```json
{
  "tool": "tool_name",
  "arguments": {
    "parameter": "value"
  }
}
```

### Error Handling
- **Handle tool errors gracefully and informatively**
- **Provide fallback options when primary tools fail**
- **Explain tool limitations clearly to users**
- **Retry with different parameters when appropriate**

## Efficiency Guidelines

### Batch Operations
- **Group related operations when possible**
- **Minimize redundant tool calls**
- **Cache results when appropriate for reuse**

### Tool Sequencing
- **Plan tool usage sequences for optimal workflow**
- **Validate prerequisites before complex operations**
- **Use tool outputs effectively as inputs to subsequent operations**

## Quality Assurance

### Verification
- **Verify tool results before proceeding with dependent operations**
- **Cross-check important results using multiple approaches**
- **Validate assumptions about tool behavior and outputs**

### User Communication
- **Explain tool usage and reasoning to users when helpful**
- **Provide progress updates during long-running operations**
- **Clarify when tool limitations may affect outcomes**
