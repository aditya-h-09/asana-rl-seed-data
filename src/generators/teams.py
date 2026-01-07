"""
Teams Generator
Creates realistic teams for product development, marketing, and operations
"""

import random
from datetime import timedelta
from utils import generate_uuid

# Team definitions based on typical B2B SaaS org structure
TEAM_TEMPLATES = [
    # Engineering teams
    {'name': 'Platform Engineering', 'department': 'Engineering', 
     'description': 'Core platform infrastructure and scalability'},
    {'name': 'Frontend Engineering', 'department': 'Engineering',
     'description': 'Web and mobile application development'},
    {'name': 'Backend Engineering', 'department': 'Engineering',
     'description': 'API and backend services development'},
    {'name': 'Data Engineering', 'department': 'Engineering',
     'description': 'Data pipelines and analytics infrastructure'},
    {'name': 'Security Engineering', 'department': 'Engineering',
     'description': 'Application and infrastructure security'},
    {'name': 'DevOps', 'department': 'Engineering',
     'description': 'CI/CD and infrastructure automation'},
    {'name': 'Mobile Engineering', 'department': 'Engineering',
     'description': 'iOS and Android native applications'},
    {'name': 'ML Engineering', 'department': 'Engineering',
     'description': 'Machine learning models and systems'},
    
    # Product teams
    {'name': 'Product Management', 'department': 'Product',
     'description': 'Product strategy and roadmap planning'},
    {'name': 'Product Design', 'department': 'Product',
     'description': 'UX/UI design and user research'},
    {'name': 'Product Analytics', 'department': 'Product',
     'description': 'User behavior analysis and metrics'},
    
    # Marketing teams
    {'name': 'Growth Marketing', 'department': 'Marketing',
     'description': 'User acquisition and growth initiatives'},
    {'name': 'Content Marketing', 'department': 'Marketing',
     'description': 'Blog, guides, and educational content'},
    {'name': 'Product Marketing', 'department': 'Marketing',
     'description': 'Go-to-market strategy and positioning'},
    {'name': 'Demand Generation', 'department': 'Marketing',
     'description': 'Lead generation and nurturing campaigns'},
    {'name': 'Brand & Creative', 'department': 'Marketing',
     'description': 'Brand identity and creative assets'},
    
    # Sales teams
    {'name': 'Enterprise Sales', 'department': 'Sales',
     'description': 'Large enterprise account management'},
    {'name': 'Mid-Market Sales', 'department': 'Sales',
     'description': 'Mid-sized business sales'},
    {'name': 'Sales Engineering', 'department': 'Sales',
     'description': 'Technical sales support and demos'},
    
    # Customer Success
    {'name': 'Customer Success', 'department': 'Customer Success',
     'description': 'Customer onboarding and support'},
    {'name': 'Technical Support', 'department': 'Customer Success',
     'description': 'Technical troubleshooting and issue resolution'},
    
    # Operations
    {'name': 'Business Operations', 'department': 'Operations',
     'description': 'Internal operations and process optimization'},
    {'name': 'Finance & Accounting', 'department': 'Operations',
     'description': 'Financial planning and accounting'},
    {'name': 'People Operations', 'department': 'Operations',
     'description': 'HR and employee experience'},
    {'name': 'Legal & Compliance', 'department': 'Operations',
     'description': 'Legal affairs and regulatory compliance'},
]

def generate_teams(conn, org: dict, config: dict):
    """
    Generate teams for the organization
    
    Args:
        conn: Database connection
        org: Organization dict
        config: Configuration
    
    Returns:
        List of team dicts
    """
    cursor = conn.cursor()
    teams = []
    
    org_created = org['created_at']
    
    for template in TEAM_TEMPLATES:
        team_id = generate_uuid()
        
        # Teams created 0-6 months after org (staggered formation)
        days_after_org = random.randint(0, 180)
        from datetime import datetime
        created_at = datetime.fromisoformat(org_created) + timedelta(days=days_after_org)
        
        team = {
            'team_id': team_id,
            'org_id': org['org_id'],
            'name': template['name'],
            'description': template['description'],
            'department': template['department'],
            'created_at': created_at.isoformat()
        }
        
        cursor.execute("""
            INSERT INTO teams (team_id, org_id, name, description, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (team_id, org['org_id'], template['name'], 
              template['description'], created_at))
        
        teams.append(team)
    
    conn.commit()
    return teams