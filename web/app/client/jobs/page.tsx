'use client';

import type { ReactNode } from 'react';
import Link from 'next/link';
import { useApp } from '@/context/AppContext';
import { formatGasWithUSD } from '@/lib/currency';
import { MapPin, Image, ExternalLink, Clock, Plus, CheckCircle2, Loader2, AlertCircle, Lock } from 'lucide-react';

export default function ClientJobsPage() {
    const { state } = useApp();

    const getStatusConfig = (status: string) => {
        const configs: Record<string, { bg: string; text: string; icon: ReactNode }> = {
            'OPEN': { bg: 'bg-green-500/20', text: 'text-green-400', icon: <Clock className="w-3 h-3" /> },
            'LOCKED': { bg: 'bg-yellow-500/20', text: 'text-yellow-400', icon: <Lock className="w-3 h-3" /> },
            'COMPLETED': { bg: 'bg-blue-500/20', text: 'text-blue-400', icon: <CheckCircle2 className="w-3 h-3" /> },
            'DISPUTED': { bg: 'bg-red-500/20', text: 'text-red-400', icon: <AlertCircle className="w-3 h-3" /> },
            'REFUNDED': { bg: 'bg-gray-500/20', text: 'text-gray-400', icon: <CheckCircle2 className="w-3 h-3" /> },
        };
        return configs[status] || configs['OPEN'];
    };

    return (
        <div className="animate-fade-in-up">
            <div className="mb-8 flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold text-white mb-2">My Jobs</h2>
                    <p className="text-slate-400">Track and manage your posted gigs.</p>
                </div>
                <Link
                    href="/client/create"
                    className="flex items-center gap-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold px-5 py-2.5 rounded-xl transition-all shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30"
                >
                    <Plus className="w-4 h-4" />
                    New Job
                </Link>
            </div>

            {state.isLoadingJobs ? (
                /* Loading Skeleton */
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div
                            key={i}
                            className="glass border border-slate-800 rounded-2xl p-6 animate-pulse"
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div className="loading-skeleton h-5 w-24 rounded"></div>
                                <div className="loading-skeleton h-6 w-20 rounded-full"></div>
                            </div>
                            <div className="loading-skeleton h-4 w-3/4 rounded mb-2"></div>
                            <div className="loading-skeleton h-4 w-1/2 rounded mb-4"></div>
                            <div className="flex gap-2">
                                <div className="loading-skeleton h-16 w-16 rounded-lg"></div>
                                <div className="loading-skeleton h-16 w-16 rounded-lg"></div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : state.clientJobs.length > 0 ? (
                <div className="space-y-4">
                    {state.clientJobs.map((job, index) => {
                        const { gas, usd } = formatGasWithUSD(job.amount);
                        const statusConfig = getStatusConfig(job.status);

                        return (
                            <div
                                key={job.job_id}
                                className={`group relative glass border border-slate-800 rounded-2xl p-6 hover:border-cyan-500/50 hover-glow-cyan transition-all duration-300 animate-fade-in-up stagger-${(index % 4) + 1}`}
                            >
                                {/* Gradient overlay on hover */}
                                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl" />

                                <div className="relative">
                                    <div className="flex justify-between items-start mb-3">
                                        <div className="flex items-center gap-3">
                                            <span className="text-cyan-400 font-semibold">Job #{job.job_id}</span>
                                            {job.worker_address && (
                                                <span className="text-xs text-slate-500">
                                                    Worker: {job.worker_address.slice(0, 6)}...{job.worker_address.slice(-4)}
                                                </span>
                                            )}
                                        </div>
                                        <span className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${statusConfig.bg} ${statusConfig.text}`}>
                                            {statusConfig.icon}
                                            {job.status}
                                        </span>
                                    </div>

                                    <p className="text-slate-300 text-sm mb-4 leading-relaxed">{job.description}</p>

                                    {job.location && (
                                        <div className="flex items-center mb-3 text-slate-400">
                                            <MapPin className="h-4 w-4 mr-1.5 text-slate-500" />
                                            <span className="text-xs">{job.location}</span>
                                        </div>
                                    )}

                                    {/* Reference photos */}
                                    {job.reference_photos && job.reference_photos.length > 0 && (
                                        <div className="mb-4">
                                            <div className="flex items-center gap-2 mb-2">
                                                <Image className="w-4 h-4 text-slate-500" />
                                                <span className="text-xs text-slate-400">{job.reference_photos.length} reference photo(s)</span>
                                            </div>
                                            <div className="flex gap-2">
                                                {job.reference_photos.slice(0, 3).map((photo, i) => (
                                                    <div
                                                        key={i}
                                                        className="w-16 h-16 rounded-lg overflow-hidden border border-slate-700"
                                                    >
                                                        <img
                                                            src={photo}
                                                            alt={`Reference ${i + 1}`}
                                                            loading="lazy"
                                                            decoding="async"
                                                            referrerPolicy="no-referrer"
                                                            className="w-full h-full object-cover"
                                                        />
                                                    </div>
                                                ))}
                                                {job.reference_photos.length > 3 && (
                                                    <div className="w-16 h-16 rounded-lg bg-slate-800 flex items-center justify-center text-slate-500 text-xs">
                                                        +{job.reference_photos.length - 3}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    )}

                                    {/* Proof photos if submitted */}
                                    {job.proof_photos && job.proof_photos.length > 0 && (
                                        <div className="mb-4 p-3 bg-green-500/10 border border-green-500/30 rounded-xl">
                                            <div className="flex items-center gap-2 mb-2">
                                                <CheckCircle2 className="w-4 h-4 text-green-400" />
                                                <span className="text-xs text-green-400 font-medium">Proof Submitted ({job.proof_photos.length} photos)</span>
                                            </div>
                                            <div className="flex gap-2">
                                                {job.proof_photos.slice(0, 3).map((photo, i) => (
                                                    <div
                                                        key={i}
                                                        className="w-14 h-14 rounded-lg overflow-hidden border border-green-500/30"
                                                    >
                                                        <img
                                                            src={photo}
                                                            alt={`Proof ${i + 1}`}
                                                            loading="lazy"
                                                            decoding="async"
                                                            referrerPolicy="no-referrer"
                                                            className="w-full h-full object-cover"
                                                        />
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    <div className="flex justify-between items-center pt-3 border-t border-slate-800">
                                        <div className="flex items-center gap-4">
                                            <div className="flex items-baseline gap-1">
                                                <span className="text-cyan-400 font-semibold text-lg">{gas} GAS</span>
                                                <span className="text-slate-500 text-sm">≈ {usd}</span>
                                            </div>
                                            <div className="flex items-center text-slate-500 text-xs">
                                                <Clock className="w-3.5 h-3.5 mr-1" />
                                                {new Date(job.created_at).toLocaleDateString()}
                                            </div>
                                        </div>

                                        {job.tx_hash && (
                                            <a
                                                href={`https://dora.coz.io/transaction/neo3/testnet/${job.tx_hash}`}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="flex items-center gap-1.5 text-cyan-500 hover:text-cyan-400 text-xs transition-colors"
                                            >
                                                <ExternalLink className="w-3.5 h-3.5" />
                                                View TX
                                            </a>
                                        )}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            ) : (
                <div className="text-center py-16 glass border border-slate-800 rounded-2xl">
                    <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-cyan-500/10 to-blue-500/10 flex items-center justify-center">
                        <Plus className="w-10 h-10 text-cyan-400" />
                    </div>
                    <h3 className="text-xl font-semibold text-white mb-2">No Jobs Posted Yet</h3>
                    <p className="text-slate-400 mb-6 max-w-sm mx-auto">
                        Create your first job posting and get work done by verified workers.
                    </p>
                    <Link
                        href="/client/create"
                        className="inline-flex items-center gap-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold px-6 py-3 rounded-xl transition-all shadow-lg shadow-cyan-500/20 active:scale-95"
                    >
                        <Plus className="w-5 h-5" />
                        Create Your First Job
                    </Link>
                </div>
            )}
        </div>
    );
}