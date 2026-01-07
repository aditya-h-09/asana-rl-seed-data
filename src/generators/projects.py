"""
Projects Generator
Creates realistic projects based on team type and real-world patterns
"""

import random
from datetime import datetime, timedelta
from utils import generate_uuid, random_date_between, batch_insert

# Project templates by department (sourced from Asana templates, ProductHunt, GitHub)
PROJECT_TEMPLATES = {
    'Engineering': [
        {'name': 'Q4 2025 Sprint Planning', 'type': 'sprint'},
        {'name': 'API v2.0 Migration', 'type': 'sprint'},
        {'name': 'Performance Optimization Initiative', 'type': 'sprint'},
        {'name': 'Security Audit & Remediation', 'type': 'sprint'},
        {'name': 'Bug Tracking & Resolution', 'type': 'ongoing'},
        {'name': 'Technical Debt Backlog', 'type': 'ongoing'},
        {'name': 'Infrastructure Modernization', 'type': 'sprint'},
        {'name': 'Mobile App Redesign - iOS', 'type': 'sprint'},
        {'name': 'Data Pipeline Architecture', 'type': 'sprint'},
        {'name': 'Microservices Migration', 'type': 'sprint'},
        {'name': 'CI/CD Pipeline Improvements', 'type': 'ongoing'},
        {'name': 'Kubernetes Cluster Upgrade', 'type': 'sprint'},
        {'name': 'ML Model Training Pipeline', 'type': 'sprint'},
        {'name': 'Authentication System Overhaul', 'type': 'sprint'},
        {'name': 'Database Sharding Implementation', 'type': 'sprint'},
    ],
    'Product': [
        {'name': '2025 Product Roadmap', 'type': 'ongoing'},
        {'name': 'User Research - Enterprise Customers', 'type': 'sprint'},
        {'name': 'Q1 Feature Prioritization', 'type': 'sprint'},
        {'name': 'Dashboard Redesign Project', 'type': 'sprint'},
        {'name': 'A/B Testing Framework', 'type': 'sprint'},
        {'name': 'Product Analytics Setup', 'type': 'sprint'},
        {'name': 'Customer Feedback Loop', 'type': 'ongoing'},
        {'name': 'Onboarding Flow Optimization', 'type': 'sprint'},
        {'name': 'Mobile App UX Research', 'type': 'sprint'},
        {'name': 'Design System Evolution', 'type': 'ongoing'},
    ],
    'Marketing': [
        {'name': 'Q4 2025 Campaign Planning', 'type': 'campaign'},
        {'name': 'Product Launch - Enterprise Tier', 'type': 'campaign'},
        {'name': 'Content Calendar - Q1 2026', 'type': 'campaign'},
        {'name': 'SEO Optimization Project', 'type': 'ongoing'},
        {'name': 'Brand Refresh Initiative', 'type': 'campaign'},
        {'name': 'Webinar Series - Fall 2025', 'type': 'campaign'},
        {'name': 'Customer Case Studies', 'type': 'ongoing'},
        {'name': 'Paid Advertising - Google Ads', 'type': 'campaign'},
        {'name': 'Email Marketing Automation', 'type': 'ongoing'},
        {'name': 'Social Media Strategy', 'type': 'ongoing'},
        {'name': 'Conference Sponsorships 2026', 'type': 'campaign'},
        {'name': 'Partner Co-Marketing', 'type': 'campaign'},
    ],
    'Sales': [
        {'name': 'Q4 2025 Sales Pipeline', 'type': 'ongoing'},
        {'name': 'Enterprise Deal Management', 'type': 'ongoing'},
        {'name': 'Sales Enablement Materials', 'type': 'ongoing'},
        {'name': 'CRM Migration - Salesforce', 'type': 'sprint'},
        {'name': 'Sales Training - New Product', 'type': 'sprint'},
        {'name': 'Account Expansion Strategy', 'type': 'ongoing'},
        {'name': 'Demo Environment Setup', 'type': 'sprint'},
    ],
    'Customer Success': [
        {'name': 'Customer Onboarding Process', 'type': 'ongoing'},
        {'name': 'Support Ticket Management', 'type': 'ongoing'},
        {'name': 'Customer Health Scoring', 'type': 'sprint'},
        {'name': 'Documentation Updates', 'type': 'ongoing'},
        {'name': 'Quarterly Business Reviews', 'type': 'ongoing'},
        {'name': 'Customer Training Webinars', 'type': 'campaign'},
    ],
    'Operations': [
        {'name': 'Q4 Financial Planning', 'type': 'operations'},
        {'name': 'Office Expansion - Austin', 'type': 'operations'},
        {'name': 'Legal Contract Templates', 'type': 'ongoing'},
        {'name': 'Compliance Audit Prep', 'type': 'operations'},
        {'name': 'HR Policy Updates', 'type': 'operations'},
        {'name': 'Recruiting Pipeline', 'type': 'ongoing'},
        {'name': 'Annual Planning 2026', 'type': 'operations'},
    ]
}

