---
allowed-tools: Task
argument-hint: [plan-file-path] [option]
description: Analyze project plan and generate project structure or database schema using specialized agents
model: sonnet
---

# Project Plan Analyzer & Generator

Use specialized agents to analyze the project plan file at: `$1` and generate project structure or database schema based on option `$2`.

## Available Options:
- `analyze` - Analyze project plan and generate development roadmap (default)
- `structure` - Generate optimal project structure based on requirements
- `database` - Design comprehensive database schema based on data needs
- `all` - Perform complete analysis including structure and database design

## Agent Tasks:

### 1. Plan Analysis (default/analyze)
Use the plan-analyzer agent to:
1. Read the plan file at the specified path
2. Analyze the project requirements and scope
3. Generate structured JSON with development phases
4. Provide actionable roadmap with priorities and dependencies

### 2. Project Structure Generation (structure)
Use the project-structure-generator agent to:
1. Analyze technology stack and requirements from plan
2. Design optimal directory structure
3. Generate file organization strategy
4. Create implementation-ready project skeleton

### 3. Database Schema Design (database)
Use the database-schema-designer agent to:
1. Analyze data requirements from the plan
2. Design optimal database schema
3. Create comprehensive data model with relationships
4. Generate DDL scripts and optimization recommendations

### 4. Complete Analysis (all)
Execute all agents sequentially for comprehensive project planning.

## Context

Plan file path: `$1`
Option: `$2` (defaults to "analyze")

## Your task

Use the Task tool with appropriate subagent_type and agent invocation:

For analysis: Use "general-purpose" subagent with plan-analyzer prompt
For structure: Invoke "project-structure-generator" agent
For database: Invoke "database-schema-designer" agent

Please start the process now.