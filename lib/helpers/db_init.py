import os
import sys
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lib.models import init_db, get_db_session, County, Budget


def initialize_database():
    try:
        init_db()
        print("✓ Database tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Error creating database tables: {e}")
        return False


def seed_sample_data():
    try:
        session = get_db_session()
        

        existing_counties = session.query(County).count()
        if existing_counties > 0:
            print("✓ Sample data already exists")
            session.close()
            return True
        

        sample_counties = [
            {
                'name': 'Nairobi',
                'population': 4397073,
                'economic_output': 2500000000.0,
                'project_score': 9
            },
            {
                'name': 'Mombasa',
                'population': 1208333,
                'economic_output': 800000000.0,
                'project_score': 8
            },
            {
                'name': 'Kiambu',
                'population': 2417735,
                'economic_output': 600000000.0,
                'project_score': 7
            },
            {
                'name': 'Nakuru',
                'population': 2162202,
                'economic_output': 450000000.0,
                'project_score': 6
            },
            {
                'name': 'Machakos',
                'population': 1421932,
                'economic_output': 300000000.0,
                'project_score': 5
            },
            {
                'name': 'Kajiado',
                'population': 1117840,
                'economic_output': 200000000.0,
                'project_score': 6
            }
        ]
        
        for county_data in sample_counties:
            county = County(
                name=county_data['name'],
                population=county_data['population'],
                economic_output=county_data['economic_output'],
                project_score=county_data['project_score']
            )
            session.add(county)
        
        session.commit()
        print(f"✓ Successfully seeded {len(sample_counties)} sample counties")
        session.close()
        return True
        
    except Exception as e:
        print(f"✗ Error seeding sample data: {e}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return False


def reset_database():
    """Reset the database by dropping and recreating all tables"""
    try:
        from lib.models import Base, engine
        
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        print("✓ Dropped existing tables")
        
        # Recreate tables
        Base.metadata.create_all(bind=engine)
        print("✓ Recreated database tables")
        
        return True
    except Exception as e:
        print(f"✗ Error resetting database: {e}")
        return False


def check_database_status():
    """Check if database is properly initialized"""
    try:
        session = get_db_session()
        
        # Check if tables exist by trying to query them
        county_count = session.query(County).count()
        budget_count = session.query(Budget).count()
        
        print(f"✓ Database status:")
        print(f"  - Counties: {county_count}")
        print(f"  - Budgets: {budget_count}")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"✗ Database check failed: {e}")
        return False


if __name__ == "__main__":
    print("Initializing Budget Allocation Database...")
    
    if initialize_database():
        if seed_sample_data():
            check_database_status()
            print("\n✓ Database initialization completed successfully!")
        else:
            print("\n✗ Database initialization completed with errors")
    else:
        print("\n✗ Database initialization failed")
