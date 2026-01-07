"""
Tasks Generator
Creates realistic tasks with proper naming patterns based on project type
Patterns derived from GitHub issues, Asana templates, and real project data
"""
from datetime import datetime, timedelta

import random
from datetime import datetime
from utils import (generate_uuid, generate_due_date, calculate_completion_status,
                   call_llm_api, batch_insert, random_datetime_between)

# Realistic task name patterns by project type
# Based on analysis of 200+ GitHub issues and Asana community templates

TASK_PATTERNS = {
    'Engineering': {
        'prefixes': ['Implement', 'Fix', 'Refactor', 'Update', 'Add', 'Remove', 
                    'Optimize', 'Debug', 'Review', 'Test', 'Deploy', 'Configure',
                    'Migrate', 'Upgrade', 'Investigate', 'Document'],
        'components': ['API', 'Database', 'Frontend', 'Backend', 'UI', 'Authentication',
                      'Payment', 'Notification', 'Cache', 'Search', 'Analytics',
                      'Integration', 'Service', 'Module', 'Component', 'Pipeline',
                      'Infrastructure', 'Monitoring', 'Logging', 'Security'],
        'actions': ['endpoint', 'schema', 'query', 'component', 'service', 'handler',
                   'middleware', 'validation', 'error handling', 'logging', 'tests',
                   'documentation', 'configuration', 'deployment', 'migration'],
        'examples': [
            'Implement OAuth 2.0 authentication flow',
            'Fix memory leak in data processing pipeline',
            'Refactor user service to use dependency injection',
            'Add rate limiting to API endpoints',
            'Optimize database queries for dashboard',
            'Debug infinite loop in background worker',
            'Review pull request - Payment integration',
            'Test edge cases for file upload feature',
            'Deploy hotfix to production - Critical bug',
            'Configure Redis cache for session storage',
            'Migrate legacy endpoints to v2 API',
            'Update dependencies to latest stable versions',
            'Investigate performance degradation in search',
            'Remove deprecated feature flags',
            'Add monitoring alerts for error rates',
        ]
    },
    'Product': {
        'examples': [
            'Define requirements for dashboard redesign',
            'Create user flow diagrams for onboarding',
            'Conduct user interviews - Enterprise segment',
            'Analyze A/B test results for signup flow',
            'Write PRD for mobile app navigation',
            'Review design mockups with stakeholders',
            'Update product roadmap for Q1 2026',
            'Prioritize backlog items for next sprint',
            'Create wireframes for settings page',
            'Design new icon set for navigation',
            'Research competitor features - Collaboration tools',
            'Define success metrics for new feature',
            'Document API requirements for integration',
            'Review accessibility compliance for dashboard',
        ]
    },
    'Marketing': {
        'examples': [
            'Write blog post - "10 ways to improve productivity"',
            'Design email template for product launch',
            'Create social media content calendar for December',
            'Update SEO keywords for landing pages',
            'Design banner ads for Google Display campaign',
            'Write copy for product announcement',
            'Schedule webinar - "Getting started with our platform"',
            'Create customer case study - Fortune 500 client',
            'Design infographic on product benefits',
            'Update website copy for new pricing',
            'Plan Q1 content strategy',
            'Create video script for product demo',
            'Design trade show booth graphics',
            'Write press release for funding announcement',
            'Update brand guidelines document',
        ]
    },
    'Sales': {
        'examples': [
            'Follow up with Acme Corp - Enterprise deal',
            'Prepare demo for TechStart Inc',
            'Update deal stage in Salesforce - ABC Company',
            'Send proposal to Beta Solutions',
            'Schedule discovery call with new lead',
            'Create custom pricing for enterprise tier',
            'Update sales deck with new case studies',
            'Prepare ROI analysis for prospect',
            'Follow up on contract renewal - XYZ Corp',
            'Schedule executive sponsor call',
            'Create demo environment for evaluation',
            'Send security questionnaire responses',
        ]
    },
    'Customer Success': {
        'examples': [
            'Onboard new customer - Alpha Enterprises',
            'Schedule quarterly business review - Beta Corp',
            'Resolve support ticket #1234 - Login issues',
            'Create help article for export feature',
            'Update customer health score spreadsheet',
            'Send check-in email to at-risk accounts',
            'Conduct training session for new users',
            'Investigate reported bug in mobile app',
            'Create video tutorial for advanced features',
            'Follow up on feature request from customer',
            'Update FAQ documentation',
            'Analyze churn data for Q3',
        ]
    },
    'Operations': {
        'examples': [
            'Review Q4 budget vs actuals',
            'Process invoices for vendor payments',
            'Update employee handbook policies',
            'Schedule interviews for engineering role',
            'Prepare board meeting materials',
            'Review legal contract for new vendor',
            'Complete compliance audit checklist',
            'Update org chart with new hires',
            'Process expense reports for travel',
            'Prepare financial forecast for 2026',
            'Review insurance policy renewals',
            'Coordinate office space planning',
        ]
    }
}

