# LEARNING RULES

## AUTO-CAPTURE RULE
ON_ERROR → CREATE_PATTERN → SAVE_TO:.ai/brain/mistakes.json

## PATTERN STRUCTURE
```json
{
  "pattern_name": {
    "trigger": "error_regex|symptom_keywords",
    "solution": "exact_solution_steps",
    "action": "AUTO_SUGGEST|AUTO_EXECUTE",
    "tags": ["technology", "category", "environment"],
    "priority": 1-10,
    "usage_count": 0
  }
}
```

## COMMANDS

### Rule #1: Windows Command Error
IF detect "move: command not found" OR "/usr/bin/bash: line 1: move"
THEN suggest "Use mv command instead of move for Linux/Windows Git Bash"
ACTION: AUTO_SUGGEST
PRIORITY: 7
UPDATE: usage_count++

### Rule #2: NPM Permission Error
IF detect "npm permission denied" OR "access denied" OR "EACCES"
THEN suggest "Run as admin or use sudo npm install"
ACTION: AUTO_SUGGEST
PRIORITY: 8
UPDATE: usage_count++

### Rule #3: Process Stuck Error
IF detect "process stuck" OR "kill process" OR "terminate"
THEN suggest "taskkill /F /PID {pid}"
ACTION: AUTO_SUGGEST
PRIORITY: 9
UPDATE: usage_count++

## ACTIONS

### CREATE_PATTERN:
1. EXTRACT error message from context
2. IDENTIFY solution that worked
3. FORMAT as JSON pattern structure
4. SAVE to .ai/brain/mistakes.json

### AUTO_SUGGEST:
1. MATCH error with existing patterns
2. SUGGEST solution immediately
3. UPDATE usage_count
4. INCREASE priority on success

### PRIORITY_SYSTEM:
- 10: Critical errors (block work)
- 8-9: Common errors (frequent)
- 5-7: Moderate errors (occasional)
- 1-4: Rare errors (edge cases)

## TRIGGER_MATCHING
- DETECT keywords in user queries
- SCAN error messages in tool outputs
- MATCH regex patterns automatically
- LOAD relevant patterns without request

## UPDATE_RULES
- usage_count++ ON_SUCCESS
- priority++ IF usage_count > 5
- archive IF not used in 30 days
- merge IF duplicate patterns found

## REQUIRED_BEHAVIOR
- ALWAYS check mistakes.json for matching patterns
- SUGGEST solutions immediately when match found
- LEARN from successful solutions
- IMPROVE pattern matching over time