'use client';

import { useState } from 'react';
import { useApp } from '@/context/AppContext';

export default function WalletPage() {
    const { state, fetchData } = useApp();
    const [isRefreshing, setIsRefreshing] = useState(false);

    const handleRefresh = async () => {
        setIsRefreshing(true);
        await fetchData();
        setTimeout(() => setIsRefreshing(false), 500);
    };

    return (
        <div className="animate-in fade-in duration-500">
            <div className="mb-8 flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold text-white mb-2">Wallet</h2>
                    <p className="text-slate-400">
                        View your wallet details and balance.
                    </p>
                </div>
                <button
                    onClick={handleRefresh}
                    disabled={isRefreshing}
                    className="flex items-center gap-2 bg-cyan-500 hover:bg-cyan-600 text-white py-2 px-4 rounded-xl transition-all disabled:opacity-50"
                >
                    <svg className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Refresh
                </button>
            </div>

            <div className="bg-gradient-to-br from-slate-900/80 to-slate-950/80 border border-slate-700 rounded-3xl max-w-2xl mx-auto">
                <div className="text-center p-12">
                    <div className="h-16 w-16 mx-auto mb-6 text-cyan-400" dangerouslySetInnerHTML={{
                        __html: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" /></svg>`
                    }} />

                    <div className="mb-6">
                        <p className="text-xs text-slate-500 mb-1">Connected as</p>
                        <p className="text-xl font-semibold text-white">{state.currentUser || 'Guest'}</p>
                    </div>

                    <div className="mb-8">
                        <p className="text-xs text-slate-500 mb-2">Wallet Address</p>
                        <div className="flex items-center justify-center">
                            <code className="text-sm text-cyan-400 bg-slate-900/50 px-4 py-2 rounded-lg font-mono">
                                {state.walletAddress}
                            </code>
                        </div>
                    </div>

                    <div>
                        <p className="text-xs text-slate-500 mb-2">Balance</p>
                        <div className="flex items-baseline justify-center">
                            <span className="text-5xl font-bold text-cyan-400">{state.walletBalance.toFixed(2)}</span>
                            <span className="text-2xl text-slate-400 ml-2">GAS</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
