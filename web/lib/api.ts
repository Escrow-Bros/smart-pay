const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiClient {
    private baseUrl: string;

    constructor() {
        this.baseUrl = API_BASE_URL;
    }

    async getWalletBalance(address: string): Promise<number> {
        const res = await fetch(`${this.baseUrl}/api/wallet/balance/${address}`);
        const data = await res.json();
        return data.balance;
    }

    async getAvailableJobs() {
        const res = await fetch(`${this.baseUrl}/api/jobs/available`);
        return res.json();
    }

    async getClientJobs(address: string) {
        const res = await fetch(`${this.baseUrl}/api/jobs/client/${address}`);
        return res.json();
    }

    async getWorkerJobs(address: string) {
        const res = await fetch(`${this.baseUrl}/api/jobs/worker/${address}`);
        return res.json();
    }

    async analyzeJob(formData: FormData) {
        const res = await fetch(`${this.baseUrl}/api/jobs/analyze`, {
            method: 'POST',
            body: formData,
        });
        return res.json();
    }

    async createJob(payload: {
        client_address: string;
        description: string;
        reference_photos: string[];
        location: string;
        latitude: number;
        longitude: number;
        amount: number;
        verification_plan: Record<string, any>;
    }) {
        const res = await fetch(`${this.baseUrl}/api/jobs/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        return res.json();
    }

    async assignJob(jobId: number, workerAddress: string) {
        const res = await fetch(`${this.baseUrl}/api/jobs/assign`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_id: jobId, worker_address: workerAddress }),
        });
        return res.json();
    }

    async submitProof(jobId: number, proofPhotos: string[], workerLocation?: { lat: number; lng: number; accuracy: number }) {
        const res = await fetch(`${this.baseUrl}/api/jobs/${jobId}/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                proof_photos: proofPhotos,
                worker_location: workerLocation
            }),
        });
        return res.json();
    }

    async uploadProofImage(file: File): Promise<string> {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch(`${this.baseUrl}/api/upload/proof`, {
            method: 'POST',
            body: formData,
        });
        const data = await res.json();
        return data.ipfs_url;
    }

    async uploadToIpfs(file: File): Promise<string> {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch(`${this.baseUrl}/api/ipfs/upload`, {
            method: 'POST',
            body: formData,
        });
        const data = await res.json();
        return data.url;
    }
}

export const apiClient = new ApiClient();
