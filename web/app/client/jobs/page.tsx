'use client';

import { useApp } from '@/context/AppContext';

export default function ClientJobsPage() {
    const { state } = useApp();

    return (
        <div className="animate-in fade-in duration-500">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-white mb-2">My Jobs</h2>
                <p className="text-slate-400">Track and manage your posted gigs.</p>
            </div>

            {state.isLoadingJobs ? (
                <div className="text-center py-8 text-slate-400">Loading...</div>
            ) : state.clientJobs.length > 0 ? (
                <div className="space-y-4">
                    {state.clientJobs.map((job) => (
                        <div
                            key={job.job_id}
                            className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 hover:border-slate-700 transition-colors"
                        >
                            <div className="flex justify-between items-center mb-3">
                                <span className="text-cyan-400 font-semibold">Job #{job.job_id}</span>
                                <span
                                    className={`px-3 py-1 rounded-full text-xs ${job.status === 'OPEN'
                                            ? 'bg-green-500/20 text-green-400'
                                            : job.status === 'LOCKED'
                                                ? 'bg-yellow-500/20 text-yellow-400'
                                                : job.status === 'COMPLETED'
                                                    ? 'bg-blue-500/20 text-blue-400'
                                                    : 'bg-red-500/20 text-red-400'
                                        }`}
                                >
                                    {job.status}
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

                            {job.reference_photos.length > 0 && (
                                <div className="flex items-center mb-2">
                                    <svg className="h-4 w-4 text-slate-500 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                    </svg>
                                    <span className="text-slate-400 text-xs">{job.reference_photos.length} reference photo(s)</span>
                                </div>
                            )}

                            <div className="flex items-center gap-2">
                                <span className="text-cyan-400 font-semibold">{job.amount} GAS</span>
                                <span className="text-slate-500 text-xs">• Created {new Date(job.created_at).toLocaleDateString()}</span>
                            </div>

                            {job.tx_hash && (
                                <div className="flex items-center mt-2">
                                    <svg className="h-3 w-3 text-slate-500 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                                    </svg>
                                    <a
                                        href={`https://dora.coz.io/transaction/neo3/testnet/${job.tx_hash}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-cyan-500 hover:text-cyan-400 text-xs underline"
                                    >
                                        TX: {job.tx_hash.slice(0, 10)}...
                                    </a>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            ) : (
                <div className="text-center py-8 bg-slate-900/30 border border-slate-800 rounded-xl">
                    <p className="text-slate-400">No jobs yet. Create your first job!</p>
                </div>
            )}
        </div>
    );
}
