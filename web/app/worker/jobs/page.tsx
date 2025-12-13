'use client';

import { useState } from 'react';
import { useApp } from '@/context/AppContext';
import { formatGasWithUSD } from '@/lib/currency';
import { MapPin, Clock, CheckCircle2, Loader2, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';

export default function WorkerJobsPage() {
    const { state, claimJob } = useApp();
    const [claimingJobId, setClaimingJobId] = useState<number | null>(null);
    const isAnyClaiming = claimingJobId !== null;

    const handleClaim = async (jobId: number) => {
        if (isAnyClaiming) return;
        setClaimingJobId(jobId);
        try {
            await claimJob(jobId);
        } catch (error) {
            toast.error('Failed to claim job. Please try again.');
        } finally {
            setClaimingJobId(null);
        }
    };

    return (
        <div className="animate-fade-in-up">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-white mb-2">Available Jobs</h2>
                <p className="text-slate-400">Browse and claim gigs to start earning.</p>
            </div>

            {state.isLoadingJobs ? (
                /* Loading Skeleton */
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div
                            key={i}
                            className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 animate-pulse"
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div className="loading-skeleton h-5 w-24 rounded"></div>
                                <div className="loading-skeleton h-6 w-20 rounded"></div>
                            </div>
                            <div className="loading-skeleton h-4 w-3/4 rounded mb-2"></div>
                            <div className="loading-skeleton h-4 w-1/2 rounded mb-4"></div>
                            <div className="flex justify-between items-center">
                                <div className="loading-skeleton h-4 w-32 rounded"></div>
                                <div className="loading-skeleton h-10 w-28 rounded-lg"></div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : state.availableJobs.length > 0 ? (
                <div className="space-y-4">
                    {state.availableJobs.map((job, index) => {
                        const { gas, usd } = formatGasWithUSD(job.amount);
                        const isClaiming = claimingJobId === job.job_id;
                        const staggerClass = ['stagger-1', 'stagger-2', 'stagger-3', 'stagger-4'][index % 4];

                        return (
                            <div
                                key={job.job_id}
                                className={`group relative glass border border-slate-800 rounded-2xl p-6 hover:border-cyan-500/50 hover-glow-cyan transition-all duration-300 animate-fade-in-up ${staggerClass}`}
                            >
                                {/* Gradient overlay on hover */}
                                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl" />

                                <div className="relative">
                                    <div className="flex justify-between items-start mb-3">
                                        <div className="flex items-center gap-2">
                                            <span className="text-cyan-400 font-semibold">Job #{job.job_id}</span>
                                            {job.verification_plan?.task_category && (
                                                <span className="px-2 py-0.5 bg-slate-700/50 rounded-full text-xs text-slate-400">
                                                    {job.verification_plan.task_category}
                                                </span>
                                            )}
                                        </div>
                                        <div className="text-right">
                                            <div className="flex items-baseline gap-1 justify-end">
                                                <Sparkles className="w-4 h-4 text-green-400" />
                                                <span className="text-green-400 font-bold text-xl">{gas} GAS</span>
                                            </div>
                                            <div className="text-slate-500 text-sm">≈ {usd}</div>
                                        </div>
                                    </div>

                                    <p className="text-slate-300 text-sm mb-4 leading-relaxed">{job.description}</p>

                                    {job.location && (
                                        <div className="flex items-center mb-3 text-slate-400">
                                            <MapPin className="h-4 w-4 mr-1.5 text-slate-500" />
                                            <span className="text-xs">{job.location}</span>
                                        </div>
                                    )}

                                    {/* Reference photo thumbnail */}
                                    {job.reference_photos && job.reference_photos.length > 0 && (
                                        <div className="flex gap-2 mb-4">
                                            {job.reference_photos.slice(0, 2).map((photo, i) => (
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
                                                        onError={(e) => { e.currentTarget.style.display = 'none'; }}
                                                    />
                                                </div>
                                            ))}
                                            {job.reference_photos.length > 2 && (
                                                <div className="w-16 h-16 rounded-lg bg-slate-800 flex items-center justify-center text-slate-500 text-xs">
                                                    +{job.reference_photos.length - 2}
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    <div className="flex justify-between items-center pt-3 border-t border-slate-800">
                                        <div className="flex items-center text-slate-500 text-xs">
                                            <Clock className="w-3.5 h-3.5 mr-1" />
                                            Posted {job.created_at && !isNaN(new Date(job.created_at).getTime())
                                                ? new Date(job.created_at).toLocaleDateString()
                                                : 'Unknown date'}
                                        </div>
                                        <button
                                            onClick={() => handleClaim(job.job_id)}
                                            disabled={isClaiming || isAnyClaiming}
                                            className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-semibold px-5 py-2.5 rounded-xl transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-green-500/20 hover:shadow-green-500/30"
                                        >
                                            {isClaiming ? (
                                                <>
                                                    <Loader2 className="w-4 h-4 animate-spin" />
                                                    Claiming...
                                                </>
                                            ) : (
                                                <>
                                                    <CheckCircle2 className="w-4 h-4" />
                                                    Claim Job
                                                </>
                                            )}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            ) : (
                <div className="text-center py-16 glass border border-slate-800 rounded-2xl">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-slate-800/50 flex items-center justify-center">
                        <Sparkles className="w-8 h-8 text-slate-600" />
                    </div>
                    <p className="text-slate-400 mb-2">No available jobs at the moment</p>
                    <p className="text-slate-600 text-sm">Check back later for new opportunities!</p>
                </div>
            )}
        </div>
    );
}
