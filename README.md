# Command Usage Guide

## Available Commands

| Command | Purpose | Order |
|---|---|---|
| `/init [plan-path] [target-folder]` | Initialize project analysis with structure and database | 1️⃣ |
| `/breakdown-loop` | Breakdown long phases >60 minutes | 2️⃣ |
| `/run-tasks` | Execute tasks in parallel | 3️⃣ |

---



### Quick Start

```bash
# 1. Initialize project analysis
/init @sample_prd.md rbac


# 2. Optimize phase durations
/breakdown-loop

# 3. Execute tasks
/run-tasks
```

---

## Command Details

### 1. `/init` - Initialize Project Analysis
**Purpose**: Generate project analysis with optimal structure and database schema from plan file.

**Syntax**: `/init [plan-path] [target-folder]`

**What it does**:
- Reads and analyzes plan file from `[plan-path]`
- Generates database schema analysis → `.ai/database/`
- Creates project structure analysis → `.ai/structure/`
- Generates setup documentation → `.ai/structure/`

**Important**: Creates ANALYSIS documents only, not actual project files


### 2. `/breakdown-loop` - Optimize Phases
**Purpose**: Break down phases that exceed 60 minutes into smaller tasks.

**Syntax**: `/breakdown-loop`

**What it does**:
- Scans for long phases (>60 min)
- Automatically breaks them down
- Continues until all phases are optimized

### 3. `/run-tasks` - Execute Tasks
**Purpose**: Execute leaf tasks in parallel with quality control.

**Syntax**: `/run-tasks`

**What it does**:
- Finds available tasks
- Executes them in parallel
- Validates and updates status

---

## File Organization

- **Plan files**: Store in `docs/`, `plans/`, or root directory
- **Database Analysis**: Generated in `.ai/database/`
- **Structure Analysis**: Generated in `.ai/structure/`
- **Development Plans**: Saved to `.ai/plan/` directory
- **Validation Reports**: Found in `.ai/brain/validation/`
- **Status Logs**: Located in `.ai/brain/status/`
- **Mistakes & Learning**: Documented in `.ai/brain/mistakes.json`

## Getting Help

For built-in commands: `/help`
For project structure: Check `.ai/` directories
For task status: Review `.ai/brain/status/` logs