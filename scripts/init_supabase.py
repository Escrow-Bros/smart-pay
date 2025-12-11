#!/usr/bin/env python3
"""
Initialize Supabase database tables.
Run this script once to create all required tables.

Usage:
    python scripts/init_supabase.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from backend.database import Database


def init_database():
    """Initialize all database tables"""
    
    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("\nPlease set your Supabase connection string in .env file:")
        print("DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres")
        return False
    
    print("🔄 Initializing Supabase database...")
    print(f"📍 Connecting to: {os.getenv('DATABASE_URL')[:50]}...")
    
    try:
        # Create database instance - this will create all tables
        db = Database()
        
        print("\n✅ Database initialized successfully!")
        print("\n📋 Created tables:")
        print("   • jobs - Stores all job postings and their status")
        print("   • disputes - Stores dispute records for AI-rejected work")
        
        # Test connection by querying
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM jobs")
            job_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM disputes")
            dispute_count = cursor.fetchone()[0]
            
        print(f"\n📊 Current data:")
        print(f"   Jobs: {job_count}")
        print(f"   Disputes: {dispute_count}")
        
        print("\n✅ Your Supabase database is ready to use!")
        print("\n🚀 Next steps:")
        print("   1. Start your backend: cd backend && python api.py")
        print("   2. Test job creation through the web interface")
        print("   3. Deploy to Render with DATABASE_URL environment variable")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 Common issues:")
        print("   • Check your DATABASE_URL is correct")
        print("   • Verify password is URL-encoded (@ = %40, etc.)")
        print("   • Ensure Supabase project is active")
        print("   • Check network connection to Supabase")
        
        return False


if __name__ == "__main__":
    print("="*60)
    print("  GigSmartPay - Supabase Database Initialization")
    print("="*60)
    
    success = init_database()
    
    if not success:
        sys.exit(1)
