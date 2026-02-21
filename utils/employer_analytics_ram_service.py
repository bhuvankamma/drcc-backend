from sqlalchemy.orm import Session
from sqlalchemy import text


# Line Chart - Job postings per month
def get_job_postings_per_month(db: Session):

    query = text("""
        SELECT 
            TO_CHAR(created_at, 'Mon') AS month,
            COUNT(*) AS total_jobs,
            DATE_TRUNC('month', created_at) AS month_date
        FROM jobs11
        WHERE status = 'active' 
        GROUP BY month, month_date
        ORDER BY month_date
    """)

    result = db.execute(query).fetchall()

    return [
        {
            "month": row.month,
            "total_openings": row.total_jobs
        }
        for row in result
    ]


# Bar Chart - Recruiter activity
def get_recruiter_activity(db: Session):

    query = text("""
        SELECT 
            posted_by,
            COUNT(*) AS jobs_posted
        FROM jobs11
        WHERE status = 'active'
        GROUP BY posted_by
        ORDER BY jobs_posted DESC
    """)

    result = db.execute(query).fetchall()

    return [
        {
            "recruiter_id": row.posted_by,
            "jobs_posted": row.jobs_posted
        }
        for row in result
    ]


# Pie Chart - Industry distribution
# COMMENTED because not present in UI
# Remove comments if needed later

"""
def get_industry_distribution(db: Session):

    query = text('''
        SELECT 
            industry,
            COUNT(*) AS total_jobs
        FROM jobs11
        WHERE industry IS NOT NULL
        GROUP BY industry
        ORDER BY total_jobs DESC
    ''')

    result = db.execute(query).fetchall()

    return [
        {
            "industry": row.industry,
            "count": row.total_jobs
        }
        for row in result
    ]
"""