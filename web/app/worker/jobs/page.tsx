'use client';

import { useApp } from '@/context/AppContext';
import { formatGasWithUSD } from '@/lib/currency';

export default function WorkerJobsPage() {
    const { state, claimJob } = useApp();

    return (
        <div className="animate-in fade-in duration-500">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-white mb-2">Available Jobs</h2>
                <p className="text-slate-400">Browse and claim gigs to start earning.</p>
            </div>

            {state.isLoadingJobs ? (
                <div className="text-center py-8 text-slate-400">Loading...</div>
            ) : state.availableJobs.length > 0 ? (
                <div className="space-y-4">
                    {state.availableJobs.map((job) => {
                        const { gas, usd } = formatGasWithUSD(job.amount);
                        return (
                            <div
                                key={job.job_id}
                                className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 hover:border-slate-700 transition-colors"
                            >
                                <div className="flex justify-between items-start mb-3">
                                    <span className="text-cyan-400 font-semibold">Job #{job.job_id}</span>
                                    <div className="text-right">
                                        <div className="flex items-baseline gap-1 justify-end">
                                            <span className="text-green-400 font-bold text-lg">{gas} GAS</span>
                                        </div>
                                        <div className="text-slate-500 text-sm">≈ {usd}</div>
                                    </div>
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

                                <div className="flex justify-between items-center mt-4">
                                    <span className="text-slate-500 text-xs">Posted {new Date(job.created_at).toLocaleDateString()}</span>
                                    <button
                                        onClick={() => claimJob(job.job_id)}
                                        className="bg-green-600 hover:bg-green-500 text-white font-semibold px-4 py-2 rounded-lg transition-all active:scale-95"
                                    >
                                        Claim Job
                                    </button>
                                </div>
                            </div>
                        );
                    })}
                </div>
            ) : (
                <div className="text-center py-8 bg-slate-900/30 border border-slate-800 rounded-xl">
                    <p className="text-slate-400">No available jobs at the moment. Check back later!</p>
                </div>
            )}
        </div>
    );
}
