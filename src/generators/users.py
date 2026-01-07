"""
Users Generator
Creates realistic user profiles with names from census data distributions
"""

import random
from datetime import datetime, timedelta
from utils import generate_uuid, batch_insert

# First names sourced from US Census data (top names representing demographic diversity)
FIRST_NAMES = [
    # Top male names
    'James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph',
    'Thomas', 'Christopher', 'Daniel', 'Matthew', 'Anthony', 'Mark', 'Donald',
    'Steven', 'Andrew', 'Paul', 'Joshua', 'Kenneth', 'Kevin', 'Brian', 'George',
    'Timothy', 'Ronald', 'Edward', 'Jason', 'Jeffrey', 'Ryan', 'Jacob', 'Gary',
    'Nicholas', 'Eric', 'Jonathan', 'Stephen', 'Larry', 'Justin', 'Scott', 'Brandon',
    # Top female names  
    'Mary', 'Patricia', 'Jennifer', 'Linda', 'Barbara', 'Elizabeth', 'Susan',
    'Jessica', 'Sarah', 'Karen', 'Lisa', 'Nancy', 'Betty', 'Margaret', 'Sandra',
    'Ashley', 'Kimberly', 'Emily', 'Donna', 'Michelle', 'Carol', 'Amanda', 'Melissa',
    'Deborah', 'Stephanie', 'Dorothy', 'Rebecca', 'Sharon', 'Laura', 'Cynthia',
    'Amy', 'Angela', 'Helen', 'Anna', 'Brenda', 'Pamela', 'Emma', 'Nicole',
    'Samantha', 'Katherine', 'Christine', 'Debra', 'Rachel', 'Carolyn', 'Janet',
    # Additional diverse names
    'Wei', 'Mohammed', 'Priya', 'Chen', 'Sofia', 'Diego', 'Fatima', 'Raj',
    'Maria', 'Carlos', 'Aisha', 'Luis', 'Mei', 'Hassan', 'Yuki', 'Sandeep'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
    'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson', 'White',
    'Harris', 'Clark', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King',
    'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Green', 'Adams',
    'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts',
    'Gomez', 'Phillips', 'Evans', 'Turner', 'Diaz', 'Parker', 'Cruz', 'Edwards',
    'Collins', 'Reyes', 'Stewart', 'Morris', 'Morales', 'Murphy', 'Cook', 'Rogers',
    'Gutierrez', 'Ortiz', 'Morgan', 'Cooper', 'Peterson', 'Bailey', 'Reed', 'Kelly',
    'Howard', 'Ramos', 'Kim', 'Cox', 'Ward', 'Richardson', 'Watson', 'Brooks',
    'Chavez', 'Wood', 'James', 'Bennett', 'Gray', 'Mendoza', 'Ruiz', 'Hughes',
    'Price', 'Alvarez', 'Castillo', 'Sanders', 'Patel', 'Myers', 'Long', 'Ross',
    'Foster', 'Jimenez', 'Powell', 'Jenkins', 'Perry', 'Russell', 'Sullivan',
    'Bell', 'Coleman', 'Butler', 'Henderson', 'Barnes', 'Gonzales', 'Fisher',
    'Vasquez', 'Simmons', 'Romero', 'Jordan', 'Patterson', 'Alexander', 'Hamilton',
    'Graham', 'Reynolds', 'Griffin', 'Wallace', 'Moreno', 'West', 'Cole', 'Hayes',
    'Bryant', 'Herrera', 'Gibson', 'Ellis', 'Tran', 'Medina', 'Aguilar', 'Stevens',
    'Murray', 'Ford', 'Castro', 'Marshall', 'Owens', 'Harrison', 'Fernandez',
    'McDonald', 'Woods', 'Washington', 'Kennedy', 'Wells', 'Vargas', 'Henry',
    'Chen', 'Freeman', 'Webb', 'Tucker', 'Guzman', 'Burns', 'Crawford', 'Olson'
]

# Job titles by department (based on LinkedIn data patterns)
JOB_TITLES = {
    'Engineering': [
        'Software Engineer', 'Senior Software Engineer', 'Staff Engineer',
        'Principal Engineer', 'Engineering Manager', 'Senior Engineering Manager',
        'Director of Engineering', 'VP of Engineering', 'CTO',
        'Frontend Engineer', 'Backend Engineer', 'Full Stack Engineer',
        'DevOps Engineer', 'Site Reliability Engineer', 'Data Engineer',
        'ML Engineer', 'Security Engineer', 'QA Engineer', 'Infrastructure Engineer'
    ],
    'Product': [
        'Product Manager', 'Senior Product Manager', 'Principal Product Manager',
        'Group Product Manager', 'Director of Product', 'VP of Product', 'CPO',
        'Product Designer', 'Senior Product Designer', 'Lead Designer',
        'Design Manager', 'Director of Design', 'UX Researcher', 'Product Analyst'
    ],
    'Marketing': [
        'Marketing Manager', 'Senior Marketing Manager', 'Director of Marketing',
        'VP of Marketing', 'CMO', 'Content Marketing Manager', 'Growth Manager',
        'Demand Generation Manager', 'Product Marketing Manager', 'Brand Manager',
        'Marketing Coordinator', 'Social Media Manager', 'SEO Specialist',
        'Marketing Analyst', 'Creative Director', 'Copywriter', 'Graphic Designer'
    ],
    'Sales': [
        'Account Executive', 'Senior Account Executive', 'Sales Manager',
        'Senior Sales Manager', 'Director of Sales', 'VP of Sales', 'CRO',
        'Sales Development Representative', 'Business Development Representative',
        'Solutions Engineer', 'Sales Engineer', 'Account Manager',
        'Enterprise Account Executive', 'Regional Sales Manager'
    ],
    'Customer Success': [
        'Customer Success Manager', 'Senior Customer Success Manager',
        'Director of Customer Success', 'VP of Customer Success',
        'Customer Support Specialist', 'Technical Support Engineer',
        'Support Manager', 'Customer Success Coordinator', 'Onboarding Specialist'
    ],
    'Operations': [
        'Operations Manager', 'Senior Operations Manager', 'Director of Operations',
        'VP of Operations', 'COO', 'Business Operations Analyst', 'Finance Manager',
        'Financial Analyst', 'Accountant', 'Senior Accountant', 'Controller',
        'CFO', 'HR Manager', 'Recruiter', 'People Operations Manager',
        'Chief People Officer', 'Legal Counsel', 'Compliance Manager', 'CEO'
    ]
}

