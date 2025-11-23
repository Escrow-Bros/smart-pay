'use client';

import { useApp } from '@/context/AppContext';

export default function WorkerWalletPage() {
    const { state } = useApp();

    return (
        <div className="animate-in fade-in duration-500">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-white mb-2">Wallet</h2>
                <p className="text-slate-400">View your earnings and wallet details.</p>
            </div>

            <div className="bg-gradient-to-br from-slate-900/80 to-slate-950/80 border border-slate-700 rounded-3xl max-w-2xl mx-auto">
                <div className="text-center p-12">
                    <div className="h-16 w-16 mx-auto mb-6 text-green-400" dangerouslySetInnerHTML={{
                        __html: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" /></svg>`
                    }} />

                    <div className="mb-6">
                        <p className="text-xs text-slate-500 mb-1">Connected as</p>
                        <p className="text-xl font-semibold text-white">{state.currentUser}</p>
                    </div>

                    <div className="mb-8">
                        <p className="text-xs text-slate-500 mb-2">Wallet Address</p>
                        <div className="flex items-center justify-center">
                            <code className="text-sm text-green-400 bg-slate-900/50 px-4 py-2 rounded-lg font-mono truncate max-w-full">
                                {state.walletAddress}
                            </code>
                        </div>
                    </div>

                    <div className="mb-6">
                        <p className="text-xs text-slate-500 mb-2">Balance</p>
                        <div className="flex items-baseline justify-center">
                            <span className="text-5xl font-bold text-green-400">{state.walletBalance.toFixed(2)}</span>
                            <span className="text-2xl text-slate-400 ml-2">GAS</span>
                        </div>
                    </div>

                    {state.workerStats && (
                        <div className="border-t border-slate-700/50 pt-6">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <p className="text-xs text-slate-500 mb-1">Jobs Completed</p>
                                    <p className="text-2xl font-bold text-white">{state.workerStats.completed_jobs}</p>
                                </div>
                                <div>
                                    <p className="text-xs text-slate-500 mb-1">Total Earned</p>
                                    <p className="text-2xl font-bold text-green-400">{state.workerStats.total_earned} GAS</p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
