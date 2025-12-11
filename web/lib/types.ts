export interface VerificationPlan {
    task_category: string;
    success_criteria: string[];
    rejection_criteria: string[];
    visual_checks: string[];
    location_required: boolean;
    comparison_mode: 'before_after' | 'reference_match' | 'checklist';
}

export interface JobDict {
    job_id: number;
    client_address: string;
    worker_address?: string | null;
    description: string;
    location: string;
    latitude: number;
    longitude: number;
    reference_photos: string[];
    proof_photos: string[];
    amount: number;
    status: string;
    created_at: string;
    updated_at: string;
    assigned_at?: string | null;
    completed_at?: string | null;
    tx_hash?: string | null;
    verification_result?: Record<string, unknown> | null;
    verification_summary?: {
        verified: boolean;
        verdict: string;
        score?: number;
        comparison?: {
            same_location: boolean;
            same_object: boolean;
            transformation_occurred: boolean;
            location_confidence: number;
            visual_changes?: string[];
        };
        gps_verification?: {
            location_match: boolean;
            distance_meters?: number;
            confidence: number;
            reasoning: string;
        };
    } | null;
    verification_plan?: VerificationPlan | null;
}

export interface WorkerStats {
    total_jobs: number;
    completed_jobs: number;
    total_earned: number;
}

export type UserMode = 'client' | 'worker';

export interface UploadedImage {
    file: File;
    preview: string;
}

export interface DisputeDict {
    dispute_id: number;
    job_id: number;
    raised_by: string;
    raised_at: string;
    reason: string;
    ai_verdict?: Record<string, any> | null;
    confidence_score?: number | null;
    evidence_photos?: string[];
    status: 'PENDING' | 'UNDER_REVIEW' | 'RESOLVED';
    resolved_by?: string | null;
    resolved_at?: string | null;
    resolution?: 'APPROVED' | 'REFUNDED' | null;
    resolution_notes?: string | null;
    transaction_hash?: string | null;
    // Job details (joined)
    description?: string;
    client_address?: string;
    worker_address?: string;
    amount?: number;
    location?: string;
    job_status?: string;
    reference_photos?: string[];
    proof_photos?: string[];
    verification_result?: Record<string, any>;
}

export interface GlobalState {
    userMode: UserMode | null;
    currentUser: string | null;
    walletAddress: string;
    walletBalance: number;
    isLoadingBalance: boolean;
    availableJobs: JobDict[];
    clientJobs: JobDict[];
    workerJobs: JobDict[];
    currentJobs: JobDict[];
    workerStats: WorkerStats;
    isLoadingJobs: boolean;
    jobDescription: string;
    jobLocation: string;
    jobLatitude: number;
    jobLongitude: number;
    clientUploadedImages: UploadedImage[];
    clientIpfsUrls: string[];
    isCreatingJob: boolean;
    creationLog: string[];
    creationTxHash: string;
    creationJobId: string;
    creationProgress: number;
    isDrafting: boolean;
    draftCriteria: string;
    draftMessage: string;
    draftPrice: number;
    uploadedImage: string;
}
