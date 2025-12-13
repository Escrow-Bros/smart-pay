'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import type { DisputeDict } from '@/lib/types';
import { Scale, Clock, Search, CheckCircle2, AlertTriangle, ChevronRight, RefreshCw, Loader2 } from 'lucide-react';

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
    const [isRefreshing, setIsRefreshing] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/disputes`);
            const data = await response.json();

            if (data.success) {
                const disputes = data.disputes as DisputeDict[];

                const pending = disputes.filter(d => d.status === 'PENDING').length;
                const under_review = disputes.filter(d => d.status === 'UNDER_REVIEW').length;
                const resolved = disputes.filter(d => d.status === 'RESOLVED').length;

                setStats({ pending, under_review, resolved, total: disputes.length });

                const unresolved = disputes
                    .filter(d => d.status !== 'RESOLVED')
                    .slice(0, 5);
                setRecentDisputes(unresolved);
            }
        } catch (error) {
            console.error('Failed to fetch disputes:', error);
        } finally {
            setIsLoading(false);
            setIsRefreshing(false);
        }
    };

    const handleRefresh = () => {
        setIsRefreshing(true);
        fetchData();
    };

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center h-64 animate-fade-in-up">
                <Loader2 className="w-8 h-8 text-purple-400 animate-spin mb-4" />
                <p className="text-slate-400">Loading tribunal dashboard...</p>
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-fade-in-up">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">AI Tribunal Dashboard</h1>
                    <p className="text-slate-400">Review and resolve disputes with AI assistance</p>
                </div>
                <button
                    onClick={handleRefresh}
                    disabled={isRefreshing}
                    className="flex items-center gap-2 px-4 py-2 bg-purple-500/10 border border-purple-500/30 rounded-xl text-purple-400 hover:bg-purple-500/20 transition-all disabled:opacity-50"
                >
                    <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                    Refresh
                </button>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <StatCard
                    title="Pending Review"
                    value={stats.pending}
                    color="red"
                    icon={<Clock className="w-6 h-6" />}
                />
                <StatCard
                    title="Under Review"
                    value={stats.under_review}
                    color="yellow"
                    icon={<Search className="w-6 h-6" />}
                />
                <StatCard
                    title="Resolved"
                    value={stats.resolved}
                    color="green"
                    icon={<CheckCircle2 className="w-6 h-6" />}
                />
                <StatCard
                    title="Total Disputes"
                    value={stats.total}
                    color="purple"
                    icon={<Scale className="w-6 h-6" />}
                />
            </div>

            {/* Recent Disputes */}
            <div className="glass border border-slate-800 rounded-2xl overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <AlertTriangle className="w-5 h-5 text-yellow-400" />
                        <h2 className="text-lg font-semibold text-white">Recent Unresolved Disputes</h2>
                    </div>
                    <Link
                        href="/tribunal/disputes"
                        className="flex items-center gap-1 text-sm text-purple-400 hover:text-purple-300 font-medium transition-colors"
                    >
                        View All
                        <ChevronRight className="w-4 h-4" />
                    </Link>
                </div>

                {recentDisputes.length === 0 ? (
                    <div className="px-6 py-16 text-center">
                        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-green-500/10 flex items-center justify-center">
                            <CheckCircle2 className="w-8 h-8 text-green-400" />
                        </div>
                        <h3 className="text-lg font-semibold text-white mb-2">All Clear!</h3>
                        <p className="text-slate-400">No pending disputes. AI is doing its job.</p>
                    </div>
                ) : (
                    <div className="divide-y divide-slate-800">
                        {recentDisputes.map((dispute, index) => (
                            <Link
                                key={dispute.dispute_id}
                                href={`/tribunal/disputes/${dispute.dispute_id}`}
                                className={`group block px-6 py-5 hover:bg-slate-800/50 transition-all animate-fade-in-up stagger-${index + 1}`}
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-3 mb-2">
                                            <span className={`flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-full ${dispute.status === 'PENDING'
                                                    ? 'bg-red-500/20 text-red-400'
                                                    : 'bg-yellow-500/20 text-yellow-400'
                                                }`}>
                                                {dispute.status === 'PENDING' ? (
                                                    <Clock className="w-3 h-3" />
                                                ) : (
                                                    <Search className="w-3 h-3" />
                                                )}
                                                {dispute.status}
                                            </span>
                                            <span className="text-sm text-slate-500">Job #{dispute.job_id}</span>
                                            <span className="text-xs text-slate-600">• {dispute.amount} GAS</span>
                                        </div>
                                        <h3 className="text-sm font-medium text-white truncate mb-1 group-hover:text-purple-300 transition-colors">
                                            {dispute.description || 'No description'}
                                        </h3>
                                        <p className="text-sm text-slate-400 line-clamp-1">
                                            {dispute.reason}
                                        </p>
                                        <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                                            <span>Raised: {new Date(dispute.raised_at).toLocaleDateString()}</span>
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

            {/* Quick Actions */}
            <div className="glass border border-purple-500/30 rounded-2xl p-6 bg-gradient-to-r from-purple-500/5 to-transparent">
                <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                    <Scale className="w-4 h-4 text-purple-400" />
                    Quick Actions
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <Link
                        href="/tribunal/disputes?status=PENDING"
                        className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl hover:bg-red-500/10 border border-slate-700 hover:border-red-500/50 transition-all group"
                    >
                        <div className="flex items-center gap-3">
                            <Clock className="w-5 h-5 text-red-400" />
                            <span className="text-sm text-slate-300">Review Pending</span>
                        </div>
                        <span className="text-lg font-bold text-red-400">{stats.pending}</span>
                    </Link>
                    <Link
                        href="/tribunal/disputes?status=UNDER_REVIEW"
                        className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl hover:bg-yellow-500/10 border border-slate-700 hover:border-yellow-500/50 transition-all group"
                    >
                        <div className="flex items-center gap-3">
                            <Search className="w-5 h-5 text-yellow-400" />
                            <span className="text-sm text-slate-300">Continue Reviews</span>
                        </div>
                        <span className="text-lg font-bold text-yellow-400">{stats.under_review}</span>
                    </Link>
                    <Link
                        href="/tribunal/disputes?status=RESOLVED"
                        className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl hover:bg-green-500/10 border border-slate-700 hover:border-green-500/50 transition-all group"
                    >
                        <div className="flex items-center gap-3">
                            <CheckCircle2 className="w-5 h-5 text-green-400" />
                            <span className="text-sm text-slate-300">View History</span>
                        </div>
                        <span className="text-lg font-bold text-green-400">{stats.resolved}</span>
                    </Link>
                </div>
            </div>
        </div>
    );
}

function StatCard({ title, value, color, icon }: { title: string; value: number; color: string; icon: React.ReactNode }) {
    const colorClasses: Record<string, string> = {
        red: 'from-red-500/10 to-transparent border-red-500/30 text-red-400',
        yellow: 'from-yellow-500/10 to-transparent border-yellow-500/30 text-yellow-400',
        green: 'from-green-500/10 to-transparent border-green-500/30 text-green-400',
        purple: 'from-purple-500/10 to-transparent border-purple-500/30 text-purple-400',
    };

    return (
        <div className={`glass rounded-2xl border p-6 bg-gradient-to-br ${colorClasses[color]}`}>
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-sm text-slate-400 mb-1">{title}</p>
                    <p className="text-3xl font-bold">{value}</p>
                </div>
                <div className="opacity-60">{icon}</div>
            </div>
        </div>
    );
}
