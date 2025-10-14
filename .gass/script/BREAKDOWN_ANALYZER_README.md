# Plan Breakdown Analyzer with Loop Tracking

## Overview

The Enhanced Plan Breakdown Analyzer is a Node.js script that automatically breaks down large project phases into smaller, manageable sub-phases using AI. It implements intelligent loop tracking to ensure all phases are properly processed and maintains state across multiple runs.

## Features

- **Automatic Phase Detection**: Reads phases from `.ai/plan/phases.json`
- **Duration-Based Breakdown**: Breaks down phases with duration > 30 minutes
- **AI-Powered Generation**: Uses Claude Agent SDK to generate detailed sub-phases
- **Loop Tracking**: Maintains state across multiple runs with automatic retry
- **Progress Persistence**: Saves completion state to `.ai/.breakdown_loop_state.json`
- **Validation**: Validates generated phase data for completeness and correctness
- **Parallel Execution**: Supports parallel execution opportunities where applicable

## File Structure

```
.ai/
├── script/
│   ├── plan-breakdown-analyzer.js    # Main analyzer script
│   ├── helpers.js                    # Helper functions
│   └── package.json                  # Dependencies
├── plan/
│   ├── phases.json                   # Main project phases
│   ├── 1.json, 2.json, ...          # Individual phase breakdowns
│   └── index.json                    # Project index
├── output/                           # Backup outputs (auto-created)
└── .breakdown_loop_state.json       # Loop tracking state (auto-created)
```

## Installation

1. Navigate to the script directory:
```bash
cd .ai/script
```

2. Install dependencies:
```bash
npm install
```

## Usage

### Basic Usage

Run the breakdown analyzer on all phases:
```bash
node plan-breakdown-analyzer.js
```

### Check Current Status

View the current breakdown progress:
```bash
node plan-breakdown-analyzer.js --status
```

### Reset Loop State

Reset all progress and start fresh:
```bash
node plan-breakdown-analyzer.js --reset
```

### Using npm scripts

```bash
npm run breakdown          # Run breakdown analyzer
npm run breakdown -- --status  # Check status
npm run breakdown -- --reset   # Reset state
```

## Configuration

### Duration Threshold

The analyzer breaks down phases with duration > 30 minutes. This can be modified in the `shouldBreakdown()` method:

```javascript
if (duration > 30) { // 30 minutes
    logger.info(`Phase ${phase.id} duration ${duration}min > 30min, needs breakdown`);
    return true;
}
```

### Maximum Iterations

The loop has a maximum iteration limit (default: 100) to prevent infinite loops:

```javascript
const state = {
    maxIterations: 100,
    currentIteration: 0
};
```

## Output Format

Each phase breakdown generates JSON with the following structure:

```json
{
  "task_id": "1.1",
  "parent_id": "1",
  "file_name": "1.1.json",
  "title": "Phase Title",
  "description": "Phase description",
  "duration": "2-3 days",
  "priority": "high",
  "dependencies": [],
  "breakdown_strategy": "time-based",
  "phases": [
    {
      "id": "1.1.1",
      "title": "Sub-phase Title",
      "description": "Sub-phase description",
      "duration": "30 minutes",
      "priority": 1,
      "dependencies": [],
      "deliverables": ["Deliverable 1", "Deliverable 2"],
      "parallel_group": 1,
      "status": "pending"
    }
  ],
  "execution_plan": {
    "parallel_groups": [...],
    "critical_path": [...],
    "milestones": [...]
  },
  "breakdown_complete": true,
  "status": "pending"
}
```

## Loop Tracking

The analyzer maintains state across multiple runs:

- **Completed Phases**: Phrases that have been successfully broken down
- **Failed Phases**: Phases that failed and need retry
- **Current Iteration**: Number of loop iterations completed
- **Last Updated**: Timestamp of last state update

### State File Format

```json
{
  "completedPhases": ["1", "2", "3"],
  "failedPhases": ["4"],
  "currentIteration": 2,
  "lastUpdated": "2025-10-14T00:00:00.000Z"
}
```

## Error Handling

The analyzer includes comprehensive error handling:

- **File Not Found**: Searches multiple paths for plan files
- **JSON Parse Errors**: Validates JSON structure before processing
- **AI API Errors**: Retries failed phases in subsequent iterations
- **Validation Errors**: Validates generated data before saving
- **Timeout Protection**: Maximum iteration limits prevent infinite loops

## Logging

The analyzer provides detailed logging:

- **ℹ️ Info**: General progress information
- **⚠️ Warnings**: Non-critical issues
- **❌ Errors**: Critical errors that stop processing
- **🐛 Debug**: Detailed debugging information

## Integration with Existing Workflow

The analyzer integrates seamlessly with the existing task management system:

1. **Reading**: Uses existing helper functions from `helpers.js`
2. **Validation**: Implements data validation similar to other scripts
3. **State Management**: Compatible with existing phase status tracking
4. **AI Integration**: Uses Claude Agent SDK consistent with other tools

## Troubleshooting

### Common Issues

1. **"File tidak ditemukan" Error**
   - Ensure `.ai/plan/phases.json` exists
   - Check file permissions
   - Run from correct directory

2. **"Claude Code process exited" Error**
   - Usually caused by timeout during long operations
   - Progress is saved, so re-run to continue
   - Consider reducing phase complexity

3. **"No JSON found in AI response" Error**
   - AI response format issue
   - Will retry automatically in next iteration
   - Check network connectivity

### Recovery

The analyzer automatically recovers from most errors:
- Failed phases are retried in subsequent iterations
- State is preserved across runs
- Partial progress is never lost

## Examples

### Example 1: First Run

```bash
$ node plan-breakdown-analyzer.js --status
📊 Current Status:
  Completed: 0 phases
  Failed: 0 phases
  Iteration: 0

$ node plan-breakdown-analyzer.js
🚀 Starting breakdown loop for 10 phases
🔄 Processing phase 1: Foundation Architecture...
✅ Phase 1 completed successfully
🔄 Processing phase 2: Visual Flow Builder...
...
```

### Example 2: Resume After Interruption

```bash
$ node plan-breakdown-analyzer.js --status
📊 Current Status:
  Completed: 3 phases
  Failed: 1 phases
  Iteration: 1
  Completed phases: 1, 2, 3
  Failed phases: 4

$ node plan-breakdown-analyzer.js
🚀 Starting breakdown loop for 10 phases
📊 Current state: 3 completed, 1 failed
⏭️  Phase 1 already completed, skipping
⏭️  Phase 2 already completed, skipping
⏭️  Phase 3 already completed, skipping
🔄 Processing phase 4: User Authentication...
```

## Performance Considerations

- **Memory Usage**: Efficient streaming of AI responses
- **Disk I/O**: Minimal file operations with async patterns
- **Network**: Batches AI calls to prevent rate limiting
- **CPU**: Lightweight JSON processing and validation

## Future Enhancements

Potential improvements for future versions:

1. **Parallel Processing**: Process multiple phases simultaneously
2. **Smart Caching**: Cache AI responses for similar phases
3. **Custom Prompts**: Allow custom prompt templates
4. **GUI Interface**: Web-based progress monitoring
5. **API Integration**: REST API for remote management
6. **Advanced Analytics**: Detailed breakdown statistics and insights

## Support

For issues or questions:

1. Check the log output for specific error messages
2. Verify file permissions and directory structure
3. Ensure all dependencies are installed
4. Review this documentation for configuration options

## License

MIT License - see package.json for details.