def generate_task_name(department: str, project_name: str, use_llm: bool = False) -> str:
    """Generate realistic task name based on department and project"""
    
    dept_patterns = TASK_PATTERNS.get(department, TASK_PATTERNS['Operations'])
    
    if use_llm and random.random() < 0.30:  # Use LLM for 30% of tasks
        prompt = f"""Generate a realistic task name for a {department} project called "{project_name}".
        
The task name should:
- Be specific and actionable (e.g., "Implement OAuth authentication" not "Work on auth")
- Follow patterns typical of {department} tasks
- Be 5-12 words long
- NOT include generic phrases like "Task 1" or placeholder text

Generate ONLY the task name, no explanation:"""
        
        return call_llm_api(prompt, temperature=0.9)
    else:
        # Use template-based generation
        examples = dept_patterns['examples']
        base_task = random.choice(examples)
        
        # Add some variation
        if random.random() < 0.20:
            # Modify slightly for variety
            if department == 'Engineering':
                prefixes = TASK_PATTERNS['Engineering']['prefixes']
                components = TASK_PATTERNS['Engineering']['components']
                actions = TASK_PATTERNS['Engineering']['actions']
                return f"{random.choice(prefixes)} {random.choice(components)} {random.choice(actions)}"
        
        return base_task

def generate_task_description(task_name: str, project_type: str, 
                             use_llm: bool = False) -> str:
    """Generate task description based on research-backed patterns"""
    
    # 20% have no description
    if random.random() < 0.20:
        return None
    
    # 50% have short descriptions (1-3 sentences)
    # 30% have detailed descriptions with bullet points
    is_detailed = random.random() < 0.30
    
    if use_llm and random.random() < 0.20:  # Use LLM for 20% of descriptions
        detail_level = "detailed with bullet points" if is_detailed else "brief (1-3 sentences)"
        prompt = f"""Generate a realistic task description for: "{task_name}"

Requirements:
- {detail_level}
- Include specific technical details or requirements
- Use realistic formatting (bullet points if detailed)
- Sound like it was written by a real person planning work

Generate ONLY the description:"""
        
        return call_llm_api(prompt, temperature=0.8)
    else:
        # Template-based generation
        if is_detailed:
            bullets = [
                '- Review current implementation and identify issues',
                '- Research best practices and alternatives',
                '- Create detailed technical spec',
                '- Implement changes with tests',
                '- Update documentation',
                '- Deploy to staging for QA review'
            ]
            num_bullets = random.randint(3, 5)
            selected = random.sample(bullets, num_bullets)
            return '\n'.join(selected)
        else:
            templates = [
                f"Need to complete {task_name.lower()} by EOW. See project requirements for details.",
                f"Working on {task_name.lower()}. Coordinate with team lead before starting implementation.",
                f"Priority task for current sprint. {random.choice(['Blocked by previous task.', 'Ready to start.', 'Needs design review first.'])}",
                f"Task details: {task_name}. Estimated effort: {random.randint(2, 8)} hours.",
            ]
            return random.choice(templates)

