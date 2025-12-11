import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from contextlib import contextmanager


class Database:
    
    def __init__(self, db_path: str = "gigshield.db"):
        """Initialize database connection"""
        self.db_path = Path(__file__).parent / db_path
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_db(self):
        """Create tables if they don't exist"""
        with self.get_connection() as conn:
            # Create tables if they don't exist
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id INTEGER PRIMARY KEY,
                    client_address TEXT NOT NULL,
                    worker_address TEXT,
                    description TEXT NOT NULL,
                    location TEXT,
                    latitude REAL,
                    longitude REAL,
                    reference_photos TEXT,
                    proof_photos TEXT,
                    amount REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    assigned_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    tx_hash TEXT,
                    verification_result TEXT,
                    acceptance_criteria TEXT
                )
            """)
            
            # Migration: Add acceptance_criteria column if it doesn't exist
            try:
                conn.execute("ALTER TABLE jobs ADD COLUMN acceptance_criteria TEXT")
            except sqlite3.OperationalError:
                pass

            # Migration: Add verification_plan column if it doesn't exist
            try:
                conn.execute("ALTER TABLE jobs ADD COLUMN verification_plan TEXT")
            except sqlite3.OperationalError:
                pass
            
            # Migration: Add location columns if they don't exist
            try:
                conn.execute("ALTER TABLE jobs ADD COLUMN location TEXT")
            except sqlite3.OperationalError:
                pass
            
            try:
                conn.execute("ALTER TABLE jobs ADD COLUMN latitude REAL")
            except sqlite3.OperationalError:
                pass
            
            try:
                conn.execute("ALTER TABLE jobs ADD COLUMN longitude REAL")
            except sqlite3.OperationalError:
                pass
            
            # Create indexes for fast queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON jobs(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_client ON jobs(client_address)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_worker ON jobs(worker_address)")
    
    # ==================== CREATE ====================
    
    def create_job(
        self,
        job_id: int,
        client_address: str,
        description: str,
        reference_photos: List[str],
        amount: float,
        tx_hash: str,
        location: str = "",
        latitude: float = 0.0,
        longitude: float = 0.0,
        verification_plan: Dict = None
    ) -> Dict:
        """Insert new job into database"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO jobs (
                    job_id, client_address, description, 
                    location, latitude, longitude,
                    reference_photos, amount, status, tx_hash,
                    verification_plan
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, ?)
            """, (
                job_id,
                client_address,
                description,
                location,
                latitude,
                longitude,
                json.dumps(reference_photos),
                amount,
                tx_hash,
                json.dumps(verification_plan or {})
            ))
        
        return self.get_job(job_id)
    
    # ==================== READ ====================
    
    def get_job(self, job_id: int) -> Optional[Dict]:
        """Get single job by ID"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM jobs WHERE job_id = ?",
                (job_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return self._row_to_dict(row)
            return None
    
    def get_available_jobs(self) -> List[Dict]:
        """Get all jobs with status OPEN"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM jobs 
                WHERE status = 'OPEN' 
                ORDER BY created_at DESC
            """)
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def get_client_jobs(self, client_address: str) -> List[Dict]:
        """Get all jobs created by a client"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM jobs 
                WHERE client_address = ? 
                ORDER BY created_at DESC
            """, (client_address,))
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    
    def get_worker_completed_jobs(self, worker_address: str) -> List[Dict]:
        """Get worker's completed jobs (history)"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM jobs 
                WHERE worker_address = ? AND status = 'COMPLETED'
                ORDER BY completed_at DESC
            """, (worker_address,))
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def get_worker_active_jobs(self, worker_address: str) -> List[Dict]:
        """Get worker's currently active jobs (LOCKED or DISPUTED status)"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM jobs 
                WHERE worker_address = ? AND status IN ('LOCKED', 'DISPUTED')
                ORDER BY assigned_at DESC
            """, (worker_address,))
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    # ==================== UPDATE ====================
    
    def assign_job(self, job_id: int, worker_address: str) -> Dict:
        """Update job when worker claims it"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE jobs 
                SET worker_address = ?,
                    status = 'LOCKED',
                    assigned_at = CURRENT_TIMESTAMP
                WHERE job_id = ?
            """, (worker_address, job_id))
        
        return self.get_job(job_id)
    
    def submit_proof(
        self,
        job_id: int,
        proof_photos: List[str]
    ) -> Dict:
        """Update job with proof photos"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE jobs 
                SET proof_photos = ?
                WHERE job_id = ?
            """, (json.dumps(proof_photos), job_id))
        
        return self.get_job(job_id)
    
    def complete_job(
        self,
        job_id: int,
        verification_result: Dict,
        tx_hash: str
    ) -> Dict:
        """Mark job as completed after payment release"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE jobs 
                SET status = 'COMPLETED',
                    completed_at = CURRENT_TIMESTAMP,
                    verification_result = ?,
                    tx_hash = ?
                WHERE job_id = ?
            """, (json.dumps(verification_result), tx_hash, job_id))
        
        return self.get_job(job_id)
    
    def dispute_job(self, job_id: int, reason: str) -> Dict:
        """Mark job as disputed"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE jobs 
                SET status = 'DISPUTED',
                    verification_result = ?
                WHERE job_id = ?
            """, (json.dumps({"disputed": True, "reason": reason}), job_id))
        
        return self.get_job(job_id)
    
    # ==================== STATS ====================
    
    def get_worker_stats(self, worker_address: str) -> Dict:
        """Get worker statistics"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_jobs,
                    SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'COMPLETED' THEN amount * 0.95 ELSE 0 END) as total_earnings
                FROM jobs 
                WHERE worker_address = ?
            """, (worker_address,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "total_jobs": row["total_jobs"] or 0,
                    "completed_jobs": row["completed"] or 0,
                    "total_earnings": round(row["total_earnings"] or 0, 2)
                }
            return {
                "total_jobs": 0,
                "completed_jobs": 0,
                "total_earnings": 0
            }
    
    # ==================== HELPER ====================
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Convert SQLite row to dictionary"""
        data = dict(row)
        
        # Parse JSON fields
        if data.get("reference_photos"):
            data["reference_photos"] = json.loads(data["reference_photos"])
        if data.get("proof_photos"):
            data["proof_photos"] = json.loads(data["proof_photos"])
        if data.get("verification_result"):
            data["verification_result"] = json.loads(data["verification_result"])
        if data.get("acceptance_criteria"):
            data["acceptance_criteria"] = json.loads(data["acceptance_criteria"])
        if data.get("verification_plan"):
            data["verification_plan"] = json.loads(data["verification_plan"])
        
        return data


# Singleton instance
_db_instance = None

def get_db() -> Database:
    """Get database singleton"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
