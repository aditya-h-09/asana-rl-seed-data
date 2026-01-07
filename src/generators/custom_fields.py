"""
Custom Fields Generator
Creates project-specific custom fields and their values
"""

import random
import json
from utils import generate_uuid, batch_insert

# Common custom field definitions by project type
CUSTOM_FIELD_TEMPLATES = {
    'sprint': [
        {'name': 'Story Points', 'type': 'dropdown', 
         'options': ['1', '2', '3', '5', '8', '13']},
        {'name': 'Sprint', 'type': 'dropdown',
         'options': ['Sprint 1', 'Sprint 2', 'Sprint 3', 'Sprint 4', 'Backlog']},
        {'name': 'Effort', 'type': 'dropdown',
         'options': ['Small', 'Medium', 'Large', 'Extra Large']},
    ],
    'ongoing': [
        {'name': 'Status', 'type': 'dropdown',
         'options': ['Not Started', 'In Progress', 'Blocked', 'Done']},
        {'name': 'Priority', 'type': 'dropdown',
         'options': ['P0', 'P1', 'P2', 'P3']},
    ],
    'campaign': [
        {'name': 'Campaign Phase', 'type': 'dropdown',
         'options': ['Planning', 'Creation', 'Review', 'Launched', 'Analysis']},
        {'name': 'Channel', 'type': 'dropdown',
         'options': ['Email', 'Social', 'Paid Ads', 'Content', 'Events']},
        {'name': 'Target Audience', 'type': 'dropdown',
         'options': ['Enterprise', 'Mid-Market', 'SMB', 'All']},
    ],
    'operations': [
        {'name': 'Department', 'type': 'dropdown',
         'options': ['Finance', 'HR', 'Legal', 'Admin']},
        {'name': 'Approval Status', 'type': 'dropdown',
         'options': ['Pending', 'Approved', 'Rejected', 'Needs Review']},
    ]
}

def generate_custom_fields(conn, projects: list, tasks: list, config: dict):
    """
    Generate custom field definitions and values for projects
    """
    cursor = conn.cursor()
    
    field_definitions = []
    field_values = []
    
    for project in projects:
        project_type = project['project_type']
        templates = CUSTOM_FIELD_TEMPLATES.get(project_type, [])
        
        # Each project gets 1-2 custom fields
        num_fields = random.randint(1, min(2, len(templates)))
        project_templates = random.sample(templates, num_fields) if templates else []
        
        for template in project_templates:
            field_id = generate_uuid()
            
            field_def = {
                'field_id': field_id,
                'project_id': project['project_id'],
                'name': template['name'],
                'field_type': template['type'],
                'options': json.dumps(template.get('options', []))
            }
            
            field_definitions.append((
                field_id,
                project['project_id'],
                template['name'],
                template['type'],
                json.dumps(template.get('options', []))
            ))
            
            # Generate values for tasks in this project
            cursor.execute("""
                SELECT task_id FROM tasks 
                WHERE project_id = ? AND parent_task_id IS NULL
            """, (project['project_id'],))
            
            project_tasks = cursor.fetchall()
            
            for (task_id,) in project_tasks:
                # 70% of tasks have values for custom fields
                if random.random() < 0.70:
                    value_id = generate_uuid()
                    
                    # Select value based on field type
                    if template['type'] == 'dropdown':
                        value = random.choice(template['options'])
                    elif template['type'] == 'number':
                        value = str(random.randint(1, 10))
                    elif template['type'] == 'text':
                        value = "Custom text value"
                    elif template['type'] == 'checkbox':
                        value = str(random.choice([True, False]))
                    else:
                        value = None
                    
                    if value:
                        field_values.append((
                            value_id,
                            task_id,
                            field_id,
                            value
                        ))
    
    # Batch insert
    if field_definitions:
        batch_insert(conn, 'custom_field_definitions',
                    ['field_id', 'project_id', 'name', 'field_type', 'options'],
                    field_definitions)
    
    if field_values:
        batch_insert(conn, 'custom_field_values',
                    ['value_id', 'task_id', 'field_id', 'value'],
                    field_values)
    
    return len(field_values)