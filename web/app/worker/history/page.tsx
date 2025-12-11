'use client';

import { useApp } from '@/context/AppContext';
import { formatGasWithUSD } from '@/lib/currency';
import { useState, useMemo } from 'react';

type FilterStatus = 'ALL' | 'COMPLETED' | 'PAYMENT_PENDING' | 'DISPUTED' | 'REFUNDED';

export default function WorkerHistoryPage() {
    const { state } = useApp();
    const [filter, setFilter] = useState<FilterStatus>('ALL');

    // Memoize sorted jobs to prevent unnecessary recalculation
    const sortedJobs = useMemo(() => {
        // Get all jobs from workerJobs (history) and currentJobs (active)
        const allJobs = [...(state.workerJobs || []), ...(state.currentJobs || [])];
        
        // Remove duplicates by job_id (in case job appears in both arrays)
        const uniqueJobs = Array.from(
            new Map(allJobs.map(job => [job.job_id, job])).values()
        );

        // Sort by most recent
        return uniqueJobs.sort((a, b) => 
            new Date(b.assigned_at || b.created_at).getTime() - 
            new Date(a.assigned_at || a.created_at).getTime()
        );
    }, [state.workerJobs, state.currentJobs]);

    // Memoize status counts for filter buttons
    const statusCounts = useMemo(() => {
        const counts: Record<string, number> = { ALL: sortedJobs.length };
        for (const job of sortedJobs) {
            counts[job.status] = (counts[job.status] || 0) + 1;
        }
        return counts;
    }, [sortedJobs]);

    // Memoize filtered jobs
    const filteredJobs = useMemo(() => 
        filter === 'ALL' ? sortedJobs : sortedJobs.filter(job => job.status === filter),
        [sortedJobs, filter]
    );

    const getStatusBadge = (status: string) => {
        const styles: Record<string, string> = {
            'COMPLETED': 'bg-green-500/20 text-green-400',
            'PAYMENT_PENDING': 'bg-yellow-500/20 text-yellow-400',
            'LOCKED': 'bg-blue-500/20 text-blue-400',
            'DISPUTED': 'bg-red-500/20 text-red-400',
            'REFUNDED': 'bg-gray-500/20 text-gray-400',
        };
        return styles[status] || 'bg-slate-500/20 text-slate-400';
    };

    const filterButtons: { label: string; value: FilterStatus; count: number }[] = [
        { label: 'All', value: 'ALL', count: statusCounts.ALL },
        { label: 'Completed', value: 'COMPLETED', count: statusCounts.COMPLETED || 0 },
        { label: 'Pending Payment', value: 'PAYMENT_PENDING', count: statusCounts.PAYMENT_PENDING || 0 },
        { label: 'Disputed', value: 'DISPUTED', count: statusCounts.DISPUTED || 0 },
        { label: 'Refunded', value: 'REFUNDED', count: statusCounts.REFUNDED || 0 },
    ];

    return (
        <div className="animate-in fade-in duration-500">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-white mb-2">Job History</h2>
                <p className="text-slate-400">View all your completed and active jobs.</p>
            </div>

            {/* Filter Tabs */}
            <div className="flex flex-wrap gap-2 mb-6">
                {filterButtons.map(({ label, value, count }) => (
                    <button
                        key={value}
                        onClick={() => setFilter(value)}
                        className={`px-4 py-2 rounded-lg font-medium transition-all ${
                            filter === value
                                ? 'bg-cyan-600 text-white'
                                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                        }`}
                    >
                        {label} {count > 0 && <span className="ml-1 opacity-70">({count})</span>}
                    </button>
                ))}
            </div>

            {/* Stats Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                    <div className="text-slate-400 text-sm mb-1">Total Jobs</div>
                    <div className="text-white text-2xl font-bold">{state.workerStats?.total_jobs || 0}</div>
                </div>
                <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                    <div className="text-slate-400 text-sm mb-1">Completed</div>
                    <div className="text-green-400 text-2xl font-bold">{state.workerStats?.completed_jobs || 0}</div>
                </div>
                <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                    <div className="text-slate-400 text-sm mb-1">Total Earned</div>
                    <div className="text-cyan-400 text-2xl font-bold">
                        {formatGasWithUSD(state.workerStats?.total_earned || 0).gas} GAS
                    </div>
                </div>
            </div>

            {/* Jobs List */}
            {state.isLoadingJobs ? (
                <div className="text-center py-8 text-slate-400">Loading...</div>
            ) : filteredJobs.length > 0 ? (
                <div className="space-y-4">
                    {filteredJobs.map((job) => {
                        const { gas, usd } = formatGasWithUSD(job.amount);
                        const isActive = ['LOCKED', 'PAYMENT_PENDING', 'DISPUTED'].includes(job.status);
                        
                        return (
                            <div
                                key={job.job_id}
                                className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 hover:border-slate-700 transition-colors"
                            >
                                <div className="flex justify-between items-start mb-3">
                                    <div className="flex items-center gap-3">
                                        <span className="text-cyan-400 font-semibold">Job #{job.job_id}</span>
                                        {isActive && (
                                            <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full">
                                                Active
                                            </span>
                                        )}
                                    </div>
                                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge(job.status)}`}>
                                        {job.status.replaceAll('_', ' ')}
                                    </span>
                                </div>

                                <p className="text-slate-300 text-sm mb-3">{job.description}</p>

                                {job.location && (
                                    <div className="flex items-center mb-2">
                                        <svg className="h-4 w-4 text-slate-500 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                        </svg>
                                        <span className="text-slate-400 text-xs">{job.location}</span>
                                    </div>
                                )}

                                {/* Proof Photos */}
                                {job.proof_photos && job.proof_photos.length > 0 && (
                                    <div className="flex items-center mb-2">
                                        <svg className="h-4 w-4 text-slate-500 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                        </svg>
                                        <span className="text-green-400 text-xs">{job.proof_photos.length} proof photo(s) submitted</span>
                                    </div>
                                )}

                                {/* Verification Result */}
                                {job.verification_summary && (
                                    <div className={`flex items-center mb-2 ${job.verification_summary.verified ? 'text-green-400' : 'text-red-400'}`}>
                                        <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            {job.verification_summary.verified ? (
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            ) : (
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            )}
                                        </svg>
                                        <span className="text-xs">{job.verification_summary.verdict}</span>
                                    </div>
                                )}

                                <div className="flex items-center justify-between mt-4">
                                    <div className="flex flex-col sm:flex-row sm:items-center gap-2">
                                        <div className="flex items-baseline gap-1">
                                            <span className="text-cyan-400 font-semibold text-lg">{gas} GAS</span>
                                            <span className="text-slate-500 text-sm">≈ {usd}</span>
                                        </div>
                                        <span className="text-slate-500 text-xs">
                                            • Assigned {new Date(job.assigned_at || job.created_at).toLocaleDateString()}
                                        </span>
                                        {job.completed_at && (
                                            <span className="text-slate-500 text-xs">
                                                • Completed {new Date(job.completed_at).toLocaleDateString()}
                                            </span>
                                        )}
                                    </div>

                                    {job.tx_hash && (
                                        <a
                                            href={`https://dora.coz.io/transaction/neo3/testnet/${job.tx_hash}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-cyan-500 hover:text-cyan-400 text-xs underline flex items-center gap-1"
                                        >
                                            <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                                            </svg>
                                            View TX
                                        </a>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            ) : (
                <div className="text-center py-12 bg-slate-900/30 border border-slate-800 rounded-xl">
                    <p className="text-slate-400 mb-2">No jobs found</p>
                    <p className="text-slate-500 text-sm">
                        {filter === 'ALL' 
                            ? 'Claim your first job to start building your work history.' 
                            : `No jobs with status "${filter.replaceAll('_', ' ')}".`
                        }
                    </p>
                </div>
            )}
        </div>
    );
}
