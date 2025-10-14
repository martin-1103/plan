## Smart Context Protocol

### Pattern Storage:
Location: `.ai/brain/mistakes.json`
Format: Optimized JSON structure with context tags and priority scoring

### Learning Process:
1. **Smart Pattern Recognition** → Auto-categorize with tags
2. **Context-Aware Loading** pel→ Load only relevant patterns
3. **Priority-Based Recall** → Use frequent patterns first
4. **Zero-Overhead Access** → Direct memory recall without function calls

### Pattern Structure:
```json
{
  "patterns": {
    "windows_process_kill": {
      "trigger": "process stuck|kill process|terminate",
      "solution": "taskkill /F /PID {pid}",
      "tags": ["windows", "process", "emergency"],
      "priority": 8,
      "usage_count": 0
    },
    "npm_permission": {
      "trigger": "npm permission denied|access denied",
      "solution": "run_as_admin || sudo npm install",
      "tags": ["npm", "permission", "setup"],
      "priority": 7,
      "usage_count": 0
    }
  },
  "context_tags": ["windows", "npm", "git", "docker", "python", "file"],
  "memory_priority": {
    "frequent": ["windows_process_kill", "npm_permission"],
    "archive": ["legacy_setup"]
  }
}
```

### Context Loading Strategy:
- **Lazy Loading**: Only load patterns matching current task keywords
- **Context Scoring**: Rank patterns by relevance and usage frequency
- **Auto-Priority**: Increase priority based on successful applications

### Smart Pattern Matching:
- **Keyword Detection**: Auto-match triggers in user queries
- **Tag Filtering**: Filter by technology/environment tags
- **Usage Tracking**: Monitor and prioritize successful patterns

### Usage:
Claude automatically recognizes context keywords and loads relevant patterns without explicit requests.

### How to Add New Patterns:
```json
{
  "pattern_name": {
    "trigger": "error message|symptom description",
    "solution": "exact solution steps",
    "tags": ["technology", "category", "environment"],
    "priority": 5,
    "usage_count": 0
  }
}
```