def generate_name() -> tuple:
    """Generate realistic full name"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    return first_name, last_name

def generate_email(first_name: str, last_name: str, domain: str, existing_emails: set) -> str:
    """Generate unique email address"""
    # Common email patterns
    patterns = [
        f"{first_name.lower()}.{last_name.lower()}",
        f"{first_name.lower()}{last_name.lower()}",
        f"{first_name[0].lower()}{last_name.lower()}",
        f"{first_name.lower()}{last_name[0].lower()}",
    ]
    
    email = f"{random.choice(patterns)}@{domain}"
    
    # Ensure uniqueness
    counter = 1
    original_email = email
    while email in existing_emails:
        email = f"{original_email.split('@')[0]}{counter}@{domain}"
        counter += 1
    
    return email

def assign_users_to_teams(conn, users, teams):
    """Create team membership associations"""
    cursor = conn.cursor()
    memberships = []
    
    # Group teams by department
    teams_by_dept = {}
    for team in teams:
        dept = team.get('department', 'Operations')
        if dept not in teams_by_dept:
            teams_by_dept[dept] = []
        teams_by_dept[dept].append(team)
    
    for user in users:
        dept = user['department']
        dept_teams = teams_by_dept.get(dept, teams_by_dept.get('Operations', []))
        
        # Assign to 1-2 teams (some users are cross-functional)
        num_teams = random.choices([1, 2], weights=[0.75, 0.25])[0]
        user_teams = random.sample(dept_teams, min(num_teams, len(dept_teams)))
        
        for team in user_teams:
            # Determine role
            if 'Director' in user['job_title'] or 'VP' in user['job_title']:
                role = 'lead'
            elif random.random() < 0.10:
                role = 'admin'
            else:
                role = 'member'
            
            membership_id = generate_uuid()
            joined_at = max(
                datetime.fromisoformat(user['created_at']),
                datetime.fromisoformat(team['created_at'])
            )
            
            memberships.append((
                membership_id,
                team['team_id'],
                user['user_id'],
                role,
                joined_at.isoformat()
            ))
    
    batch_insert(conn, 'team_memberships', 
                ['membership_id', 'team_id', 'user_id', 'role', 'joined_at'],
                memberships)

def generate_users(conn, org: dict, teams: list, config: dict):
    """
    Generate realistic users based on census data distributions
    """
    cursor = conn.cursor()
    users = []
    existing_emails = set()
    
    employee_count = config['employee_count']
    org_created = datetime.fromisoformat(org['created_at'])
    
    # Department distribution (percentages based on typical SaaS companies)
    dept_distribution = {
        'Engineering': 0.35,
        'Sales': 0.20,
        'Customer Success': 0.15,
        'Marketing': 0.12,
        'Product': 0.10,
        'Operations': 0.08
    }
    
    for _ in range(employee_count):
        user_id = generate_uuid()
        first_name, last_name = generate_name()
        email = generate_email(first_name, last_name, org['domain'], existing_emails)
        existing_emails.add(email)
        
        # Assign department
        department = random.choices(
            list(dept_distribution.keys()),
            weights=list(dept_distribution.values())
        )[0]
        
        # Assign job title based on department
        job_title = random.choice(JOB_TITLES[department])
        
        # User joined 0-2 years after org creation
        days_after_org = random.randint(0, 730)
        created_at = org_created + timedelta(days=days_after_org)
        
        # 2% inactive (left company)
        is_active = random.random() > 0.02
        
        user = {
            'user_id': user_id,
            'org_id': org['org_id'],
            'email': email,
            'name': f"{first_name} {last_name}",
            'job_title': job_title,
            'department': department,
            'created_at': created_at.isoformat(),
            'is_active': is_active
        }
        
        users.append(user)
    
    # Batch insert users
    user_data = [(u['user_id'], u['org_id'], u['email'], u['name'], 
                  u['job_title'], u['department'], u['created_at'], u['is_active'])
                 for u in users]
    
    batch_insert(conn, 'users',
                ['user_id', 'org_id', 'email', 'name', 'job_title', 
                 'department', 'created_at', 'is_active'],
                user_data)
    
    # Assign users to teams
    assign_users_to_teams(conn, users, teams)
    
    return users