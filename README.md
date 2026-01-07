Here is the corrected content in a clean, copy-pasteable Markdown format. I’ve structured it with proper headers and bullet points to ensure it’s readable and professional.

```markdown
# Asana RL Environment - Seed Data Generator

This project generates realistic, high-quality seed data for an Asana reinforcement learning environment. The data simulates a B2B SaaS company with 5,000–10,000 employees using Asana for product development, marketing, and operations.

## Overview
The generator creates a complete enterprise Asana workspace with:
* **1 Organization:** A simulated B2B SaaS company.
* **25 Teams:** Including Engineering, Product, Marketing, Sales, Customer Success, and Operations.
* **5,000–10,000 Users:** Featuring realistic names from US Census data.
* **100+ Projects:** Spanning different team workflows.
* **2,000+ Tasks:** Using realistic naming patterns based on GitHub issues and Asana templates.
* **Metadata:** Includes comments, custom fields, tags, and attachments.

## Features

### Data Realism
* **Task Naming:** Follows real-world patterns (e.g., "Implement OAuth 2.0 authentication flow" instead of "Task 1").
* **Name Distribution:** First and last names are pulled from US Census data.
* **Research-Backed Distributions:** * **Task Completion Rates:** Based on project type (70–85% for sprints, 40–50% for ongoing tasks).
    * **Due Date Patterns:** 25% within 1 week, 40% within 1 month, 10% with no due date.
    * **Assignment Rates:** Approximately 15% unassigned, per Asana benchmarks.
* **Temporal Consistency:** Tasks are completed after creation; comments are spread across the task lifetime.
* **Department-Specific Patterns:** Engineering tasks follow a `[Component] - [Action]` pattern, while Marketing follows `[Campaign] - [Deliverable]`.

## Setup Instructions

### Prerequisites
* Python 3.8 or higher
* pip

### Installation
1. Clone or download the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt

```

3. (Optional) Set up Anthropic API for LLM-generated content:
```bash
cp .env.example .env

```


*Note: LLM integration is optional. The generator uses template-based generation by default, which produces equally realistic data without requiring an API key.*

### Running the Generator

```bash
python src/main.py

```

The script will:

1. Create a new SQLite database at `output/asana_simulation.sqlite`.
2. Generate all data with progress logging.
3. Display statistics on completion.
*Expected runtime: 2–5 minutes for the full dataset.*

## Configuration

Edit the `CONFIG` dictionary in `src/main.py` to adjust settings:

```python
CONFIG = {
    'employee_count': 7500,        # Number of users (5000-10000)
    'output_db': 'output/asana_simulation.sqlite',
    'schema_file': 'schema.sql',
    'start_date': '2024-07-01',    # Start of data history
    'end_date': '2026-01-06',      # Current date
}

```

## Database Schema

The schema follows Asana's entity model with proper foreign key relationships:

### Core Tables

* **organizations**: Top-level workspace.
* **teams**: Groups within the organization.
* **users**: Team members with census-based names.
* **team_memberships**: Many-to-many user-team relationships.
* **projects**: Collections of tasks.
* **sections**: Subdivisions within projects (To Do, In Progress, Done).
* **tasks**: Core unit of work (supports subtasks via `parent_task_id`).

### Metadata Tables

* **comments**: Task discussions and updates.
* **custom_field_definitions**: Project-specific field settings.
* **custom_field_values**: Actual values for custom fields on tasks.
* **tags**: Cross-project labels.
* **task_tags**: Task-tag associations.
* **attachments**: Simulated file metadata.

## Key Design Decisions

* **Custom Fields**: Handled with separate tables for definitions (per-project) and values (per-task), allowing flexible field types (dropdown, text, number, date, checkbox).
* **Task Hierarchy**: Uses a single tasks table with a self-referential `parent_task_id`. Subtasks reference parents via this field (NULL for top-level tasks).
* **Temporal Consistency**: All timestamps are validated. Tasks cannot be completed before creation, and due dates respect business days (85% avoid weekends).

## Data Quality Checks

Run these queries to verify data quality:

**Check temporal consistency:**

```sql
SELECT COUNT(*) FROM tasks WHERE completed_at < created_at; -- Should be 0

```

**Verify assignment distribution:**

```sql
SELECT ROUND(COUNT(CASE WHEN assignee_id IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) as unassigned_pct FROM tasks; -- Should be ~15%

```

**Verify due date distribution:**

```sql
SELECT CASE 
    WHEN due_date IS NULL THEN 'No due date' 
    WHEN due_date < DATE('now') THEN 'Overdue' 
    WHEN due_date < DATE('now', '+7 days') THEN 'Within 1 week' 
    ELSE 'Other' END as cat, COUNT(*) FROM tasks GROUP BY cat;

```

## Troubleshooting

* **Inconsistent Timestamps:** Check your system clock and verify `start_date < end_date` in `CONFIG`. Ensure `end_date` is not in the future.

## License

All code is provided for evaluation purposes.

```
