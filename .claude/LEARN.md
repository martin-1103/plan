# LEARNING RULES

## 🎭 **Meta-Rule: Self-Reflective Pattern Creation**

### **CRITICAL META-RULE**: Always Ask "Should I Create a Learning Pattern?"

**When encountering ANY error or unexpected behavior:**

1. **PAUSE** - Before continuing, ask: "Is this error likely to happen again?"
2. **ANALYZE** - What pattern or practice could prevent this error?
3. **DECIDE** - If the answer is "yes, this could recur," immediately create/update a learning pattern
4. **DOCUMENT** - Add the pattern to mistakes.json with prevention strategy

### **Self-Check Questions Before Any Action**
1. "Have I seen this type of error before in this project?"
2. "Could this error be prevented by following a specific pattern?"
3. "Would documenting this help future development?"
4. "Is this a one-off issue or a systemic pattern to avoid?"

**If ANY answer is "yes" → CREATE/UPDATE LEARNING PATTERN IMMEDIATELY**

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
    "usage_count": 0,
    "prevention_rule": "how to prevent this error",
    "self_check_questions": ["question1", "question2"],
    "error_category": "tool_format|environment|build|deployment|ai_integration",
    "implementation": "step-by-step guidance",
    "last_seen": "timestamp",
    "prevention_success_rate": 0.0-1.0
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

## ERROR CATEGORIES THAT ALWAYS NEED LEARNING PATTERNS

### **Category 1: Tool Call Format Errors**
- **Examples**: Git commit newline issues, command format errors
- **Prevention**: Use proper command templates and validation
- **Priority**: 8-9

### **Category 2: Environment Configuration Issues**
- **Examples**: API keys, database setup, path configuration
- **Prevention**: Environment setup checklists and validation scripts
- **Priority**: 9-10

### **Category 3: Build/Compilation Errors**
- **Examples**: TypeScript errors, dependency issues, syntax errors
- **Prevention**: Pre-commit hooks and linting rules
- **Priority**: 7-8

### **Category 4: Deployment Failures**
- **Examples**: Vercel limits, function timeouts, deployment config
- **Prevention**: Deployment checklists and monitoring
- **Priority**: 9-10

### **Category 5: AI Integration Problems**
- **Examples**: OpenAI setup, prompt formatting, API integration
- **Prevention**: Integration templates and error handling
- **Priority**: 6-8

## PRIORITY_SYSTEM:
- 10: Critical errors (block work, deployment issues)
- 8-9: Common errors (frequent, environment issues)
- 5-7: Moderate errors (occasional, integration issues)
- 1-4: Rare errors (edge cases, one-time issues)

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

### **Pre-Action Behavior (Proactive Prevention)**
- **PRE-ACTION CHECK**: Always run self-check questions before executing any action
- **PATTERN SCAN**: Check existing patterns before executing similar actions
- **PREVENTION SUGGESTION**: Suggest prevention strategies before errors occur
- **RISK ASSESSMENT**: Evaluate if action matches high-risk error categories

### **During Error (Reactive Learning)**
- **IMMEDIATE PATTERN CHECK**: Always check mistakes.json for matching patterns
- **INSTANT SUGGESTION**: Suggest solutions immediately when match found
- **PATTERN CREATION**: Create new patterns for unfamiliar errors
- **DOCUMENTATION**: Document both error and prevention strategies

### **Post-Resolution (Continuous Improvement)**
- **SUCCESS LEARNING**: Learn from successful solutions and update patterns
- **PREVENTION UPDATES**: Update prevention rules based on successful resolutions
- **SUCCESS RATE TRACKING**: Track prevention_success_rate for each pattern
- **PATTERN EVOLUTION**: Improve pattern matching over time

### **Meta-Cognitive Behavior**
- **REFLECTION**: Always ask "Should I create/update a learning pattern?"
- **CATEGORIZATION**: Assign proper error_category to new patterns
- **IMPLEMENTATION GUIDANCE**: Provide clear implementation steps
- **INSTITUTIONAL MEMORY**: Build and maintain project error prevention knowledge

## PATTERN CREATION TEMPLATE

### **When Creating New Learning Patterns:**

#### **Step 1: Error Analysis**
```
## 🚨 [Error Category] Prevention

### **Problem**: [Brief description of what went wrong]
```
[Error message or symptoms]
```

### **Root Cause**: [Why this happened]

### **Prevention Rule**:
```
# ❌ WRONG - [what not to do]
[example of incorrect approach]

# ✅ CORRECT - [what to do instead]
[example of correct approach]
```

### **Implementation**: [How to apply this rule consistently]
```

#### **Step 2: Pattern Documentation**
```json
{
  "pattern_name": "descriptive_name",
  "trigger": "error_regex_or_keywords",
  "solution": "exact_solution_steps",
  "action": "AUTO_SUGGEST",
  "tags": ["technology", "category", "environment"],
  "priority": 1-10,
  "usage_count": 0,
  "prevention_rule": "how to prevent this error",
  "self_check_questions": [
    "question about prevention",
    "question about implementation"
  ],
  "error_category": "tool_format|environment|build|deployment|ai_integration",
  "implementation": "step-by-step guidance",
  "last_seen": "timestamp",
  "prevention_success_rate": 0.0
}
```

#### **Step 3: Save and Integrate**
1. **SAVE** to `.ai/brain/mistakes.json`
2. **UPDATE** existing patterns if similar
3. **COMMUNICATE** to team members
4. **TRACK** success rate over time

### **Template Examples:**

#### **Tool Format Error Template:**
```json
{
  "windows_path_error": {
    "trigger": "unexpected EOF|looking for matching|command not found",
    "solution": "Use forward slashes or escape backslashes in Windows Git Bash",
    "action": "AUTO_SUGGEST",
    "tags": ["windows", "bash", "path", "command"],
    "priority": 8,
    "usage_count": 0,
    "prevention_rule": "Always use forward slashes in paths for Git Bash",
    "self_check_questions": [
      "Am I using Windows paths with backslashes?",
      "Should I escape the backslashes or use forward slashes?"
    ],
    "error_category": "tool_format",
    "implementation": "Replace all \\ with / in file paths for Git Bash commands",
    "last_seen": "2025-10-15T00:00:00.000Z",
    "prevention_success_rate": 0.0
  }
}
```

#### **Environment Error Template:**
```json
{
  "missing_env_var": {
    "trigger": "API_KEY not found|undefined|null",
    "solution": "Check .env file and environment variable setup",
    "action": "AUTO_SUGGEST",
    "tags": ["environment", "config", "api"],
    "priority": 9,
    "usage_count": 0,
    "prevention_rule": "Always validate environment variables before deployment",
    "self_check_questions": [
      "Are all required environment variables set?",
      "Did I check the .env.example file?"
    ],
    "error_category": "environment",
    "implementation": "Create environment checklist and validation script",
    "last_seen": "2025-10-15T00:00:00.000Z",
    "prevention_success_rate": 0.0
  }
}
```