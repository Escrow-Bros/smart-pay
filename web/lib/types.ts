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
    verification_plan?: Record<string, any>;
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
