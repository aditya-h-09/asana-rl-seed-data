-- Asana Simulation Database Schema
-- Designed for SQLite

-- Organizations/Workspaces
CREATE TABLE organizations (
    org_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    employee_count INTEGER NOT NULL
);

-- Teams within an organization
CREATE TABLE teams (
    team_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);

-- Users/Members
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    job_title TEXT,
    department TEXT,
    created_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);

-- Team memberships (many-to-many)
CREATE TABLE team_memberships (
    membership_id TEXT PRIMARY KEY,
    team_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT CHECK(role IN ('member', 'lead', 'admin')),
    joined_at TIMESTAMP NOT NULL,
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    UNIQUE(team_id, user_id)
);

-- Projects
CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,
    team_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    project_type TEXT CHECK(project_type IN ('sprint', 'ongoing', 'campaign', 'operations')),
    status TEXT CHECK(status IN ('active', 'archived', 'on_hold')),
    owner_id TEXT,
    created_at TIMESTAMP NOT NULL,
    due_date DATE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (owner_id) REFERENCES users(user_id)
);

-- Sections within projects (e.g., To Do, In Progress, Done)
CREATE TABLE sections (
    section_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- Tasks (includes both top-level tasks and subtasks)
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    section_id TEXT,
    parent_task_id TEXT,  -- NULL for top-level tasks, references task_id for subtasks
    name TEXT NOT NULL,
    description TEXT,
    assignee_id TEXT,
    created_by TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    due_date DATE,
    completed BOOLEAN DEFAULT 0,
    completed_at TIMESTAMP,
    priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'urgent')),
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (section_id) REFERENCES sections(section_id),
    FOREIGN KEY (parent_task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (assignee_id) REFERENCES users(user_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    CHECK (completed = 0 OR completed_at IS NOT NULL),
    CHECK (completed_at IS NULL OR completed_at >= created_at)
);

-- Comments/Stories on tasks
CREATE TABLE comments (
    comment_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Custom field definitions (project-specific)
CREATE TABLE custom_field_definitions (
    field_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    field_type TEXT CHECK(field_type IN ('text', 'number', 'dropdown', 'date', 'checkbox')),
    options TEXT,  -- JSON array for dropdown options
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- Custom field values for tasks
CREATE TABLE custom_field_values (
    value_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    field_id TEXT NOT NULL,
    value TEXT,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (field_id) REFERENCES custom_field_definitions(field_id),
    UNIQUE(task_id, field_id)
);

-- Tags (can be applied across projects)
CREATE TABLE tags (
    tag_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    name TEXT NOT NULL,
    color TEXT,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id),
    UNIQUE(org_id, name)
);

-- Task-Tag associations (many-to-many)
CREATE TABLE task_tags (
    task_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,
    PRIMARY KEY (task_id, tag_id),
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
);

-- Attachments
CREATE TABLE attachments (
    attachment_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT,
    file_size INTEGER,
    uploaded_by TEXT NOT NULL,
    uploaded_at TIMESTAMP NOT NULL,
    url TEXT,  -- Simulated URL
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (uploaded_by) REFERENCES users(user_id)
);

-- Indexes for performance
CREATE INDEX idx_users_org ON users(org_id);
CREATE INDEX idx_teams_org ON teams(org_id);
CREATE INDEX idx_projects_team ON projects(team_id);
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_tasks_parent ON tasks(parent_task_id);
CREATE INDEX idx_comments_task ON comments(task_id);
CREATE INDEX idx_team_memberships_team ON team_memberships(team_id);
CREATE INDEX idx_team_memberships_user ON team_memberships(user_id);