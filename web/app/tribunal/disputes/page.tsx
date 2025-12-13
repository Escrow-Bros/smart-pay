'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import type { DisputeDict } from '@/lib/types';
import { Search, Clock, Eye, CheckCircle2, ChevronRight, AlertTriangle, RefreshCw, Loader2 } from 'lucide-react';

function DisputesContent() {
    const searchParams = useSearchParams();
    const statusFilter = searchParams.get('status') || 'all';

    const [disputes, setDisputes] = useState<DisputeDict[]>([]);
    const [filteredDisputes, setFilteredDisputes] = useState<DisputeDict[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [activeFilter, setActiveFilter] = useState<string>(statusFilter);

    useEffect(() => {
        fetchDisputes();
    }, []);

    useEffect(() => {
        applyFilters();
    }, [disputes, activeFilter, searchQuery]);

    const fetchDisputes = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/disputes`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success) {
                setDisputes(data.disputes);
                setError(null);
            } else {
                setError(data.error || 'Failed to load disputes');
            }
        } catch (err) {
            console.error('Failed to fetch disputes:', err);
            const errorMessage = err instanceof Error ? err.message : 'Network error. Please check your connection.';
            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const applyFilters = () => {
        let filtered = [...disputes];

        if (activeFilter !== 'all') {
            filtered = filtered.filter(d => d.status === activeFilter.toUpperCase());
        }

        if (searchQuery.trim()) {
            const query = searchQuery.toLowerCase();
            filtered = filtered.filter(d =>
                d.job_id.toString().includes(query) ||
                d.reason.toLowerCase().includes(query) ||
                d.description?.toLowerCase().includes(query) ||
                d.raised_by?.toLowerCase().includes(query)
            );
        }

        filtered.sort((a, b) => new Date(b.raised_at).getTime() - new Date(a.raised_at).getTime());

        setFilteredDisputes(filtered);
    };

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center h-64 animate-fade-in-up">
                <Loader2 className="w-8 h-8 text-purple-400 animate-spin mb-4" />
                <p className="text-slate-400">Loading disputes...</p>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-fade-in-up">
            {/* Error Banner */}
            {error && (
                <div className="glass border border-red-500/30 bg-red-500/10 rounded-2xl p-4">
                    <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                            <AlertTriangle className="w-5 h-5 text-red-400 mt-0.5" />
                            <div>
                                <h3 className="text-sm font-semibold text-red-400 mb-1">Failed to Load Disputes</h3>
                                <p className="text-sm text-slate-400">{error}</p>
                            </div>
                        </div>
                        <button
                            onClick={fetchDisputes}
                            className="flex items-center gap-2 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 text-sm font-medium rounded-xl transition-colors"
                        >
                            <RefreshCw className="w-4 h-4" />
                            Retry
                        </button>
                    </div>
                </div>
            )}

            {/* Filters and Search */}
            <div className="glass border border-slate-800 rounded-2xl p-4">
                <div className="flex flex-col md:flex-row gap-4">
                    {/* Search */}
                    <div className="flex-1 relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                        <input
                            type="text"
                            placeholder="Search by job ID, reason, or address..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-10 pr-4 py-2.5 bg-slate-800/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                        />
                    </div>

                    {/* Status Filters */}
                    <div className="flex gap-2 flex-wrap">
                        <FilterButton
                            label="All"
                            count={disputes.length}
                            isActive={activeFilter === 'all'}
                            onClick={() => setActiveFilter('all')}
                        />
                        <FilterButton
                            label="Pending"
                            count={disputes.filter(d => d.status === 'PENDING').length}
                            isActive={activeFilter === 'pending'}
                            onClick={() => setActiveFilter('pending')}
                            color="red"
                        />
                        <FilterButton
                            label="Under Review"
                            count={disputes.filter(d => d.status === 'UNDER_REVIEW').length}
                            isActive={activeFilter === 'under_review'}
                            onClick={() => setActiveFilter('under_review')}
                            color="yellow"
                        />
                        <FilterButton
                            label="Resolved"
                            count={disputes.filter(d => d.status === 'RESOLVED').length}
                            isActive={activeFilter === 'resolved'}
                            onClick={() => setActiveFilter('resolved')}
                            color="green"
                        />
                    </div>
                </div>

                <div className="mt-3 text-sm text-slate-500">
                    Showing {filteredDisputes.length} of {disputes.length} disputes
                </div>
            </div>

            {/* Disputes List */}
            <div className="glass border border-slate-800 rounded-2xl overflow-hidden">
                {filteredDisputes.length === 0 ? (
                    <div className="px-6 py-16 text-center">
                        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-slate-800/50 flex items-center justify-center">
                            <Search className="w-8 h-8 text-slate-600" />
                        </div>
                        <h3 className="text-lg font-semibold text-white mb-2">No disputes found</h3>
                        <p className="text-slate-400">Try adjusting your filters or search query</p>
                    </div>
                ) : (
                    <div className="divide-y divide-slate-800">
                        {filteredDisputes.map((dispute, index) => (
                            <Link
                                key={dispute.dispute_id}
                                href={`/tribunal/disputes/${dispute.dispute_id}`}
                                className={`group block px-6 py-5 hover:bg-slate-800/50 transition-all animate-fade-in-up stagger-${(index % 4) + 1}`}
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-3 mb-2">
                                            <span className="text-purple-400 font-semibold">#{dispute.dispute_id}</span>
                                            <span className="text-slate-600">•</span>
                                            <span className="text-sm text-slate-500">Job #{dispute.job_id}</span>
                                            <StatusBadge status={dispute.status} />
                                        </div>
                                        <h3 className="text-sm font-medium text-white truncate mb-1 group-hover:text-purple-300 transition-colors">
                                            {dispute.reason}
                                        </h3>
                                        <div className="flex items-center gap-4 text-xs text-slate-500">
                                            <span>{dispute.amount} GAS</span>
                                            <span>•</span>
                                            <span>{new Date(dispute.raised_at).toLocaleDateString()}</span>
                                        </div>
                                    </div>
                                    <div className="ml-4 flex-shrink-0">
                                        <ChevronRight className="w-5 h-5 text-slate-600 group-hover:text-purple-400 group-hover:translate-x-1 transition-all" />
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

function FilterButton({
    label,
    count,
    isActive,
    onClick,
    color = 'gray'
}: {
    label: string;
    count: number;
    isActive: boolean;
    onClick: () => void;
    color?: string;
}) {
    const colorClasses: Record<string, string> = {
        gray: isActive ? 'bg-slate-600 text-white border-slate-500' : 'bg-slate-800/50 text-slate-400 border-slate-700 hover:border-slate-600',
        red: isActive ? 'bg-red-500/20 text-red-400 border-red-500/50' : 'bg-slate-800/50 text-slate-400 border-slate-700 hover:border-red-500/50 hover:text-red-400',
        yellow: isActive ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50' : 'bg-slate-800/50 text-slate-400 border-slate-700 hover:border-yellow-500/50 hover:text-yellow-400',
        green: isActive ? 'bg-green-500/20 text-green-400 border-green-500/50' : 'bg-slate-800/50 text-slate-400 border-slate-700 hover:border-green-500/50 hover:text-green-400',
    };

    return (
        <button
            onClick={onClick}
            className={`px-4 py-2 rounded-xl text-sm font-medium border transition-all ${colorClasses[color]}`}
        >
            {label} ({count})
        </button>
    );
}

function StatusBadge({ status }: { status: string }) {
    const config: Record<string, { bg: string; text: string; icon: React.ReactNode }> = {
        PENDING: { bg: 'bg-red-500/20', text: 'text-red-400', icon: <Clock className="w-3 h-3" /> },
        UNDER_REVIEW: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', icon: <Eye className="w-3 h-3" /> },
        RESOLVED: { bg: 'bg-green-500/20', text: 'text-green-400', icon: <CheckCircle2 className="w-3 h-3" /> },
    };

    const { bg, text, icon } = config[status] || { bg: 'bg-slate-700', text: 'text-slate-400', icon: null };

    return (
        <span className={`flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full ${bg} ${text}`}>
            {icon}
            {status.replace('_', ' ')}
        </span>
    );
}

export default function AllDisputesPage() {
    return (
        <Suspense fallback={
            <div className="flex flex-col items-center justify-center h-64 animate-fade-in-up">
                <Loader2 className="w-8 h-8 text-purple-400 animate-spin mb-4" />
                <p className="text-slate-400">Loading disputes...</p>
            </div>
        }>
            <DisputesContent />
        </Suspense>
    );
}
