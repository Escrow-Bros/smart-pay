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
    tx_hash?: string | null;
    verification_result?: Record<string, unknown> | null;
    verification_summary?: {
        verified: boolean;
        verdict: string;
    } | null;
}

export interface WorkerStats {
    total_jobs: number;
    completed_jobs: number;
    total_earned: number;
}

export type UserMode = 'client' | 'worker';

export interface GlobalState {
    // User state
    userMode: UserMode | null;
    currentUser: string | null;
    walletAddress: string;

    // Wallet
    walletBalance: number;
    isLoadingBalance: boolean;

    // Jobs
    availableJobs: JobDict[];
    clientJobs: JobDict[];
    workerJobs: JobDict[];
    currentJob: JobDict | null;
    workerStats: WorkerStats;
    isLoadingJobs: boolean;

    // Job creation
    jobDescription: string;
    jobLocation: string;
    jobLatitude: number;
    jobLongitude: number;
    clientUploadedImages: string[];
    clientIpfsUrls: string[];
    isCreatingJob: boolean;
    creationLog: string[];
    creationTxHash: string;
    creationJobId: string;
    creationProgress: number;

    // Draft state
    isDrafting: boolean;
    draftCriteria: string;
    draftMessage: string;
    draftPrice: number;

    // Worker proof
    uploadedImage: string;
}
