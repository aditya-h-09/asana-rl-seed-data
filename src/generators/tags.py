"""
Tags Generator
Creates organization-wide tags that can be applied across projects
"""

import random
from utils import generate_uuid, batch_insert

# Common tags used across organizations
TAG_TEMPLATES = [
    {'name': 'urgent', 'color': '#FF0000'},
    {'name': 'bug', 'color': '#DC143C'},
    {'name': 'feature', 'color': '#4169E1'},
    {'name': 'technical-debt', 'color': '#FF8C00'},
    {'name': 'documentation', 'color': '#32CD32'},
    {'name': 'security', 'color': '#8B0000'},
    {'name': 'performance', 'color': '#FF6347'},
    {'name': 'ui-ux', 'color': '#9370DB'},
    {'name': 'backend', 'color': '#4682B4'},
    {'name': 'frontend', 'color': '#20B2AA'},
    {'name': 'mobile', 'color': '#FF69B4'},
    {'name': 'api', 'color': '#6495ED'},
    {'name': 'database', 'color': '#CD853F'},
    {'name': 'testing', 'color': '#9ACD32'},
    {'name': 'deployment', 'color': '#FF4500'},
    {'name': 'blocked', 'color': '#B22222'},
    {'name': 'needs-review', 'color': '#FFA500'},
    {'name': 'customer-request', 'color': '#1E90FF'},
    {'name': 'quick-win', 'color': '#32CD32'},
    {'name': 'research', 'color': '#9932CC'},
]

def generate_tags(conn, org: dict, tasks: list, config: dict):
    """
    Generate tags and apply them to tasks
    """
    cursor = conn.cursor()
    
    # Create tags for organization
    tags_data = []
    tag_ids = {}
    
    for template in TAG_TEMPLATES:
        tag_id = generate_uuid()
        tags_data.append((
            tag_id,
            org['org_id'],
            template['name'],
            template['color']
        ))
        tag_ids[template['name']] = tag_id
    
    batch_insert(conn, 'tags',
                ['tag_id', 'org_id', 'name', 'color'],
                tags_data)
    
    # Apply tags to tasks (30% of tasks have 1-2 tags)
    cursor.execute("SELECT task_id FROM tasks WHERE parent_task_id IS NULL")
    task_rows = cursor.fetchall()
    
    task_tags_data = []
    for (task_id,) in task_rows:
        if random.random() < 0.30:
            # Apply 1-2 tags
            num_tags = random.choices([1, 2], weights=[0.70, 0.30])[0]
            selected_tags = random.sample(list(tag_ids.keys()), num_tags)
            
            for tag_name in selected_tags:
                task_tags_data.append((
                    task_id,
                    tag_ids[tag_name]
                ))
    
    if task_tags_data:
        batch_insert(conn, 'task_tags',
                    ['task_id', 'tag_id'],
                    task_tags_data)
    
    return tags_data