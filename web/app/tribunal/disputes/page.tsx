'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import type { DisputeDict } from '@/lib/types';

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

        // Status filter
        if (activeFilter !== 'all') {
            filtered = filtered.filter(d => d.status === activeFilter.toUpperCase());
        }

        // Search filter
        if (searchQuery.trim()) {
            const query = searchQuery.toLowerCase();
            filtered = filtered.filter(d =>
                d.job_id.toString().includes(query) ||
                d.reason.toLowerCase().includes(query) ||
                d.description?.toLowerCase().includes(query) ||
                d.raised_by?.toLowerCase().includes(query)
            );
        }

        // Sort by most recent
        filtered.sort((a, b) => new Date(b.raised_at).getTime() - new Date(a.raised_at).getTime());

        setFilteredDisputes(filtered);
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-gray-500">Loading disputes...</div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Error Banner */}
            {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                            <span className="text-red-600 text-xl">⚠️</span>
                            <div>
                                <h3 className="text-sm font-semibold text-red-800 mb-1">Failed to Load Disputes</h3>
                                <p className="text-sm text-red-700">{error}</p>
                            </div>
                        </div>
                        <button
                            onClick={fetchDisputes}
                            className="ml-4 px-4 py-2 bg-red-100 hover:bg-red-200 text-red-800 text-sm font-medium rounded-lg transition-colors"
                        >
                            Retry
                        </button>
                    </div>
                </div>
            )}

            {/* Filters and Search */}
            <div className="bg-white rounded-lg shadow p-4">
                <div className="flex flex-col md:flex-row gap-4">
                    {/* Search */}
                    <div className="flex-1">
                        <input
                            type="text"
                            placeholder="Search by job ID, reason, or address..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                    </div>

                    {/* Status Filters */}
                    <div className="flex gap-2">
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

                <div className="mt-3 text-sm text-gray-600">
                    Showing {filteredDisputes.length} of {disputes.length} disputes
                </div>
            </div>

            {/* Disputes List */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                {filteredDisputes.length === 0 ? (
                    <div className="px-6 py-12 text-center text-gray-500">
                        <div className="text-4xl mb-2">🔍</div>
                        <p>No disputes found</p>
                        <p className="text-sm mt-1">Try adjusting your filters or search query</p>
                    </div>
                ) : (
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Dispute ID
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Job ID
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Status
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Reason
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Amount
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Raised At
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Action
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {filteredDisputes.map((dispute) => (
                                <tr key={dispute.dispute_id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                        #{dispute.dispute_id}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        #{dispute.job_id}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <StatusBadge status={dispute.status} />
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                                        {dispute.reason}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        {dispute.amount} GAS
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {new Date(dispute.raised_at).toLocaleDateString()}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                                        <Link
                                            href={`/tribunal/disputes/${dispute.dispute_id}`}
                                            className="text-blue-600 hover:text-blue-900 font-medium"
                                        >
                                            View Details →
                                        </Link>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
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
    const colorClasses = {
        gray: isActive ? 'bg-gray-200 text-gray-900' : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
        red: isActive ? 'bg-red-600 text-white' : 'bg-red-100 text-red-700 hover:bg-red-200',
        yellow: isActive ? 'bg-yellow-600 text-white' : 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200',
        green: isActive ? 'bg-green-600 text-white' : 'bg-green-100 text-green-700 hover:bg-green-200',
    }[color];

    return (
        <button
            onClick={onClick}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${colorClasses}`}
        >
            {label} ({count})
        </button>
    );
}

function StatusBadge({ status }: { status: string }) {
    const colorClasses = {
        PENDING: 'bg-red-100 text-red-800',
        UNDER_REVIEW: 'bg-yellow-100 text-yellow-800',
        RESOLVED: 'bg-green-100 text-green-800',
    }[status] || 'bg-gray-100 text-gray-800';

    return (
        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${colorClasses}`}>
            {status.replace('_', ' ')}
        </span>
    );
}

export default function AllDisputesPage() {
    return (
        <Suspense fallback={
            <div className="flex items-center justify-center h-64">
                <div className="text-gray-500">Loading disputes...</div>
            </div>
        }>
            <DisputesContent />
        </Suspense>
    );
}
