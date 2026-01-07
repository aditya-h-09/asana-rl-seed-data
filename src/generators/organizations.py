"""
Organization/Workspace Generator
Creates the top-level organization for the simulation
"""

import random
from datetime import datetime, timedelta
from utils import generate_uuid, random_datetime_between

# Realistic B2B SaaS company names (sourced from YC, Crunchbase patterns)
COMPANY_NAMES = [
    "DataStream", "CloudSync", "MetricsHub", "FlowBase", "VectorAI",
    "PulseWorks", "NexusCloud", "SignalPath", "OptiScale", "CoreStack",
    "FusionData", "ApexFlow", "ZenithOps", "CatalystHQ", "VelocityIO",
    "QuantumLeap", "PrismData", "HorizonTech", "EchoStream", "NimbusLabs"
]

COMPANY_DOMAINS = [
    "datastream.com", "cloudsync.io", "metricshub.com", "flowbase.io",
    "vectorai.com", "pulseworks.io", "nexuscloud.com", "signalpath.io",
    "optiscale.com", "corestack.io", "fusiondata.com", "apexflow.io",
    "zenithops.com", "catalysthq.com", "velocity.io", "quantumleap.io",
    "prismdata.com", "horizontech.io", "echostream.io", "nimbuslabs.com"
]

def generate_organizations(conn, config: dict) -> dict:
    """
    Generate a single organization (B2B SaaS company)
    
    Args:
        conn: Database connection
        config: Configuration dict with employee_count
    
    Returns:
        dict with org details
    """
    # Select random company
    idx = random.randint(0, len(COMPANY_NAMES) - 1)
    name = COMPANY_NAMES[idx]
    domain = COMPANY_DOMAINS[idx]
    
    # Employee count from config (5000-10000 range)
    employee_count = config['employee_count']
    
    # Organization created 2-4 years ago (established company)
    years_ago = random.randint(2, 4)
    created_at = datetime.now() - timedelta(days=years_ago * 365)
    
    org_id = generate_uuid()
    
    org = {
        'org_id': org_id,
        'name': name,
        'domain': domain,
        'created_at': created_at.isoformat(),
        'employee_count': employee_count
    }
    
    # Insert into database
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO organizations (org_id, name, domain, created_at, employee_count)
        VALUES (?, ?, ?, ?, ?)
    """, (org_id, name, domain, created_at, employee_count))
    
    conn.commit()
    
    return org