Asana RL Environment - Seed Data Generator
This project generates realistic, high-quality seed data for an Asana reinforcement learning environment. The data simulates a B2B SaaS company with 5000-10000 employees using Asana for product development, marketing, and operations.

Overview
The generator creates a complete enterprise Asana workspace with:

1 Organization (B2B SaaS company)

25 Teams (Engineering, Product, Marketing, Sales, Customer Success, Operations)

5000-10000 Users with realistic names from census data

100+ Projects across different team workflows

2000+ Tasks with realistic naming patterns based on GitHub issues and Asana templates

Comments, Custom Fields, Tags and other metadata

Features

Data Realism

Task names follow real-world patterns: "Implement OAuth 2.0 authentication flow" not "Task 1"
Census-based name distribution: First and last names from US Census data
Research-backed distributions:
Task completion rates by project type (70-85% for sprints, 40-50% for ongoing)
Due date patterns (25% within 1 week, 40% within 1 month, 10% no due date)
Assignment rates (15% unassigned per Asana benchmarks)
Temporal consistency: Tasks completed after creation, comments spread over task lifetime
Department-specific patterns: Engineering tasks follow "[Component] - [Action]" pattern, Marketing tasks follow "[Campaign] - [Deliverable]"

Setup Instructions
Prerequisites
Python 3.8 or higher
pip
Installation
Clone or download the repository
Install dependencies:
bash
pip install -r requirements.txt
(Optional) Set up Anthropic API for LLM-generated content:
bash
cp .env.example .env


Note: LLM integration is optional. The generator uses template-based generation by default, which produces equally realistic data without requiring an API key.

# Running the Generator
bash
python src/main.py
The script will:

Create a new SQLite database at output/asana_simulation.sqlite
Generate all data with progress logging
Display statistics on completion
Expected runtime: 2-5 minutes for full dataset

Configuration
Edit the CONFIG dictionary in src/main.py to adjust:

python
CONFIG = {
    'employee_count': 7500,  # Number of users (5000-10000)
    'output_db': 'output/asana_simulation.sqlite',
    'schema_file': 'schema.sql',
    'start_date': '2024-07-01',  # Start of data history
    'end_date': '2026-01-06',  # Current date
}
Database Schema
The schema follows Asana's entity model with proper foreign key relationships:

Core Tables
organizations: Top-level workspace
teams: Groups within organization
users: Team members with census-based names
team_memberships: Many-to-many user-team relationships
projects: Collections of tasks
sections: Subdivisions within projects (To Do, In Progress, Done)
tasks: Core unit of work (supports subtasks via parent_task_id)
Metadata Tables
comments: Task discussions and updates
custom_field_definitions: Project-specific fields
custom_field_values: Values for custom fields on tasks
tags: Cross-project labels
task_tags: Task-tag associations
attachments: File metadata (simulated)
Key Design Decisions
Custom Fields: Handled with separate tables for definitions (per-project) and values (per-task), allowing flexible field types (dropdown, text, number, date, checkbox).

Task Hierarchy: Single tasks table with self-referential parent_task_id foreign key. Subtasks reference parent via this field (NULL for top-level tasks).

Temporal Consistency: All timestamps validated:

Tasks cannot be completed before creation
Comments fall within task lifetime
Due dates respect business days (85% avoid weekends)
Data Generation Methodology
Research-Backed Distributions
Task Completion Rates
Source: Asana "Anatomy of Work" reports


LLM Content Generation
The generator supports optional LLM integration for enhanced variety.

# Data Quality Checks
## Run these queries to verify data quality:

sql
## Check temporal consistency
SELECT COUNT(*) FROM tasks 
WHERE completed_at < created_at; -- Should be 0

## Verify assignment distribution
SELECT 
    ROUND(COUNT(CASE WHEN assignee_id IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) as unassigned_pct
FROM tasks; -- Should be ~15%

## Check completion rates by project type
SELECT 
    p.project_type,
    ROUND(AVG(CASE WHEN t.completed THEN 1.0 ELSE 0.0 END) * 100, 2) as completion_pct
FROM tasks t
JOIN projects p ON t.project_id = p.project_id
GROUP BY p.project_type;

## Verify due date distribution
SELECT 
    CASE 
        WHEN due_date IS NULL THEN 'No due date'
        WHEN due_date < DATE('now') THEN 'Overdue'
        WHEN due_date < DATE('now', '+7 days') THEN 'Within 1 week'
        WHEN due_date < DATE('now', '+30 days') THEN 'Within 1 month'
        ELSE '1+ months'
    END as due_date_category,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM tasks
WHERE parent_task_id IS NULL
GROUP BY due_date_category;
Extending the Generator
Adding New Project Types

Inconsistent Timestamps
Check system clock
Verify start_date < end_date in CONFIG
Ensure end_date is not in future
License
All code is provided for evaluation purposes.

Contact
For questions about this implementation, refer to the submitted documentation.