# Section templates by project type
SECTION_TEMPLATES = {
    'sprint': ['Backlog', 'To Do', 'In Progress', 'In Review', 'Done'],
    'ongoing': ['Incoming', 'Prioritized', 'In Progress', 'Completed'],
    'campaign': ['Planning', 'In Progress', 'Review & Approval', 'Launched', 'Post-Mortem'],
    'operations': ['To Do', 'In Progress', 'Blocked', 'Completed']
}

def generate_projects(conn, teams: list, users: list, config: dict):
    """
    Generate realistic projects for each team
    """
    projects = []
    sections_data = []
    
    start_date = config['start_date']
    end_date = config['end_date']
    
    # Group teams and users by department
    teams_by_dept = {}
    for team in teams:
        dept = team.get('department', 'Operations')
        if dept not in teams_by_dept:
            teams_by_dept[dept] = []
        teams_by_dept[dept].append(team)
    
    users_by_dept = {}
    for user in users:
        dept = user['department']
        if dept not in users_by_dept:
            users_by_dept[dept] = []
        users_by_dept[dept].append(user)
    
    # Generate projects for each team
    for team in teams:
        dept = team.get('department', 'Operations')
        templates = PROJECT_TEMPLATES.get(dept, PROJECT_TEMPLATES['Operations'])
        
        # Each team gets 2-5 projects
        num_projects = random.randint(2, 5)
        team_templates = random.sample(templates, min(num_projects, len(templates)))
        
        for template in team_templates:
            project_id = generate_uuid()
            
            # Project name
            name = template['name']
            project_type = template['type']
            
            # Description (30% have descriptions)
            description = None
            if random.random() < 0.30:
                description = f"Project for {name}. Key objectives and deliverables to be tracked."
            
            # Project status
            status_weights = [0.70, 0.25, 0.05]  # active, archived, on_hold
            status = random.choices(['active', 'archived', 'on_hold'], 
                                  weights=status_weights)[0]
            
            # Owner from team's department
            dept_users = users_by_dept.get(dept, users)
            owner = random.choice(dept_users) if dept_users else random.choice(users)
            
            # Created date
            created_at = random_date_between(start_date, end_date, weight_to_start=True)
            
            # Due date (sprint projects have due dates, ongoing ones often don't)
            due_date = None
            if project_type == 'sprint':
                # Sprint projects: 2-6 weeks duration
                weeks = random.randint(2, 6)
                due_date = created_at + timedelta(weeks=weeks)
            elif project_type == 'campaign':
                # Campaign projects: 1-3 months
                months = random.randint(1, 3)
                due_date = created_at + timedelta(days=30*months)
            elif project_type == 'operations':
                if random.random() < 0.50:  # 50% have due dates
                    months = random.randint(1, 4)
                    due_date = created_at + timedelta(days=30*months)
            
            project = {
                'project_id': project_id,
                'team_id': team['team_id'],
                'name': name,
                'description': description,
                'project_type': project_type,
                'status': status,
                'owner_id': owner['user_id'],
                'created_at': created_at.isoformat(),
                'due_date': due_date.isoformat() if due_date else None
            }
            
            projects.append(project)
            
            # Create sections for this project
            section_names = SECTION_TEMPLATES[project_type]
            for position, section_name in enumerate(section_names):
                section_id = generate_uuid()
                sections_data.append((
                    section_id,
                    project_id,
                    section_name,
                    position
                ))
    
    # Batch insert projects
    project_data = [
        (p['project_id'], p['team_id'], p['name'], p['description'],
         p['project_type'], p['status'], p['owner_id'], p['created_at'], p['due_date'])
        for p in projects
    ]
    
    batch_insert(conn, 'projects',
                ['project_id', 'team_id', 'name', 'description', 'project_type',
                 'status', 'owner_id', 'created_at', 'due_date'],
                project_data)
    
    # Batch insert sections
    batch_insert(conn, 'sections',
                ['section_id', 'project_id', 'name', 'position'],
                sections_data)
    
    return projects