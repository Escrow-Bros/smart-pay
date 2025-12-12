'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import type { DisputeDict } from '@/lib/types';

interface DisputeStats {
    pending: number;
    under_review: number;
    resolved: number;
    total: number;
}

export default function TribunalDashboard() {
    const [stats, setStats] = useState<DisputeStats>({ pending: 0, under_review: 0, resolved: 0, total: 0 });
    const [recentDisputes, setRecentDisputes] = useState<DisputeDict[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/disputes`);
            const data = await response.json();

            if (data.success) {
                const disputes = data.disputes as DisputeDict[];

                // Calculate stats
                const pending = disputes.filter(d => d.status === 'PENDING').length;
                const under_review = disputes.filter(d => d.status === 'UNDER_REVIEW').length;
                const resolved = disputes.filter(d => d.status === 'RESOLVED').length;

                setStats({
                    pending,
                    under_review,
                    resolved,
                    total: disputes.length
                });

                // Get 5 most recent unresolved disputes
                const unresolved = disputes
                    .filter(d => d.status !== 'RESOLVED')
                    .slice(0, 5);
                setRecentDisputes(unresolved);
            }
        } catch (error) {
            console.error('Failed to fetch disputes:', error);
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-gray-500">Loading dashboard...</div>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <StatCard
                    title="Pending Review"
                    value={stats.pending}
                    color="red"
                    icon="⏱️"
                />
                <StatCard
                    title="Under Review"
                    value={stats.under_review}
                    color="yellow"
                    icon="🔍"
                />
                <StatCard
                    title="Resolved"
                    value={stats.resolved}
                    color="green"
                    icon="✅"
                />
                <StatCard
                    title="Total Disputes"
                    value={stats.total}
                    color="blue"
                    icon="📊"
                />
            </div>

            {/* Recent Disputes */}
            <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-gray-900">Recent Unresolved Disputes</h2>
                    <Link
                        href="/tribunal/disputes"
                        className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                    >
                        View All →
                    </Link>
                </div>

                {recentDisputes.length === 0 ? (
                    <div className="px-6 py-12 text-center text-gray-500">
                        <div className="text-4xl mb-2">🎉</div>
                        <p>No pending disputes!</p>
                        <p className="text-sm mt-1">All work is being approved smoothly.</p>
                    </div>
                ) : (
                    <div className="divide-y divide-gray-200">
                        {recentDisputes.map((dispute) => (
                            <Link
                                key={dispute.dispute_id}
                                href={`/tribunal/disputes/${dispute.dispute_id}`}
                                className="block px-6 py-4 hover:bg-gray-50 transition-colors"
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-3 mb-2">
                                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${dispute.status === 'PENDING'
                                                    ? 'bg-red-100 text-red-800'
                                                    : 'bg-yellow-100 text-yellow-800'
                                                }`}>
                                                {dispute.status}
                                            </span>
                                            <span className="text-sm text-gray-500">
                                                Job #{dispute.job_id}
                                            </span>
                                        </div>
                                        <h3 className="text-sm font-medium text-gray-900 truncate mb-1">
                                            {dispute.description || 'No description'}
                                        </h3>
                                        <p className="text-sm text-gray-600 line-clamp-2">
                                            {dispute.reason}
                                        </p>
                                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                                            <span>Raised by: {dispute.raised_by?.slice(0, 10)}...</span>
                                            <span>Amount: {dispute.amount} GAS</span>
                                            <span>{new Date(dispute.raised_at).toLocaleDateString()}</span>
                                        </div>
                                    </div>
                                    <div className="ml-4 flex-shrink-0">
                                        <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                        </svg>
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                )}
            </div>

            {/* Quick Actions */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-sm font-semibold text-blue-900 mb-3">Quick Actions</h3>
                <div className="space-y-2">
                    <Link
                        href="/tribunal/disputes?status=PENDING"
                        className="block text-sm text-blue-700 hover:text-blue-900 hover:underline"
                    >
                        → Review pending disputes ({stats.pending})
                    </Link>
                    <Link
                        href="/tribunal/disputes?status=UNDER_REVIEW"
                        className="block text-sm text-blue-700 hover:text-blue-900 hover:underline"
                    >
                        → Continue reviews in progress ({stats.under_review})
                    </Link>
                    <Link
                        href="/tribunal/disputes?status=RESOLVED"
                        className="block text-sm text-blue-700 hover:text-blue-900 hover:underline"
                    >
                        → View resolution history ({stats.resolved})
                    </Link>
                </div>
            </div>
        </div>
    );
}

function StatCard({ title, value, color, icon }: { title: string; value: number; color: string; icon: string }) {
    const colorClasses = {
        red: 'bg-red-50 text-red-700 border-red-200',
        yellow: 'bg-yellow-50 text-yellow-700 border-yellow-200',
        green: 'bg-green-50 text-green-700 border-green-200',
        blue: 'bg-blue-50 text-blue-700 border-blue-200',
    }[color];

    return (
        <div className={`rounded-lg border-2 p-6 ${colorClasses}`}>
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-sm font-medium opacity-80">{title}</p>
                    <p className="text-3xl font-bold mt-2">{value}</p>
                </div>
                <div className="text-4xl opacity-50">{icon}</div>
            </div>
        </div>
    );
}
