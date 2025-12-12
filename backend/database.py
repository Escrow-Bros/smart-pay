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
        # psycopg2 will handle connection to Supabase
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
        """Get all worker's jobs (all statuses for history view)"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM jobs 
                WHERE worker_address = %s 
                ORDER BY COALESCE(completed_at, updated_at, created_at) DESC
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
    
    def get_jobs_by_status(self, status: str) -> List[Dict]:
        """Get all jobs with specific status"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM jobs 
                WHERE status = %s 
                ORDER BY created_at DESC
            """, (status,))
            return [self._row_to_dict(dict(row)) for row in cursor.fetchall()]
    
    def get_worker_active_jobs(self, worker_address: str) -> List[Dict]:
        """Get worker's active jobs (IN_PROGRESS + SUBMITTED + DISPUTED + PAYMENT_PENDING)"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM jobs 
                WHERE worker_address = %s 
                AND status IN ('IN_PROGRESS', 'SUBMITTED', 'DISPUTED', 'PAYMENT_PENDING')
                ORDER BY assigned_at DESC
            """, (worker_address,))
            return [self._row_to_dict(dict(row)) for row in cursor.fetchall()]
    
    def get_all_worker_jobs(self, worker_address: str) -> List[Dict]:
        """Get all jobs for a worker (any status)"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM jobs 
                WHERE worker_address = %s
                ORDER BY assigned_at DESC
            """, (worker_address,))
            return [self._row_to_dict(dict(row)) for row in cursor.fetchall()]
    
    def get_worker_stats(self, worker_address: str) -> Dict:
        """Get worker statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_jobs,
                    COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed_jobs,
                    COALESCE(SUM(CASE WHEN status = 'COMPLETED' THEN amount ELSE 0 END), 0) as total_earnings
                FROM jobs 
                WHERE worker_address = %s
            """, (worker_address,))
            row = cursor.fetchone()
            return dict(row) if row else {"total_jobs": 0, "completed_jobs": 0, "total_earnings": 0}
    
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
    
    def get_all_disputes(self, status: str = None) -> List[Dict]:
        """Get all disputes, optionally filtered by status (alias for get_disputes)"""
        return self.get_disputes(status)
    
    def get_dispute(self, dispute_id: int) -> Optional[Dict]:
        """Get single dispute by ID with complete job details"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT 
                    d.*,
                    j.description as job_description,
                    j.reference_photos,
                    j.proof_photos,
                    j.client_address,
                    j.worker_address,
                    j.amount
                FROM disputes d
                JOIN jobs j ON d.job_id = j.job_id
                WHERE d.dispute_id = %s
            """, (dispute_id,))
            row = cursor.fetchone()
            
            if row:
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
                if row_dict.get('reference_photos'):
                    try:
                        row_dict['reference_photos'] = json.loads(row_dict['reference_photos'])
                    except:
                        pass
                if row_dict.get('proof_photos'):
                    try:
                        row_dict['proof_photos'] = json.loads(row_dict['proof_photos'])
                    except:
                        pass
                return row_dict
            return None
    
    def get_dispute_by_job(self, job_id: int) -> Optional[Dict]:
        """Get dispute by job ID with complete job details"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT 
                    d.*,
                    j.description as job_description,
                    j.reference_photos,
                    j.proof_photos,
                    j.client_address,
                    j.worker_address,
                    j.amount
                FROM disputes d
                JOIN jobs j ON d.job_id = j.job_id
                WHERE d.job_id = %s
                ORDER BY d.raised_at DESC
                LIMIT 1
            """, (job_id,))
            row = cursor.fetchone()
            
            if row:
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
                if row_dict.get('reference_photos'):
                    try:
                        row_dict['reference_photos'] = json.loads(row_dict['reference_photos'])
                    except:
                        pass
                if row_dict.get('proof_photos'):
                    try:
                        row_dict['proof_photos'] = json.loads(row_dict['proof_photos'])
                    except:
                        pass
                return row_dict
            return None
    
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
        """Worker submits proof of completion (allows resubmission for disputed jobs)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE jobs 
                SET proof_photos = %s, status = 'SUBMITTED'
                WHERE job_id = %s AND status IN ('IN_PROGRESS', 'DISPUTED')
            """, (json.dumps(proof_photos), job_id))
            
            if cursor.rowcount == 0:
                raise ValueError("Job not found or not in progress/disputed")
        
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
    
    def set_payment_pending(self, job_id: int, verification_result: Dict = None, tx_hash: str = None) -> Dict:
        """Mark job as PAYMENT_PENDING after payment TX is broadcast (awaiting blockchain confirmation)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE jobs 
                SET status = 'PAYMENT_PENDING', 
                    verification_summary = %s,
                    tx_hash = COALESCE(%s, tx_hash)
                WHERE job_id = %s
            """, (json.dumps(verification_result) if verification_result else None, tx_hash, job_id))
            
            if cursor.rowcount == 0:
                raise ValueError("Job not found")
        
        return self.get_job(job_id)
    
    def complete_job(self, job_id: int, tx_hash: str = None) -> Dict:
        """Mark job as COMPLETED after blockchain confirmation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE jobs 
                SET status = 'COMPLETED', 
                    completed_at = CURRENT_TIMESTAMP,
                    tx_hash = COALESCE(%s, tx_hash)
                WHERE job_id = %s
            """, (tx_hash, job_id))
            
            if cursor.rowcount == 0:
                raise ValueError("Job not found")
        
        return self.get_job(job_id)
    
    def dispute_job(self, job_id: int, reason: str, ai_verdict: Dict = None, raised_by: str = "system") -> Dict:
        """Move job to disputed state and create/update dispute record"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Check if there's already an existing PENDING dispute for this job
            cursor.execute("""
                SELECT dispute_id FROM disputes 
                WHERE job_id = %s AND status = 'PENDING'
                ORDER BY raised_at DESC
                LIMIT 1
            """, (job_id,))
            existing_dispute = cursor.fetchone()
            
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
            
            if existing_dispute:
                # Update existing dispute instead of creating duplicate
                print(f"📝 Updating existing dispute #{existing_dispute['dispute_id']} for job #{job_id}")
                cursor.execute("""
                    UPDATE disputes 
                    SET reason = %s,
                        ai_verdict = %s,
                        evidence_photos = %s,
                        raised_at = CURRENT_TIMESTAMP
                    WHERE dispute_id = %s
                """, (
                    reason,
                    json.dumps(ai_verdict) if ai_verdict else None,
                    json.dumps(evidence_photos) if evidence_photos else None,
                    existing_dispute['dispute_id']
                ))
            else:
                # Create new dispute record
                print(f"🆕 Creating new dispute for job #{job_id}")
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
    
    def dismiss_dispute(self, dispute_id: int, dismissed_by: str, reason: str = None) -> Dict:
        """Dismiss a dispute (technical issue, not worker's fault) and allow worker to retry"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get dispute details
            cursor.execute("SELECT job_id FROM disputes WHERE dispute_id = %s", (dispute_id,))
            dispute = cursor.fetchone()
            if not dispute:
                raise ValueError("Dispute not found")
            
            job_id = dispute['job_id']
            
            # Mark dispute as dismissed
            cursor.execute("""
                UPDATE disputes 
                SET status = 'RESOLVED',
                    resolution = 'DISMISSED',
                    resolved_by = %s,
                    resolved_at = CURRENT_TIMESTAMP,
                    resolution_notes = %s
                WHERE dispute_id = %s
            """, (dismissed_by, reason or "Technical issue - not worker's fault", dispute_id))
            
            # Reset job back to IN_PROGRESS so worker can resubmit
            cursor.execute("""
                UPDATE jobs 
                SET status = 'IN_PROGRESS'
                WHERE job_id = %s
            """, (job_id,))
            
            print(f"✅ Dispute #{dispute_id} dismissed. Job #{job_id} reset to IN_PROGRESS.")
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
                elif resolution == 'REFUNDED':
                    cursor.execute("""
                        UPDATE jobs SET status = 'REFUNDED'
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
