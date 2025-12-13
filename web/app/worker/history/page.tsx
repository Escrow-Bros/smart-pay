'use client';

import type { ReactNode } from 'react';
import { useApp } from '@/context/AppContext';
import { formatGasWithUSD } from '@/lib/currency';
import { useState, useMemo } from 'react';
import { Briefcase, CheckCircle2, Clock, AlertTriangle, RotateCcw, MapPin, Image, ExternalLink, Loader2 } from 'lucide-react';

type FilterStatus = 'ALL' | 'COMPLETED' | 'PAYMENT_PENDING' | 'DISPUTED' | 'REFUNDED';

export default function WorkerHistoryPage() {
    const { state } = useApp();
    const [filter, setFilter] = useState<FilterStatus>('ALL');

    // Memoize sorted jobs to prevent unnecessary recalculation
    const sortedJobs = useMemo(() => {
        const allJobs = [...(state.workerJobs || []), ...(state.currentJobs || [])];

        const uniqueJobs = Array.from(
            new Map(allJobs.map(job => [job.job_id, job])).values()
        );

        const getTimestamp = (dateStr: string | undefined): number => {
            if (!dateStr) return 0;
            const time = new Date(dateStr).getTime();
            return isNaN(time) ? 0 : time;
        };

        return uniqueJobs.sort((a, b) =>
            getTimestamp(b.assigned_at || b.created_at) -
            getTimestamp(a.assigned_at || a.created_at)
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
            <div className="flex flex-wrap gap-2 mb-6">
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
                            {label} {count > 0 && <span className="ml-1 opacity-70">({count})</span>}
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

            {/* Jobs List */}
            {state.isLoadingJobs ? (
                /* Loading Skeleton */
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="glass border border-slate-800 rounded-2xl p-6 animate-pulse">
                            <div className="flex justify-between items-start mb-4">
                                <div className="loading-skeleton h-5 w-24 rounded"></div>
                                <div className="loading-skeleton h-6 w-20 rounded-full"></div>
                            </div>
                            <div className="loading-skeleton h-4 w-3/4 rounded mb-2"></div>
                            <div className="loading-skeleton h-4 w-1/2 rounded"></div>
                        </div>
                    ))}
                </div>
            ) : filteredJobs.length > 0 ? (
                <div className="space-y-4">
                    {filteredJobs.map((job, index) => {
                        const { gas, usd } = formatGasWithUSD(job.amount);
                        const isActive = ['LOCKED', 'PAYMENT_PENDING', 'DISPUTED'].includes(job.status);
                        const statusConfig = getStatusConfig(job.status);

                        return (
                            <div
                                key={job.job_id}
                                className={`group glass border border-slate-800 rounded-2xl p-6 hover:border-cyan-500/50 hover-glow-cyan transition-all animate-fade-in-up stagger-${(index % 4) + 1}`}
                            >
                                <div className="flex justify-between items-start mb-3">
                                    <div className="flex items-center gap-3">
                                        <span className="text-cyan-400 font-semibold">Job #{job.job_id}</span>
                                        {isActive && (
                                            <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 text-xs rounded-full flex items-center gap-1">
                                                <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse"></span>
                                                Active
                                            </span>
                                        )}
                                    </div>
                                    <span className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${statusConfig.bg} ${statusConfig.text}`}>
                                        {statusConfig.icon}
                                        {job.status.replaceAll('_', ' ')}
                                    </span>
                                </div>

                                <p className="text-slate-300 text-sm mb-3 leading-relaxed">{job.description}</p>

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
                                {job.verification_summary && (
                                    <div className={`flex items-center mb-2 ${job.verification_summary.verified ? 'text-green-400' : 'text-red-400'}`}>
                                        {job.verification_summary.verified ? (
                                            <CheckCircle2 className="h-4 w-4 mr-1.5" />
                                        ) : (
                                            <AlertTriangle className="h-4 w-4 mr-1.5" />
                                        )}
                                        <span className="text-xs">{job.verification_summary.verdict}</span>
                                    </div>
                                )}

                                <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-800">
                                    <div className="flex flex-col sm:flex-row sm:items-center gap-2">
                                        <div className="flex items-baseline gap-1">
                                            <span className="text-cyan-400 font-semibold text-lg">{gas} GAS</span>
                                            <span className="text-slate-500 text-sm">≈ {usd}</span>
                                        </div>
                                        <span className="text-slate-500 text-xs">
                                            • {(() => {
                                                const dateStr = job.assigned_at || job.created_at;
                                                if (!dateStr) return 'Unknown date';
                                                const time = new Date(dateStr).getTime();
                                                return isNaN(time) ? 'Unknown date' : new Date(dateStr).toLocaleDateString();
                                            })()}
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
                    })}
                </div>
            ) : (
                <div className="text-center py-16 glass border border-slate-800 rounded-2xl">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-slate-800/50 flex items-center justify-center">
                        <Briefcase className="w-8 h-8 text-slate-600" />
                    </div>
                    <h3 className="text-lg font-semibold text-white mb-2">No jobs found</h3>
                    <p className="text-slate-400">
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
