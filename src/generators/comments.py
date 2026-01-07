"""
Comments Generator
Creates realistic task comments and activity
"""

import random
from datetime import datetime, timedelta
from utils import generate_uuid, batch_insert

COMMENT_TEMPLATES = [
    "Started working on this task.",
    "Making good progress. Should be done by EOD.",
    "Blocked by {blocker}. Need help from team.",
    "Completed initial implementation. Ready for review.",
    "Updated the approach based on feedback.",
    "Added test cases for edge conditions.",
    "This is taking longer than expected due to {reason}.",
    "Quick update: {status}",
    "Coordinating with {team} team on this.",
    "Question: {question}",
    "FYI @{person} - this relates to your work on {related}.",
    "Pushing this to next sprint due to {reason}.",
    "Moving forward with Option A after team discussion.",
    "Documentation updated in the wiki.",
    "Deployed to staging for testing.",
    "Found an issue with {component}. Investigating.",
    "Code review complete. Looks good to merge.",
    "Need design input on {aspect}.",
    "Performance looks good after optimization.",
    "Following up on this from standup discussion.",
]

BLOCKERS = ["dependency not ready", "waiting on API access", "blocked by infrastructure issue", 
            "needs approval", "waiting on design"]
REASONS = ["complexity", "scope creep", "technical debt", "unexpected edge cases", "dependency delays"]
STATUSES = ["50% complete", "almost done", "in final review", "waiting for feedback", "needs testing"]
QUESTIONS = ["should we include error handling for X?", "what's the expected behavior for edge case Y?",
            "is this the right approach?", "need clarification on requirements"]
RELATED_ITEMS = ["authentication", "API integration", "dashboard updates", "database migration"]

def generate_comment_content() -> str:
    """Generate realistic comment content"""
    template = random.choice(COMMENT_TEMPLATES)
    
    # Fill in template variables
    if '{blocker}' in template:
        template = template.replace('{blocker}', random.choice(BLOCKERS))
    if '{reason}' in template:
        template = template.replace('{reason}', random.choice(REASONS))
    if '{status}' in template:
        template = template.replace('{status}', random.choice(STATUSES))
    if '{question}' in template:
        template = template.replace('{question}', random.choice(QUESTIONS))
    if '{component}' in template:
        template = template.replace('{component}', random.choice(['API', 'UI', 'database', 'service']))
    if '{aspect}' in template:
        template = template.replace('{aspect}', random.choice(['layout', 'interaction', 'styling', 'flow']))
    if '{team}' in template:
        template = template.replace('{team}', random.choice(['product', 'engineering', 'design']))
    if '{related}' in template:
        template = template.replace('{related}', random.choice(RELATED_ITEMS))
    if '{person}' in template:
        template = template.replace('{person}', random.choice(['Sarah', 'John', 'Alex', 'Maria']))
    
    return template

def generate_comments(conn, tasks: list, users: list, config: dict):
    """
    Generate comments for tasks
    
    Based on research:
    - 40% of tasks have no comments
    - 35% have 1-2 comments  
    - 20% have 3-5 comments
    - 5% have 6+ comments (very active discussions)
    """
    cursor = conn.cursor()
    comments_data = []
    
    # Get full task data including assignee
    cursor.execute("""
        SELECT task_id, assignee_id, created_by, created_at, completed_at, project_id
        FROM tasks
        WHERE parent_task_id IS NULL
    """)
    task_rows = cursor.fetchall()
    
    # Get project team members
    project_members = {}
    for task_id, _, _, _, _, project_id in task_rows:
        if project_id not in project_members:
            cursor.execute("""
                SELECT DISTINCT u.user_id
                FROM users u
                JOIN team_memberships tm ON u.user_id = tm.user_id
                JOIN projects p ON tm.team_id = p.team_id
                WHERE p.project_id = ? AND u.is_active = 1
                LIMIT 10
            """, (project_id,))
            project_members[project_id] = [row[0] for row in cursor.fetchall()]
    
    for task_id, assignee_id, created_by, created_at, completed_at, project_id in task_rows:
        # Determine number of comments
        rand = random.random()
        if rand < 0.40:
            num_comments = 0
        elif rand < 0.75:
            num_comments = random.randint(1, 2)
        elif rand < 0.95:
            num_comments = random.randint(3, 5)
        else:
            num_comments = random.randint(6, 10)
        
        if num_comments == 0:
            continue
        
        # Get potential commenters (assignee, creator, team members)
        potential_commenters = list(set([created_by] + 
                                       ([assignee_id] if assignee_id else []) +
                                       project_members.get(project_id, [])[:5]))
        
        if not potential_commenters:
            continue
        
        task_created = datetime.fromisoformat(created_at)
        task_completed = datetime.fromisoformat(completed_at) if completed_at else datetime.now()
        
        # Generate comments spread over task lifetime
        for i in range(num_comments):
            comment_id = generate_uuid()
            
            # Comments distributed over task lifetime
            progress = (i + 1) / (num_comments + 1)
            days_range = (task_completed - task_created).days
            comment_day = int(days_range * progress)
            
            comment_time = task_created + timedelta(
                days=comment_day,
                hours=random.randint(9, 18),
                minutes=random.randint(0, 59)
            )
            
            # Ensure comment is not in future
            if comment_time > datetime.now():
                comment_time = datetime.now() - timedelta(hours=random.randint(1, 48))
            
            # Select commenter (assignee more likely if exists)
            if assignee_id and random.random() < 0.60:
                commenter = assignee_id
            else:
                commenter = random.choice(potential_commenters)
            
            content = generate_comment_content()
            
            comments_data.append((
                comment_id,
                task_id,
                commenter,
                content,
                comment_time.isoformat()
            ))
    
    # Batch insert
    batch_insert(conn, 'comments',
                ['comment_id', 'task_id', 'user_id', 'content', 'created_at'],
                comments_data)
    
    return comments_data