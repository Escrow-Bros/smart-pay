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
            
            # Migration: Add verification_summary column if it doesn't exist
            try:
                conn.execute("ALTER TABLE jobs ADD COLUMN verification_summary TEXT")
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
            
            # Create disputes table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS disputes (
                    dispute_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dispute_status ON disputes(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dispute_job ON disputes(job_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dispute_raised_by ON disputes(raised_by)")
    
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
        """Get worker's currently active jobs (LOCKED, PAYMENT_PENDING, or DISPUTED status)"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM jobs 
                WHERE worker_address = ? AND status IN ('LOCKED', 'PAYMENT_PENDING', 'DISPUTED')
                ORDER BY assigned_at DESC
            """, (worker_address,))
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    def get_all_worker_jobs(self, worker_address: str) -> List[Dict]:
        """Get all jobs assigned to a worker (any status except null worker)"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM jobs 
                WHERE worker_address = ?
                ORDER BY assigned_at DESC
            """, (worker_address,))
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def get_jobs_by_status(self, status: str) -> List[Dict]:
        """Get all jobs with a specific status (for recovery/monitoring)"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM jobs 
                WHERE status = ?
                ORDER BY created_at DESC
            """, (status,))
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
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
    
    def set_payment_pending(
        self,
        job_id: int,
        verification_result: Dict,
        tx_hash: str
    ) -> Dict:
        """Mark job as payment pending (transaction broadcast but not confirmed)"""
        # Use helper to build verification_summary with proper logging
        if not isinstance(verification_result, dict):
            print(f"⚠️  WARNING: Job #{job_id} - verification_result is not a dict, defaulting to unverified")
            verification_result = {}
        
        # Log warnings if expected keys are missing
        if verification_result.get("verified") is None:
            print(f"⚠️  WARNING: Job #{job_id} - 'verified' key missing from verification_result, defaulting to False")
        if not verification_result.get("verdict"):
            print(f"⚠️  WARNING: Job #{job_id} - 'verdict' key missing from verification_result, using fallback message")
        
        verification_summary = self._build_verification_summary(verification_result)
        
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE jobs 
                SET status = 'PAYMENT_PENDING',
                    verification_result = ?,
                    verification_summary = ?,
                    tx_hash = ?
                WHERE job_id = ?
            """, (json.dumps(verification_result), json.dumps(verification_summary), tx_hash, job_id))
        
        return self.get_job(job_id)
    
    def complete_job(
        self,
        job_id: int,
        verification_result: Dict | None = None,
        tx_hash: str | None = None
    ) -> Dict:
        """Mark job as completed after payment confirmation on blockchain"""
        with self.get_connection() as conn:
            # Build UPDATE query dynamically based on provided fields
            updates = ["status = 'COMPLETED'", "completed_at = CURRENT_TIMESTAMP"]
            params = []
            
            if verification_result is not None:
                updates.append("verification_result = ?")
                params.append(json.dumps(verification_result))
            
            if tx_hash is not None:
                updates.append("tx_hash = ?")
                params.append(tx_hash)
            
            params.append(job_id)
            
            conn.execute(f"""
                UPDATE jobs 
                SET {', '.join(updates)}
                WHERE job_id = ?
            """, tuple(params))
        
        return self.get_job(job_id)
    
    def dispute_job(self, job_id: int, reason: str) -> Dict:
        """Mark job as disputed"""
        verification_result = {"disputed": True, "reason": reason, "verified": False}
        verification_summary = self._build_verification_summary(verification_result, reason)
        
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE jobs 
                SET status = 'DISPUTED',
                    verification_result = ?,
                    verification_summary = ?
                WHERE job_id = ?
            """, (json.dumps(verification_result), json.dumps(verification_summary), job_id))
        
        return self.get_job(job_id)
    
    def _build_verification_summary(self, verification_result: Optional[Dict], fallback_reason: Optional[str] = None) -> Dict:
        """
        Helper to build verification_summary safely from verification_result.
        Ensures consistent handling across set_payment_pending, dispute_job, and create_dispute.
        """
        # Defensive: Handle None or non-dict verification_result
        if not isinstance(verification_result, dict):
            print(f"⚠️  WARNING: verification_result is not a dict, defaulting to unverified")
            verification_result = {}
        
        # Extract verification summary with safe defaults (unverified by default)
        verified = verification_result.get("verified")
        verdict = verification_result.get("verdict") or verification_result.get("reason")
        
        # Use fallback_reason if verdict is missing
        if not verdict and fallback_reason:
            verdict = fallback_reason
        
        return {
            "verified": verified if verified is not None else False,
            "verdict": verdict if verdict else "Verification result unavailable"
        }
    
    # ==================== DISPUTES ====================
    
    def create_dispute(
        self,
        job_id: int,
        raised_by: str,
        reason: str,
        ai_verdict: Optional[Dict] = None,
        evidence_photos: Optional[List[str]] = None
    ) -> Dict:
        """Create a new dispute record"""
        dispute_id = None
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO disputes (
                    job_id, raised_by, reason, 
                    ai_verdict, evidence_photos, status
                ) VALUES (?, ?, ?, ?, ?, 'PENDING')
            """, (
                job_id,
                raised_by,
                reason,
                json.dumps(ai_verdict) if ai_verdict else None,
                json.dumps(evidence_photos) if evidence_photos else None
            ))
            
            dispute_id = cursor.lastrowid
            
            # Also update job status to DISPUTED if not already
            verification_result = {"disputed": True, "reason": reason, "verified": False}
            verification_summary = self._build_verification_summary(verification_result, reason)
            
            conn.execute("""
                UPDATE jobs 
                SET status = 'DISPUTED',
                    verification_result = ?,
                    verification_summary = ?
                WHERE job_id = ? AND status != 'DISPUTED'
            """, (json.dumps(verification_result), json.dumps(verification_summary), job_id))
            
            # Commit happens automatically at end of with block
        
        # Fetch the committed dispute from a fresh connection
        return self.get_dispute(dispute_id)
    
    def get_dispute(self, dispute_id: int) -> Optional[Dict]:
        """Get dispute by ID with job details"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT d.*, 
                       j.description, j.client_address, j.worker_address,
                       j.reference_photos, j.proof_photos, j.amount, j.location,
                       j.status as job_status, j.verification_result
                FROM disputes d
                JOIN jobs j ON d.job_id = j.job_id
                WHERE d.dispute_id = ?
            """, (dispute_id,))
            row = cursor.fetchone()
            
            if row:
                dispute = dict(row)
                # Parse JSON fields
                if dispute.get('ai_verdict'):
                    dispute['ai_verdict'] = json.loads(dispute['ai_verdict'])
                if dispute.get('evidence_photos'):
                    dispute['evidence_photos'] = json.loads(dispute['evidence_photos'])
                if dispute.get('reference_photos'):
                    dispute['reference_photos'] = json.loads(dispute['reference_photos'])
                if dispute.get('proof_photos'):
                    dispute['proof_photos'] = json.loads(dispute['proof_photos'])
                if dispute.get('verification_result'):
                    dispute['verification_result'] = json.loads(dispute['verification_result'])
                return dispute
            return None
    
    def get_dispute_by_job(self, job_id: int) -> Optional[Dict]:
        """Get most recent dispute for a job"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT d.*, 
                       j.description, j.client_address, j.worker_address,
                       j.reference_photos, j.proof_photos, j.amount, j.location,
                       j.status as job_status, j.verification_result
                FROM disputes d
                JOIN jobs j ON d.job_id = j.job_id
                WHERE d.job_id = ?
                ORDER BY d.raised_at DESC
                LIMIT 1
            """, (job_id,))
            row = cursor.fetchone()
            
            if row:
                dispute = dict(row)
                # Parse JSON fields
                if dispute.get('ai_verdict'):
                    dispute['ai_verdict'] = json.loads(dispute['ai_verdict'])
                if dispute.get('evidence_photos'):
                    dispute['evidence_photos'] = json.loads(dispute['evidence_photos'])
                if dispute.get('reference_photos'):
                    dispute['reference_photos'] = json.loads(dispute['reference_photos'])
                if dispute.get('proof_photos'):
                    dispute['proof_photos'] = json.loads(dispute['proof_photos'])
                if dispute.get('verification_result'):
                    dispute['verification_result'] = json.loads(dispute['verification_result'])
                return dispute
            return None
    
    def get_all_disputes(self, status: Optional[str] = None) -> List[Dict]:
        """Get all disputes, optionally filtered by status"""
        with self.get_connection() as conn:
            if status:
                cursor = conn.execute("""
                    SELECT d.dispute_id, d.job_id, d.raised_by, d.raised_at, 
                           d.reason, d.status, d.resolution,
                           j.description, j.client_address, j.worker_address,
                           j.amount, j.location, j.status as job_status
                    FROM disputes d
                    JOIN jobs j ON d.job_id = j.job_id
                    WHERE d.status = ?
                    ORDER BY d.raised_at DESC
                """, (status,))
            else:
                cursor = conn.execute("""
                    SELECT d.dispute_id, d.job_id, d.raised_by, d.raised_at, 
                           d.reason, d.status, d.resolution,
                           j.description, j.client_address, j.worker_address,
                           j.amount, j.location, j.status as job_status
                    FROM disputes d
                    JOIN jobs j ON d.job_id = j.job_id
                    ORDER BY d.raised_at DESC
                """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def resolve_dispute(
        self,
        dispute_id: int,
        resolution: str,
        resolved_by: str,
        resolution_notes: str = ""
    ) -> Dict:
        """Mark dispute as resolved"""
        with self.get_connection() as conn:
            # First, fetch the job_id from the current connection before UPDATE
            cursor = conn.execute("""
                SELECT job_id FROM disputes WHERE dispute_id = ?
            """, (dispute_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Dispute {dispute_id} not found")
            
            job_id = row['job_id']
            
            # Now perform the UPDATE on disputes table
            conn.execute("""
                UPDATE disputes
                SET status = 'RESOLVED',
                    resolution = ?,
                    resolved_by = ?,
                    resolved_at = CURRENT_TIMESTAMP,
                    resolution_notes = ?
                WHERE dispute_id = ?
            """, (resolution, resolved_by, resolution_notes, dispute_id))
            
            # Update job status based on resolution using the fetched job_id
            if resolution == 'APPROVED':
                conn.execute("""
                    UPDATE jobs 
                    SET status = 'COMPLETED'
                    WHERE job_id = ?
                """, (job_id,))
            elif resolution == 'REFUNDED':
                conn.execute("""
                    UPDATE jobs 
                    SET status = 'REFUNDED'
                    WHERE job_id = ?
                """, (job_id,))
            
            # Commit happens automatically at end of with block
        
        # Reuse get_dispute to fetch updated record with proper JSON decoding
        return self.get_dispute(dispute_id)
    
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
        if data.get("verification_summary"):
            data["verification_summary"] = json.loads(data["verification_summary"])
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
