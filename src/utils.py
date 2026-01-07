"""
Utility functions for data generation
"""

import uuid
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional
import requests
import os
import json

def generate_uuid() -> str:
    """Generate UUIDv4 similar to Asana's GID format"""
    return str(uuid.uuid4())

def random_date_between(start_date: str, end_date: str, 
                        avoid_weekends: bool = False,
                        weight_to_start: bool = False) -> datetime:
    """
    Generate random date between two dates
    
    Args:
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD)
        avoid_weekends: If True, 85% chance to avoid weekends
        weight_to_start: If True, weight dates toward start (for creation dates)
    """
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    
    if weight_to_start:
        # Use exponential distribution weighted toward start
        days_diff = (end - start).days
        random_days = int(np.random.exponential(days_diff / 3))
        random_days = min(random_days, days_diff)
    else:
        random_days = random.randint(0, (end - start).days)
    
    result_date = start + timedelta(days=random_days)
    
    # Avoid weekends 85% of the time
    if avoid_weekends and random.random() < 0.85:
        while result_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            result_date += timedelta(days=1)
            if result_date > end:
                result_date = start + timedelta(days=random.randint(0, (end - start).days))
    
    return result_date

def random_datetime_between(start_date: str, end_date: str,
                           business_hours: bool = True) -> datetime:
    """
    Generate random datetime (with time component)
    
    Args:
        business_hours: If True, weight toward 9am-6pm on weekdays
    """
    date = random_date_between(start_date, end_date)
    
    if business_hours and random.random() < 0.8:
        # Business hours: 9am-6pm
        hour = random.randint(9, 18)
        minute = random.randint(0, 59)
    else:
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
    
    return date.replace(hour=hour, minute=minute, second=random.randint(0, 59))

def weighted_choice(choices: List, weights: List):
    """Select item from choices based on weights"""
    return random.choices(choices, weights=weights, k=1)[0]

def generate_due_date(created_at: datetime, task_type: str = 'general') -> Optional[datetime]:
    """
    Generate realistic due date based on task type and creation date
    
    Distribution (based on Asana research):
    - 25% within 1 week
    - 40% within 1 month
    - 20% 1-3 months out
    - 10% no due date
    - 5% overdue
    """
    # 10% have no due date
    if random.random() < 0.10:
        return None
    
    now = datetime.now()
    
    # Determine timeframe
    rand = random.random()
    if rand < 0.25:  # Within 1 week
        days = random.randint(1, 7)
    elif rand < 0.65:  # Within 1 month
        days = random.randint(8, 30)
    elif rand < 0.85:  # 1-3 months
        days = random.randint(31, 90)
    else:  # Overdue (5%)
        days = -random.randint(1, 30)
    
    due = created_at + timedelta(days=days)
    
    # Avoid weekends 85% of the time
    if random.random() < 0.85:
        while due.weekday() >= 5:
            due += timedelta(days=1)
    
    return due

def call_llm_api(prompt: str, temperature: float = 0.8) -> str:
    """
    Call Anthropic API to generate content
    
    Note: This is a placeholder. In production:
    1. Set ANTHROPIC_API_KEY environment variable
    2. Install anthropic package: pip install anthropic
    """
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        # Fallback to deterministic generation if no API key
        return generate_fallback_content(prompt)
    
    try:
        # Using requests to call API directly
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json',
            },
            json={
                'model': 'claude-sonnet-4-20250514',
                'max_tokens': 500,
                'temperature': temperature,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['content'][0]['text'].strip()
        else:
            return generate_fallback_content(prompt)
            
    except Exception as e:
        print(f"LLM API error: {e}, using fallback")
        return generate_fallback_content(prompt)

def generate_fallback_content(prompt: str) -> str:
    """Generate content without LLM (deterministic fallback)"""
    # This is a simple fallback - in practice you'd have template-based generation
    if 'task name' in prompt.lower():
        return random.choice([
            'Implement feature',
            'Fix bug in module',
            'Review pull request',
            'Update documentation',
            'Design new component'
        ])
    elif 'description' in prompt.lower():
        return "Task description with relevant details and context."
    elif 'comment' in prompt.lower():
        return "Status update on this task."
    return "Generated content"

def calculate_completion_status(created_at: datetime, 
                                project_type: str,
                                now: datetime) -> tuple:
    """
    Determine if task should be completed and when
    
    Completion rates by project type:
    - Sprint projects: 70-85%
    - Bug tracking: 60-70%  
    - Ongoing projects: 40-50%
    
    Returns: (is_completed: bool, completed_at: datetime or None)
    """
    completion_rates = {
        'sprint': (0.70, 0.85),
        'ongoing': (0.40, 0.50),
        'campaign': (0.65, 0.75),
        'operations': (0.55, 0.65)
    }
    
    rate_range = completion_rates.get(project_type, (0.50, 0.60))
    completion_rate = random.uniform(*rate_range)
    
    # Older tasks more likely to be completed
    days_old = (now - created_at).days
    age_factor = min(days_old / 90, 1.0)  # Cap at 90 days
    adjusted_rate = completion_rate + (age_factor * 0.2)
    
    is_completed = random.random() < adjusted_rate
    
    if not is_completed:
        return False, None
    
    # Generate completion timestamp (log-normal distribution, 1-14 days after creation)
    days_to_complete = int(np.random.lognormal(1.5, 0.8))  # Mean ~6 days
    days_to_complete = max(1, min(days_to_complete, 14))
    
    completed_at = created_at + timedelta(days=days_to_complete)
    
    if completed_at > now:
        # Set to a random time between created_at and now, ensuring constraint is met
        time_range = (now - created_at).days
        if time_range <= 0:
            completed_at = created_at
        else:
            days_between = random.randint(1, max(1, time_range))
            completed_at = created_at + timedelta(days=days_between)
    
    return True, completed_at

def load_json_data(filename: str) -> dict:
    """Load data from JSON file in data/ directory"""
    try:
        with open(f'data/{filename}', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def batch_insert(conn, table: str, columns: List[str], data: List[tuple]):
    """Efficiently insert multiple rows"""
    placeholders = ','.join(['?' for _ in columns])
    query = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
    conn.executemany(query, data)
    conn.commit()