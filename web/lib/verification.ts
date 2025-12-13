import { JobDict } from './types';

export interface GPSVerification {
    location_match?: boolean;
    distance_meters?: number;
}

export interface Comparison {
    same_object?: boolean;
    transformation_occurred?: boolean;
}

export interface VerificationResult {
    score?: number;
    confidence?: number;
    verdict?: string | boolean;
    verified?: boolean;
    gps_verification?: GPSVerification;
    breakdown?: {
        visual_location?: GPSVerification;
        comparison?: Comparison;
    };
    comparison?: Comparison;
    reason?: string;
    reasoning?: string;
    issues?: string[];
}

export function isGPSVerification(obj: unknown): obj is GPSVerification {
    return typeof obj === 'object' && obj !== null && (
        'location_match' in obj || 'distance_meters' in obj
    );
}

export function isComparison(obj: unknown): obj is Comparison {
    return typeof obj === 'object' && obj !== null && (
        'same_object' in obj || 'transformation_occurred' in obj
    );
}

export function getVerificationStatus(job: JobDict | null) {
    if (!job) return null;

    // Safely extract verification data (prefer summary, fall back to result)
    const rawResult: unknown = job.verification_summary ?? job.verification_result;

    if (!rawResult || typeof rawResult !== 'object') return null;

    // Cast using our defined interface for safer access
    const r = rawResult as VerificationResult;

    const rawScore = r.score ?? r.confidence;

    // Normalize score: if <= 1 (e.g. 0.95), multiply by 100. If > 1 (e.g. 95), keep as is.
    const score =
        typeof rawScore === 'number'
            ? Math.max(0, Math.min(100, rawScore <= 1 ? Math.round(rawScore * 100) : Math.round(rawScore)))
            : 0;

    const verdictText = typeof r.verdict === 'string' ? r.verdict : 'Verification complete';
    const isApproved = r.verified === true || r.verdict === 'APPROVED' || r.verdict === true;

    return {
        result: r,
        score,
        verdict: verdictText,
        isApproved
    };
}
