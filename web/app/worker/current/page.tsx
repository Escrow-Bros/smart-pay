'use client';

import { useApp } from '@/context/AppContext';

export default function WorkerCurrentJobPage() {
    const { state } = useApp();

    if (!state.currentJob) {
        return (
            <div className="animate-in fade-in duration-500">
                <div className="mb-8">
                    <h2 className="text-3xl font-bold text-white mb-2">Current Job</h2>
                    <p className="text-slate-400">Your active job assignment.</p>
                </div>

                <div className="text-center py-12 bg-slate-900/30 border border-slate-800 rounded-xl">
                    <p className="text-slate-400 mb-2">No active job</p>
                    <p className="text-slate-500 text-sm">Claim a job from the Available Jobs page to start working.</p>
                </div>
            </div>
        );
    }

    const job = state.currentJob;

    return (
        <div className="animate-in fade-in duration-500">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text_white mb-2">Current Job</h2>
                <p className="text-slate-400">Complete your work and submit proof to get paid.</p>
            </div>

            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-8">
                <div className="mb-6">
                    <div className="flex justify-between items-start mb-4">
                        <span className="text-cyan-400 font-semibold text-lg">Job #{job.job_id}</span>
                        <span className="text-green-400 font-bold text-2xl">{job.amount} GAS</span>
                    </div>

                    <p className="text-slate-200 mb-4">{job.description}</p>

                    {job.location && (
                        <div className="flex items-center mb-3">
                            <svg className="h-5 w-5 text-slate-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                            </svg>
                            <span className="text-slate-300">{job.location}</span>
                        </div>
                    )}
                </div>

                <div className="border-t border-slate-700 pt-6">
                    <h3 className="text-white font-semibold mb-3">Submit Proof of Completion</h3>
                    <p className="text-slate-400 text-sm mb-4">
                        Upload photos showing the completed work to receive payment.
                    </p>

                    <div className="border-2 border-dashed border-slate-700 rounded-xl p-8 text-center hover:border-cyan-500/50 transition-all cursor-pointer">
                        <svg className="h-12 w-12 text-slate-500 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <p className="text-slate-400">Upload proof photos</p>
                    </div>

                    <button className="w-full mt-4 bg-green-600 hover:bg-green-500 text-white font-semibold py-3 rounded-xl transition-all active:scale-95">
                        Submit for Verification
                    </button>
                </div>
            </div>
        </div>
    );
}
