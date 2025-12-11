import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool


class Database:
    
    def __init__(self, connection_string: str = None):
        """Initialize database connection pool"""
        self.connection_string = connection_string or os.getenv("DATABASE_URL")
        
        if not self.connection_string:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Create connection pool (min 1, max 10 connections)
        self.pool = SimpleConnectionPool(1, 10, self.connection_string)
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.pool.putconn(conn)
    
    def _init_db(self):
        """Create tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create jobs table
            cursor.execute("""
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
                    acceptance_criteria TEXT,
                    verification_plan TEXT,
                    verification_summary TEXT
                )
            """)
            
            # Create indexes for fast queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON jobs(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_client ON jobs(client_address)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_worker ON jobs(worker_address)")
            
            # Create disputes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS disputes (
                    dispute_id SERIAL PRIMARY KEY,
                    job_id INTEGER NOT NULL,
                    raised_by TEXT NOT NULL,
                    raised_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reason TEXT NOT NULL,
                    ai_verdict TEXT,
                    evidence_photos TEXT,
                    status TEXT DEFAULT 'PENDING',
                    resolved_by TEXT,
                    resolved_at TIMESTAMP,
                    resolution TEXT,
                    resolution_notes TEXT,
                    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dispute_status ON disputes(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dispute_job ON disputes(job_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dispute_raised_by ON disputes(raised_by)")
    
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
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO jobs (
                    job_id, client_address, description, 
                    location, latitude, longitude,
                    reference_photos, amount, status, tx_hash,
                    verification_plan
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'OPEN', %s, %s)
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
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM jobs WHERE job_id = %s",
                (job_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return self._row_to_dict(dict(row))
            return None
    
    def get_available_jobs(self) -> List[Dict]:
        """Get all jobs with status OPEN"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM jobs 
                WHERE status = 'OPEN' 
                ORDER BY created_at DESC
            """)
            return [self._row_to_dict(dict(row)) for row in cursor.fetchall()]
    
    def get_client_jobs(self, client_address: str) -> List[Dict]:
        """Get all jobs created by a client"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM jobs 
                WHERE client_address = %s
                ORDER BY created_at DESC
            """, (client_address,))
            return [self._row_to_dict(dict(row)) for row in cursor.fetchall()]
    
    
    def get_worker_completed_jobs(self, worker_address: str) -> List[Dict]:
        """Get worker's completed jobs (history)"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM jobs 
                WHERE worker_address = %s AND status = 'COMPLETED'
                ORDER BY completed_at DESC
            """, (worker_address,))
            return [self._row_to_dict(dict(row)) for row in cursor.fetchall()]
    
    def get_worker_assigned_job(self, worker_address: str) -> Optional[Dict]:
        """Get worker's currently assigned job (IN_PROGRESS)"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM jobs 
                WHERE worker_address = %s AND status = 'IN_PROGRESS'
                ORDER BY assigned_at DESC
                LIMIT 1
            """, (worker_address,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_dict(dict(row))
            return None
    
    def get_all_jobs(self) -> List[Dict]:
        """Get all jobs for debugging"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC")
            return [self._row_to_dict(dict(row)) for row in cursor.fetchall()]
    
    def get_disputes(self, status: str = None) -> List[Dict]:
        """Get disputes, optionally filtered by status"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            if status:
                cursor.execute("""
                    SELECT d.*, j.description as job_description 
                    FROM disputes d
                    JOIN jobs j ON d.job_id = j.job_id
                    WHERE d.status = %s
                    ORDER BY d.raised_at DESC
                """, (status,))
            else:
                cursor.execute("""
                    SELECT d.*, j.description as job_description 
                    FROM disputes d
                    JOIN jobs j ON d.job_id = j.job_id
                    ORDER BY d.raised_at DESC
                """)
            
            results = []
            for row in cursor.fetchall():
                row_dict = dict(row)
                # Parse JSON fields
                if row_dict.get('evidence_photos'):
                    try:
                        row_dict['evidence_photos'] = json.loads(row_dict['evidence_photos'])
                    except:
                        pass
                if row_dict.get('ai_verdict'):
                    try:
                        row_dict['ai_verdict'] = json.loads(row_dict['ai_verdict'])
                    except:
                        pass
                results.append(row_dict)
            
            return results
    
    # ==================== UPDATE ====================
    
    def assign_job(self, job_id: int, worker_address: str) -> Dict:
        """Assign job to worker"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE jobs 
                SET worker_address = %s, status = 'IN_PROGRESS', assigned_at = CURRENT_TIMESTAMP
                WHERE job_id = %s AND status = 'OPEN'
            """, (worker_address, job_id))
            
            if cursor.rowcount == 0:
                raise ValueError("Job not found or already assigned")
        
        return self.get_job(job_id)
    
    def submit_proof(self, job_id: int, proof_photos: List[str]) -> Dict:
        """Worker submits proof of completion"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE jobs 
                SET proof_photos = %s, status = 'SUBMITTED'
                WHERE job_id = %s AND status = 'IN_PROGRESS'
            """, (json.dumps(proof_photos), job_id))
            
            if cursor.rowcount == 0:
                raise ValueError("Job not found or not in progress")
        
        return self.get_job(job_id)
    
    def approve_job(self, job_id: int, verification_result: str = None) -> Dict:
        """Approve job completion (AI or client)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE jobs 
                SET status = 'COMPLETED', 
                    completed_at = CURRENT_TIMESTAMP,
                    verification_result = %s
                WHERE job_id = %s AND status IN ('SUBMITTED', 'IN_PROGRESS')
            """, (verification_result, job_id))
            
            if cursor.rowcount == 0:
                raise ValueError("Job not found or not in correct state")
        
        return self.get_job(job_id)
    
    def dispute_job(self, job_id: int, reason: str, ai_verdict: Dict = None, raised_by: str = "system") -> Dict:
        """Move job to disputed state and create dispute record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Update job status
            cursor.execute("""
                UPDATE jobs 
                SET status = 'DISPUTED'
                WHERE job_id = %s
            """, (job_id,))
            
            if cursor.rowcount == 0:
                raise ValueError("Job not found")
            
            # Get job details for evidence
            job = self.get_job(job_id)
            evidence_photos = job.get('proof_photos', [])
            
            # Create dispute record
            cursor.execute("""
                INSERT INTO disputes (job_id, raised_by, reason, ai_verdict, evidence_photos, status)
                VALUES (%s, %s, %s, %s, %s, 'PENDING')
            """, (
                job_id,
                raised_by,
                reason,
                json.dumps(ai_verdict) if ai_verdict else None,
                json.dumps(evidence_photos) if evidence_photos else None
            ))
        
        return self.get_job(job_id)
    
    def resolve_dispute(
        self, 
        dispute_id: int, 
        resolution: str,
        resolved_by: str,
        resolution_notes: str = None
    ) -> Dict:
        """Resolve a dispute"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE disputes 
                SET status = 'RESOLVED',
                    resolution = %s,
                    resolved_by = %s,
                    resolved_at = CURRENT_TIMESTAMP,
                    resolution_notes = %s
                WHERE dispute_id = %s
            """, (resolution, resolved_by, resolution_notes, dispute_id))
            
            if cursor.rowcount == 0:
                raise ValueError("Dispute not found")
            
            # Get the dispute to find job_id
            cursor.execute("SELECT job_id FROM disputes WHERE dispute_id = %s", (dispute_id,))
            row = cursor.fetchone()
            
            if row:
                job_id = row[0]
                # Update job status based on resolution
                if resolution == 'APPROVED':
                    cursor.execute("""
                        UPDATE jobs SET status = 'COMPLETED', completed_at = CURRENT_TIMESTAMP
                        WHERE job_id = %s
                    """, (job_id,))
                elif resolution == 'REJECTED':
                    cursor.execute("""
                        UPDATE jobs SET status = 'OPEN', worker_address = NULL, proof_photos = NULL
                        WHERE job_id = %s
                    """, (job_id,))
        
        # Return updated dispute
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM disputes WHERE dispute_id = %s", (dispute_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def save_verification_result(self, job_id: int, verification_summary: Dict) -> Dict:
        """Save AI verification result"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE jobs 
                SET verification_summary = %s
                WHERE job_id = %s
            """, (json.dumps(verification_summary), job_id))
        
        return self.get_job(job_id)
    
    # ==================== DELETE ====================
    
    def delete_job(self, job_id: int) -> bool:
        """Delete a job (use with caution)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))
            return cursor.rowcount > 0
    
    # ==================== HELPER METHODS ====================
    
    def _row_to_dict(self, row: Dict) -> Dict:
        """Convert database row to dictionary with parsed JSON fields"""
        result = dict(row)
        
        # Parse JSON fields
        json_fields = ['reference_photos', 'proof_photos', 'verification_plan', 'verification_summary']
        for field in json_fields:
            if field in result and result[field]:
                try:
                    result[field] = json.loads(result[field])
                except (json.JSONDecodeError, TypeError):
                    pass
        
        # Convert datetime objects to ISO format strings
        datetime_fields = ['created_at', 'assigned_at', 'completed_at']
        for field in datetime_fields:
            if field in result and result[field]:
                if isinstance(result[field], datetime):
                    result[field] = result[field].isoformat()
        
        return result
    
    def close(self):
        """Close all connections in the pool"""
        if hasattr(self, 'pool'):
            self.pool.closeall()
