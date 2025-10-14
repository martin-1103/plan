---
allowed-tools: Task
argument-hint: [target-folder]
description: Initialize project with database schema and structure generation
model: sonnet
---

# Initialize Project

Target folder: `$1`

## Setting up project foundation...

### 1. Generating Database Schema
> Use the database-schema-designer agent to design optimal database schema for the project in `$1`

### 2. Creating Project Structure
> Use the project-structure-generator agent to generate optimal project structure in `$1`

## Initializing complete project setup in: `$1`

This command will:
1. Design and create database schema using database-schema-designer agent
2. Generate optimal project structure using project-structure-generator agent
3. Set up foundational files and directories in target folder: `$1`