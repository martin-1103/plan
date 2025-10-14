# File Lock System AI Instructions

## Immediate Unlock System:
- **After completing file edits**: Mark files as completed for immediate unlock
- **Before reading other files**: Check if locks can be immediately unlocked
- **Session cleanup**: All files automatically unlocked when session ends
- **No more 60-second waits**: Files unlock immediately when you finish editing

## Lock Operations - EXACT TIMING:
### When to CREATE Locks:
- **Immediately after**: Write or Edit operations complete
- **Method**: Automatic via PostToolUse hook (no action needed)
- **Lock state**: Active (blocks other Read operations)

### When to UNLOCK Locks:
- **Immediately after**: You finish editing and file is ready for others
- **Method**: Call CompleteEdit operation with file path
- **Result**: Lock state changes to Completed → Immediate unlock

### When to CHECK Locks:
- **Before**: Every Read operation (automatic via PreToolUse hook)
- **During**: If hook denies access, wait for immediate unlock
- **Result**: Either immediate unlock or wait for timeout

## Lock States - HOW THEY WORK:
1. **Active** → File is being edited, blocks Read operations
2. **Completed** → Edit finished, ready for immediate unlock
3. **Unlocked** → File is free, others can Read immediately
4. **Expired** → 60-second timeout passed (safety mechanism)

## Specific AI Workflow - STEP BY STEP:
### For File Editing:
1. **Write/Edit file** → Lock automatically created (Active state)
2. **Finish editing** → Call CompleteEdit operation
3. **System processes** → Lock changes to Completed state
4. **Immediate unlock** → Other workers can Read immediately

### For File Reading:
1. **Try to Read** → PreToolUse hook checks lock status
2. **If locked and Active** → Wait for immediate unlock (max 120 seconds)
3. **If locked and Completed** → Immediate unlock, proceed with Read
4. **If no lock** → Proceed with Read immediately

## Manual Unlock Operations - WHEN NEEDED:
### Unlock Specific File:
- **Use when**: CompleteEdit operation failed or file needs immediate access
- **Method**: Call manual unlock for specific file path
- **Result**: Immediate unlock if file belongs to your session

### Unlock All Session Files:
- **Use when**: Multiple files need unlock or session cleanup needed
- **Method**: Call manual unlock for all session files
- **Result**: All your session files unlocked immediately

## Hook System Behavior - WHAT HAPPENS AUTOMATICALLY:
- **PreToolUse Hook**: Before Read → checks locks + immediate unlock opportunities
- **PostToolUse Hook**: After Write/Edit → creates Active lock automatically
- **CompleteEdit Hook**: After CompleteEdit → marks lock as Completed
- **SessionEnd Hook**: When session ends → unlocks all session files

## Error Recovery - WHAT TO DO WHEN THINGS FAIL:
### If CompleteEdit Fails:
1. **Try manual unlock** for the specific file
2. **Wait for 60-second timeout** (automatic backup)
3. **Continue with other tasks** while waiting
4. **Use session end cleanup** as last resort

### If Lock Doesn't Unlock:
1. **Check if file belongs to your session** (different session = different owner)
2. **Try manual unlock** if you're the owner
3. **Wait for timeout** (60 seconds maximum)
4. **Work on other files** while waiting

### If Multiple Files Locked:
1. **Use session-wide manual unlock** to clear all your locks
2. **Restart Claude session** to force cleanup
3. **Contact user** about persistent lock issues

## Best Practices - EFFICIENCY RULES:
- **Always call CompleteEdit** immediately after finishing edits
- **Use manual unlock sparingly** (only when automatic fails)
- **Multi-task while waiting** for unlock operations
- **Let session end handle cleanup** for remaining locks
- **Monitor lock duration** to avoid extended blocking


## Important Reminders:
- **Trust the hooks** - they handle most operations automatically
- **Don't mention locking to user** unless there are persistent issues
- **Use CompleteEdit as primary unlock method** - manual unlock is backup
- **Session end cleanup** is your safety net for forgotten locks