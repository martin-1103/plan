# Command Usage Guide

## Available Commands

| Command | Purpose | Order |
|---|---|---|
| `/init [target-folder]` | Initialize project with structure and database | 1️⃣ |
| `/coreplan <plan-file-path>` | Generate coreplan from plan file | 2️⃣ |
| `/breakdown-loop` | Breakdown long phases >60 minutes | 3️⃣ |
| `/run-tasks` | Execute tasks in parallel | 4️⃣ |

---

## Recommended Workflow

```mermaid
graph TD
    A[/init target-folder] --> B[/coreplan plan-file.txt]
    B --> C[/breakdown-loop]
    C --> D[/run-tasks]
```

### Quick Start

```bash
# 1. Initialize project
/init my-project

# 2. Generate development plan
/coreplan sample_prd.md

# 3. Optimize phase durations
/breakdown-loop

# 4. Execute tasks
/run-tasks
```

---

## Command Details

### 1. `/init` - Initialize Project
**Purpose**: Create new project with optimal structure and database schema.

**Syntax**: `/init <target-folder>`

**What it does**:
- Generates database schema
- Creates project directory structure
- Sets up foundational files

### 2. `/coreplan` - Generate Core Plan
**Purpose**: Convert plan file into structured development phases.

**Syntax**: `/coreplan <plan-file-path>`

**What it does**:
- Analyzes plan file
- Creates structured JSON phases
- Saves to `.ai/plan/` directory

### 3. `/breakdown-loop` - Optimize Phases
**Purpose**: Break down phases that exceed 60 minutes into smaller tasks.

**Syntax**: `/breakdown-loop`

**What it does**:
- Scans for long phases (>60 min)
- Automatically breaks them down
- Continues until all phases are optimized

### 4. `/run-tasks` - Execute Tasks
**Purpose**: Execute leaf tasks in parallel with quality control.

**Syntax**: `/run-tasks`

**What it does**:
- Finds available tasks
- Executes them in parallel
- Validates and updates status

---

## File Organization

- **Plan files**: Store in `docs/` or `plans/`
- **Generated outputs**: Saved to `.ai/` subdirectories
- **Validation reports**: Found in `.ai/brain/validation/`
- **Status logs**: Located in `.ai/brain/status/`

## Getting Help

For built-in commands: `/help`
For project structure: Check `.ai/` directories
For task status: Review `.ai/brain/status/` logs