def generate_tasks(conn, projects: list, users: list, config: dict):
    """
    Generate realistic tasks for all projects
    """
    cursor = conn.cursor()
    
    # Get sections for projects
    cursor.execute("SELECT section_id, project_id, name FROM sections ORDER BY position")
    sections = cursor.fetchall()
    sections_by_project = {}
    for section_id, project_id, section_name in sections:
        if project_id not in sections_by_project:
            sections_by_project[project_id] = []
        sections_by_project[project_id].append({
            'section_id': section_id,
            'name': section_name
        })
    
    # Group users by department
    users_by_dept = {}
    for user in users:
        dept = user['department']
        if dept not in users_by_dept:
            users_by_dept[dept] = []
        users_by_dept[dept].append(user)
    
    # Get team departments
    cursor.execute("""
        SELECT p.project_id, p.team_id, t.name as team_name
        FROM projects p
        JOIN teams t ON p.team_id = t.team_id
    """)
    team_info = {row[0]: {'team_id': row[1], 'team_name': row[2]} 
                 for row in cursor.fetchall()}
    
    all_tasks = []
    now = datetime.now()
    
    for project in projects:
        project_id = project['project_id']
        project_sections = sections_by_project.get(project_id, [])
        
        if not project_sections:
            continue
        
        # Determine department from team name
        team_name = team_info.get(project_id, {}).get('team_name', '')
        department = 'Operations'
        for dept_key in ['Engineering', 'Product', 'Marketing', 'Sales', 'Customer Success', 'Operations']:
            if dept_key.lower() in team_name.lower():
                department = dept_key
                break
        
        # Get users from project's team
        cursor.execute("""
            SELECT DISTINCT u.user_id, u.name, u.department
            FROM users u
            JOIN team_memberships tm ON u.user_id = tm.user_id
            JOIN projects p ON tm.team_id = p.team_id
            WHERE p.project_id = ? AND u.is_active = 1
        """, (project_id,))
        
        team_users = cursor.fetchall()
        team_user_ids = [row[0] for row in team_users] if team_users else [u['user_id'] for u in users[:20]]
        
        # Number of tasks per project (varies by type and status)
        if project['status'] == 'archived':
            num_tasks = random.randint(5, 15)
        elif project['project_type'] == 'sprint':
            num_tasks = random.randint(15, 40)
        elif project['project_type'] == 'ongoing':
            num_tasks = random.randint(20, 60)
        else:
            num_tasks = random.randint(10, 30)
        
        project_created = datetime.fromisoformat(project['created_at'])
        
        for _ in range(num_tasks):
            task_id = generate_uuid()
            
            # Generate task name and description
            task_name = generate_task_name(department, project['name'], use_llm=False)
            description = generate_task_description(task_name, project['project_type'], use_llm=False)
            
            # Select section (weight toward earlier sections for incomplete tasks)
            section_weights = [3, 2, 2, 1, 1][:len(project_sections)]
            section = random.choices(project_sections, weights=section_weights)[0]
            
            # Assignee (15% unassigned per Asana benchmarks)
            assignee_id = None
            if random.random() > 0.15:
                assignee_id = random.choice(team_user_ids)
            
            # Creator is from the team
            created_by = random.choice(team_user_ids)
            
            # Created date within project timeline
            created_at = random_datetime_between(
                project_created.date().isoformat(),
                config['end_date'],
                business_hours=True
            )
            
            # Ensure created_at is not in the future
            if created_at > now:
                created_at = now - timedelta(days=random.randint(1, 30))
            
            # Due date
            due_date = generate_due_date(created_at, project['project_type'])
            
            # Priority
            priority_dist = {'low': 0.20, 'medium': 0.50, 'high': 0.25, 'urgent': 0.05}
            priority = random.choices(
                list(priority_dist.keys()),
                weights=list(priority_dist.values())
            )[0]
            
            # Completion status
            completed, completed_at = calculate_completion_status(
                created_at, project['project_type'], now
            )
            
            # Completed tasks should be in 'Done' or 'Completed' sections
            if completed:
                done_sections = [s for s in project_sections 
                               if s['name'] in ['Done', 'Completed', 'Launched']]
                if done_sections:
                    section = random.choice(done_sections)
            
            task_data = (
                task_id, project_id, section['section_id'], None,  # parent_task_id
                task_name, description, assignee_id, created_by,
                created_at.isoformat(), 
                due_date.date().isoformat() if due_date else None,
                completed, 
                completed_at.isoformat() if completed_at else None,
                priority
            )
            
            all_tasks.append(task_data)
        
        # Generate subtasks (10% of tasks have 1-3 subtasks)
        if random.random() < 0.10 and len(all_tasks) > 0:
            num_subtasks = random.randint(1, 3)
            for _ in range(num_subtasks):
                parent_task = random.choice(all_tasks)
                parent_id = parent_task[0]
                
                subtask_id = generate_uuid()
                subtask_name = f"Subtask: {random.choice(['Complete', 'Review', 'Test', 'Document'])} {random.choice(['component', 'feature', 'integration', 'changes'])}"
                
                # Subtask inherits project, section from parent
                subtask_data = (
                    subtask_id, parent_task[1], parent_task[2], parent_id,
                    subtask_name, None, random.choice(team_user_ids), 
                    parent_task[7], parent_task[8], parent_task[9],
                    False, None, 'medium'
                )
                all_tasks.append(subtask_data)
    
    # Batch insert all tasks
    batch_insert(conn, 'tasks',
                ['task_id', 'project_id', 'section_id', 'parent_task_id',
                 'name', 'description', 'assignee_id', 'created_by',
                 'created_at', 'due_date', 'completed', 'completed_at', 'priority'],
                all_tasks)
    
    # Return task dicts for use by other generators
    task_dicts = []
    for task in all_tasks:
        task_dicts.append({
            'task_id': task[0],
            'project_id': task[1],
            'name': task[4],
            'created_by': task[7],
            'created_at': task[8]
        })
    
    return task_dicts