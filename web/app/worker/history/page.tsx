'use client';

import type { ReactNode } from 'react';
import { useState, useMemo } from 'react';
import { useApp } from '@/context/AppContext';
import { formatGasWithUSD } from '@/lib/currency';
import { Briefcase, CheckCircle2, Clock, AlertTriangle, RotateCcw, MapPin, Image, ExternalLink, Loader2 } from 'lucide-react';
import type { JobDict } from '@/lib/types';
import VerificationModal from '@/components/VerificationModal';
import { getVerificationStatus } from '@/lib/verification';

type FilterStatus = 'ALL' | 'COMPLETED' | 'PAYMENT_PENDING' | 'DISPUTED' | 'REFUNDED';

// Safe timestamp parser
const getTimestamp = (dateStr: string | undefined): number => {
    if (!dateStr) return 0;
    const time = new Date(dateStr).getTime();
    return isNaN(time) ? 0 : time;
};

// Format date with fallback
const formatDate = (dateStr: string | undefined): string => {
    const time = getTimestamp(dateStr);
    return time === 0 ? 'Unknown date' : new Date(time).toLocaleDateString();
};

export default function WorkerHistoryPage() {
    const { state } = useApp();
    const [filter, setFilter] = useState<FilterStatus>('ALL');
    const [selectedJobForVerification, setSelectedJobForVerification] = useState<JobDict | null>(null);

    // Filter jobs first
    const relevantJobs = useMemo(() => {
        const allJobs = [...(state.workerJobs || []), ...(state.currentJobs || [])];
        const uniqueJobs = Array.from(
            new Map(allJobs.map(job => [job.job_id, job])).values()
        );
        return uniqueJobs;
    }, [state.workerJobs, state.currentJobs]);

    // Use derived state for initial loading to prevent flash
    // If we have no jobs but isLoadingJobs is true (or we have just mounted/no data yet), we can show a loader or equivalent.
    // However, AppContext sets isLoadingJobs. Let's rely on state.isLoadingJobs if it's reliable, 
    // or simply check if we have data vs empty state.
    // The user mentioned checking `filteredJobs.length === 0` renders immediately.

    // Stable Sort with deterministic tie-breaker
    const sortedJobs = useMemo(() => {
        return [...relevantJobs].sort((a, b) => {
            const diff = getTimestamp(b.assigned_at || b.created_at) - getTimestamp(a.assigned_at || a.created_at);
            if (diff !== 0) return diff;
            // deterministic tie-breaker
            return String(b.job_id).localeCompare(String(a.job_id));
        });
    }, [relevantJobs]);

    // Memoize stats
    const statusCounts = useMemo(() => {
        const counts: Record<string, number> = { ALL: sortedJobs.length };
        for (const job of sortedJobs) {
            counts[job.status] = (counts[job.status] || 0) + 1;
        }
        return counts;
    }, [sortedJobs]);

    // Filtered list
    const filteredJobs = useMemo(() =>
        filter === 'ALL' ? sortedJobs : sortedJobs.filter(job => job.status === filter),
        [sortedJobs, filter]
    );

    const getStatusConfig = (status: string) => {
        const configs: Record<string, { bg: string; text: string; icon: ReactNode }> = {
            'COMPLETED': { bg: 'bg-green-500/20', text: 'text-green-400', icon: <CheckCircle2 className="w-3 h-3" /> },
            'PAYMENT_PENDING': { bg: 'bg-yellow-500/20', text: 'text-yellow-400', icon: <Clock className="w-3 h-3" /> },
            'LOCKED': { bg: 'bg-blue-500/20', text: 'text-blue-400', icon: <Clock className="w-3 h-3" /> },
            'DISPUTED': { bg: 'bg-red-500/20', text: 'text-red-400', icon: <AlertTriangle className="w-3 h-3" /> },
            'REFUNDED': { bg: 'bg-gray-500/20', text: 'text-gray-400', icon: <RotateCcw className="w-3 h-3" /> },
        };
        return configs[status] || { bg: 'bg-slate-500/20', text: 'text-slate-400', icon: null };
    };

    const filterButtons: { label: string; value: FilterStatus; count: number; color: string }[] = [
        { label: 'All', value: 'ALL', count: statusCounts.ALL, color: 'gray' },
        { label: 'Completed', value: 'COMPLETED', count: statusCounts.COMPLETED || 0, color: 'green' },
        { label: 'Pending', value: 'PAYMENT_PENDING', count: statusCounts.PAYMENT_PENDING || 0, color: 'yellow' },
        { label: 'Disputed', value: 'DISPUTED', count: statusCounts.DISPUTED || 0, color: 'red' },
        { label: 'Refunded', value: 'REFUNDED', count: statusCounts.REFUNDED || 0, color: 'gray' },
    ];

    return (
        <div className="animate-fade-in-up">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-white mb-2">Job History</h2>
                <p className="text-slate-400">View all your completed and active jobs.</p>
            </div>

            {/* Filter Tabs */}
            <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
                {filterButtons.map(({ label, value, count, color }) => {
                    const isActive = filter === value;
                    const colorClasses: Record<string, string> = {
                        gray: isActive ? 'bg-slate-600 text-white border-slate-500' : 'border-slate-700 hover:border-slate-600',
                        green: isActive ? 'bg-green-500/20 text-green-400 border-green-500/50' : 'border-slate-700 hover:border-green-500/50 hover:text-green-400',
                        yellow: isActive ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50' : 'border-slate-700 hover:border-yellow-500/50 hover:text-yellow-400',
                        red: isActive ? 'bg-red-500/20 text-red-400 border-red-500/50' : 'border-slate-700 hover:border-red-500/50 hover:text-red-400',
                    };

                    return (
                        <button
                            key={value}
                            onClick={() => setFilter(value)}
                            className={`px-4 py-2 rounded-xl font-medium border transition-all text-sm ${isActive ? colorClasses[color] : `bg-slate-800/50 text-slate-400 ${colorClasses[color]}`
                                }`}
                        >
                            {label} <span className="ml-1 opacity-60 text-xs">({count})</span>
                        </button>
                    );
                })}
            </div>

            {/* Stats Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="glass border border-slate-800 rounded-2xl p-5">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-slate-700/50 rounded-lg">
                            <Briefcase className="w-5 h-5 text-slate-400" />
                        </div>
                        <div className="text-slate-400 text-sm">Total Jobs</div>
                    </div>
                    <div className="text-white text-2xl font-bold">{state.workerStats?.total_jobs || 0}</div>
                </div>
                <div className="glass border border-green-500/30 rounded-2xl p-5">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-green-500/20 rounded-lg">
                            <CheckCircle2 className="w-5 h-5 text-green-400" />
                        </div>
                        <div className="text-slate-400 text-sm">Completed</div>
                    </div>
                    <div className="text-green-400 text-2xl font-bold">{state.workerStats?.completed_jobs || 0}</div>
                </div>
                <div className="glass border border-cyan-500/30 rounded-2xl p-5">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-cyan-500/20 rounded-lg">
                            <Briefcase className="w-5 h-5 text-cyan-400" />
                        </div>
                        <div className="text-slate-400 text-sm">Total Earned</div>
                    </div>
                    <div className="text-cyan-400 text-2xl font-bold">
                        {formatGasWithUSD(state.workerStats?.total_earned || 0).gas} GAS
                    </div>
                </div>
            </div>

            {/* Job List */}
            <div className="space-y-4">
                {state.isLoadingJobs ? (
                    <div className="flex justify-center py-12">
                        <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
                    </div>
                ) : filteredJobs.length === 0 ? (
                    <div className="text-center py-12 bg-slate-800/30 rounded-2xl border border-slate-700 border-dashed">
                        <Briefcase className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                        <h3 className="text-xl font-semibold text-slate-400">No jobs found</h3>
                        <p className="text-slate-500 mt-2">Try changing the filter or look for new work.</p>
                    </div>
                ) : (
                    filteredJobs.map((job) => {
                        const statusConfig = getStatusConfig(job.status);
                        const { gas, usd } = formatGasWithUSD(job.amount);

                        const status = getVerificationStatus(job);

                        return (
                            <div
                                key={job.job_id}
                                className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-5 hover:bg-slate-800/60 transition-colors group"
                            >

                                {job.location && (
                                    <div className="flex items-center mb-2 text-slate-400">
                                        <MapPin className="h-4 w-4 mr-1.5 text-slate-500" />
                                        <span className="text-xs">{job.location}</span>
                                    </div>
                                )}

                                {/* Proof Photos */}
                                {job.proof_photos && job.proof_photos.length > 0 && (
                                    <div className="flex items-center mb-2">
                                        <Image className="h-4 w-4 mr-1.5 text-green-400" />
                                        <span className="text-green-400 text-xs">{job.proof_photos.length} proof photo(s) submitted</span>
                                    </div>
                                )}

                                {/* Verification Result */}
                                {status && (
                                    <button
                                        type="button"
                                        onClick={() => setSelectedJobForVerification(job)}
                                        aria-label={`Open verification report for job ${job.job_id}`}
                                        className={`flex items-center mb-2 text-left bg-transparent p-0 border-0 cursor-pointer hover:opacity-80 transition-opacity focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900 focus-visible:outline-none rounded-md ${status.isApproved ? 'text-green-400 focus-visible:ring-green-500' : 'text-red-400 focus-visible:ring-red-500'}`}
                                    >
                                        {status.isApproved ? (
                                            <CheckCircle2 className="h-4 w-4 mr-1.5" />
                                        ) : (
                                            <AlertTriangle className="h-4 w-4 mr-1.5" />
                                        )}
                                        <span className="text-xs">{status.verdict} • Click for details</span>
                                    </button>
                                )}

                                <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-800">
                                    <div className="flex flex-col sm:flex-row sm:items-center gap-2">
                                        <div className="flex items-baseline gap-1">
                                            <span className="text-cyan-400 font-semibold text-lg">{gas} GAS</span>
                                            <span className="text-slate-500 text-sm">≈ {usd}</span>
                                        </div>
                                        <span className="text-slate-500 text-xs">
                                            • {formatDate(job.assigned_at || job.created_at)}
                                        </span>
                                    </div>

                                    {job.tx_hash && (
                                        <a
                                            href={`https://dora.coz.io/transaction/neo3/testnet/${job.tx_hash}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="flex items-center gap-1.5 text-cyan-500 hover:text-cyan-400 text-xs transition-colors"
                                        >
                                            <ExternalLink className="h-3 w-3" />
                                            View TX
                                        </a>
                                    )}
                                </div>
                            </div>
                        );
                    })
                )}
            </div>

            {/* Verification Details Modal */}
            <VerificationModal
                isOpen={!!selectedJobForVerification}
                onClose={() => setSelectedJobForVerification(null)}
                job={selectedJobForVerification}
            />
        </div>
    );
}
