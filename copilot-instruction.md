# Copilot Instruction: PR Review Automation

## Copilot-Powered PR Review Automation

Enable Copilot PR reviews as a first-level automated reviewer before human review.

### Capabilities

- Detect missing error handling
- Suggest test cases
- Identify insecure coding patterns
- Recommend performance improvements

### Outcome

- Reduced review fatigue
- Faster PR turnaround
- Improved code quality consistency

---

## Usage Instructions

1. **Automatic PR Review**: When a PR is created, Copilot will automatically review the code using the above capabilities.
2. **Console Output**: Copilot will display instructions in the console, highlighting missing error handling, test cases, insecure patterns, and performance issues.
3. **Action Prompt**: Copilot will prompt the user to fix detected issues and suggest specific changes.
4. **Instruction File Reference**: This file (`copilot-instruction.md`) will be referenced and called automatically during PR review to guide the process and suggest improvements.

---

## Example Console Output

```
Copilot PR Review:
- Missing error handling in function `process_data`. Please add try/except blocks.
- No test cases found for `user_login`. Please add unit tests.
- Insecure pattern detected: hardcoded password. Please use environment variables.
- Performance improvement: Use bulk inserts instead of single-row operations in `save_records`.

Would you like Copilot to suggest fixes for these issues? (Y/N)
```

---

## Integration

- Ensure this file is present in the repository root.
- Copilot will reference this file and follow the instructions during PR review automation.
