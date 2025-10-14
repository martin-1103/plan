---
allowed-tools: Task
argument-hint: [plan-path] [target-folder]
description: Initialize project with database schema and structure generation from plan file
model: sonnet
---

# Initialize Project

Plan file: `$1`
Target folder: `$2`

## Setting up project foundation...

### 1. Read and Analyze Plan
> Read PRD/plan file from `$1` to understand project requirements

### 2. Generating Database Schema
> Use the database-schema-designer agent to design optimal database schema based on requirements from `$1`
> Output: Schema analysis and design in `.ai/database/` folder

### 3. Creating Project Structure
> Use the project-structure-generator agent to generate optimal project structure for `$2` based on requirements from `$1`
> Output: Structure analysis and architecture in `.ai/structure/` folder

## Usage Examples
```bash
/init @sample_prd.md rbac
/init @docs/plan.txt my-project
/init requirements.md webapp
```

## What this command generates:
1. **Database Schema Analysis** → `.ai/database/schema-analysis.md`
2. **Project Structure Analysis** → `.ai/structure/structure-analysis.md`
3. **Setup Documentation** → `.ai/structure/setup-guide.md`

## Important Notes:
- This command generates ANALYSIS and PLANNING documents only
- No actual project files are created in the target folder
- All outputs are saved in `.ai/` folder for review and implementation
- Use the generated analysis as blueprint for manual implementation