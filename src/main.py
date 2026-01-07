"""
Asana Simulation Data Generator
Main orchestration script that coordinates all data generation
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path

from generators.organizations import generate_organizations
from generators.teams import generate_teams
from generators.users import generate_users
from generators.projects import generate_projects
from generators.tasks import generate_tasks
from generators.comments import generate_comments
from generators.custom_fields import generate_custom_fields
from generators.tags import generate_tags

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    'employee_count': 7500,  # Target: 5000-10000
    'output_db': 'output/asana_simulation.sqlite',
    'schema_file': 'schema.sql',
    'start_date': '2024-07-01',  # 6 months of history
    'end_date': '2026-01-06',  # Current date
}

def initialize_database(db_path: str, schema_path: str):
    """Create database and initialize schema"""
    logger.info(f"Initializing database at {db_path}")
    
    # Create output directory if it doesn't exist
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Remove existing database
    if Path(db_path).exists():
        Path(db_path).unlink()
        logger.info("Removed existing database")
    
    # Create new database and execute schema
    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r') as f:
        schema = f.read()
    conn.executescript(schema)
    conn.commit()
    logger.info("Database schema created successfully")
    
    return conn

def main():
    """Main execution flow"""
    logger.info("=== Starting Asana Simulation Data Generation ===")
    start_time = datetime.now()
    
    # Initialize database
    conn = initialize_database(CONFIG['output_db'], CONFIG['schema_file'])
    
    try:
        # Step 1: Generate organization
        logger.info("Step 1: Generating organization...")
        org = generate_organizations(conn, CONFIG)
        logger.info(f"Created organization: {org['name']}")
        
        # Step 2: Generate teams
        logger.info("Step 2: Generating teams...")
        teams = generate_teams(conn, org, CONFIG)
        logger.info(f"Created {len(teams)} teams")
        
        # Step 3: Generate users
        logger.info("Step 3: Generating users...")
        users = generate_users(conn, org, teams, CONFIG)
        logger.info(f"Created {len(users)} users")
        
        # Step 4: Generate projects
        logger.info("Step 4: Generating projects...")
        projects = generate_projects(conn, teams, users, CONFIG)
        logger.info(f"Created {len(projects)} projects")
        
        # Step 5: Generate tasks
        logger.info("Step 5: Generating tasks...")
        tasks = generate_tasks(conn, projects, users, CONFIG)
        logger.info(f"Created {len(tasks)} tasks")
        
        # Step 6: Generate comments
        logger.info("Step 6: Generating comments...")
        comments = generate_comments(conn, tasks, users, CONFIG)
        logger.info(f"Created {len(comments)} comments")
        
        # Step 7: Generate custom fields
        logger.info("Step 7: Generating custom fields...")
        custom_fields = generate_custom_fields(conn, projects, tasks, CONFIG)
        logger.info(f"Created {custom_fields} custom field values")
        
        # Step 8: Generate tags
        logger.info("Step 8: Generating tags...")
        tags = generate_tags(conn, org, tasks, CONFIG)
        logger.info(f"Created {len(tags)} tags and associations")
        
        # Commit all changes
        conn.commit()
        logger.info("All data committed to database")
        
        # Generate statistics
        cursor = conn.cursor()
        stats = {
            'organizations': cursor.execute("SELECT COUNT(*) FROM organizations").fetchone()[0],
            'teams': cursor.execute("SELECT COUNT(*) FROM teams").fetchone()[0],
            'users': cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            'projects': cursor.execute("SELECT COUNT(*) FROM projects").fetchone()[0],
            'tasks': cursor.execute("SELECT COUNT(*) FROM tasks").fetchone()[0],
            'comments': cursor.execute("SELECT COUNT(*) FROM comments").fetchone()[0],
            'tags': cursor.execute("SELECT COUNT(*) FROM tags").fetchone()[0],
        }
        
        logger.info("\n=== Generation Complete ===")
        logger.info("Database Statistics:")
        for entity, count in stats.items():
            logger.info(f"  {entity.capitalize()}: {count:,}")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"\nTotal time: {elapsed:.2f} seconds")
        logger.info(f"Output: {CONFIG['output_db']}")
        
    except Exception as e:
        logger.error(f"Error during generation: {e}", exc_info=True)
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()