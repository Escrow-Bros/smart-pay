'use client';

import { useState } from 'react';
import { useApp } from '@/context/AppContext';
import { formatGasWithUSD } from '@/lib/currency';

export default function WorkerWalletPage() {
    const { state, fetchData } = useApp();
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [showAddressTooltip, setShowAddressTooltip] = useState(false);

    const handleRefresh = async () => {
        setIsRefreshing(true);
        await fetchData();
        setTimeout(() => setIsRefreshing(false), 500);
    };

    const handleCopyAddress = async () => {
        try {
            await navigator.clipboard.writeText(state.walletAddress);
            setShowAddressTooltip(true);
            setTimeout(() => setShowAddressTooltip(false), 2000);
        } catch (error) {
            console.error('Failed to copy address:', error);
        }
    };

    const { gas, usd } = formatGasWithUSD(state.walletBalance);
    const earnedFormatted = state.workerStats ? formatGasWithUSD(state.workerStats.total_earned) : { gas: '0.00', usd: '$0.00' };

    return (
        <div className="animate-in fade-in duration-500">
            <div className="mb-8 flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold text-white mb-2">Wallet</h2>
                    <p className="text-slate-400">Track your earnings and manage your funds.</p>
                </div>
                <button
                    onClick={handleRefresh}
                    disabled={isRefreshing}
                    className="flex items-center gap-2 bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded-xl transition-all disabled:opacity-50"
                >
                    <svg className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Refresh
                </button>
            </div>

            {/* Main Wallet Card */}
            <div className="bg-gradient-to-br from-green-900/20 via-slate-900/80 to-slate-950/80 border border-green-500/30 rounded-3xl max-w-3xl mx-auto shadow-2xl shadow-green-900/20">
                <div className="p-8">
                    {/* Icon and User Info */}
                    <div className="flex items-center justify-between mb-8">
                        <div className="flex items-center gap-4">
                            <div className="h-16 w-16 bg-green-500/20 rounded-2xl flex items-center justify-center">
                                <svg className="h-8 w-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                                </svg>
                            </div>
                            <div>
                                <p className="text-xs text-slate-500 mb-1">Connected as</p>
                                <p className="text-xl font-semibold text-white">{state.currentUser}</p>
                            </div>
                        </div>
                        <div className="px-4 py-2 bg-green-500/10 border border-green-500/30 rounded-xl">
                            <p className="text-xs text-green-400 font-medium">WORKER</p>
                        </div>
                    </div>

                    {/* Wallet Address */}
                    <div className="mb-8">
                        <p className="text-xs text-slate-500 mb-2">Wallet Address</p>
                        <div className="relative group">
                            <div className="flex items-center justify-between bg-slate-900/80 border border-slate-700 rounded-xl px-4 py-3 hover:border-green-500/50 transition-all">
                                <code className="text-sm text-green-400 font-mono flex-1 overflow-hidden truncate">
                                    {state.walletAddress}
                                </code>
                                <button
                                    onClick={handleCopyAddress}
                                    className="ml-3 p-2 hover:bg-slate-800 rounded-lg transition-colors flex-shrink-0"
                                    title="Copy address"
                                >
                                    {showAddressTooltip ? (
                                        <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                    ) : (
                                        <svg className="w-4 h-4 text-slate-400 group-hover:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                        </svg>
                                    )}
                                </button>
                            </div>
                            {showAddressTooltip && (
                                <div className="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 bg-green-500 text-white text-xs px-3 py-1 rounded-lg whitespace-nowrap z-10">
                                    Copied to clipboard!
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Balance Display */}
                    <div className="bg-slate-900/50 border border-slate-700 rounded-2xl p-6 mb-6">
                        <p className="text-xs text-slate-500 mb-3 uppercase tracking-wider">Current Balance</p>
                        <div className="flex items-baseline mb-2">
                            <span className="text-5xl font-bold text-green-400">{gas}</span>
                            <span className="text-2xl text-slate-400 ml-3">GAS</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-2xl font-semibold text-slate-300">{usd}</span>
                            <span className="text-xs text-slate-500 bg-slate-800 px-2 py-1 rounded">
                                MAINNET VALUE
                            </span>
                        </div>
                    </div>

                    {/* Worker Stats */}
                    {state.workerStats && (
                        <div className="grid grid-cols-3 gap-4">
                            <div className="bg-slate-900/50 border border-slate-700 rounded-xl p-4">
                                <svg className="w-6 h-6 text-slate-500 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                </svg>
                                <p className="text-xs text-slate-500 mb-1">Total Jobs</p>
                                <p className="text-2xl font-bold text-white">{state.workerStats.total_jobs}</p>
                            </div>
                            <div className="bg-slate-900/50 border border-slate-700 rounded-xl p-4">
                                <svg className="w-6 h-6 text-green-500 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <p className="text-xs text-slate-500 mb-1">Completed</p>
                                <p className="text-2xl font-bold text-green-400">{state.workerStats.completed_jobs}</p>
                            </div>
                            <div className="bg-slate-900/50 border border-slate-700 rounded-xl p-4">
                                <svg className="w-6 h-6 text-yellow-500 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                </svg>
                                <p className="text-xs text-slate-500 mb-1">Success Rate</p>
                                <p className="text-2xl font-bold text-yellow-400">
                                    {state.workerStats.total_jobs > 0 
                                        ? Math.round((state.workerStats.completed_jobs / state.workerStats.total_jobs) * 100)
                                        : 0}%
                                </p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Earnings Section */}
                {state.workerStats && (
                    <div className="border-t border-slate-700/50 p-6">
                        <div className="bg-gradient-to-r from-green-900/30 to-green-800/20 border border-green-500/30 rounded-2xl p-6">
                            <div className="flex items-center gap-3 mb-3">
                                <div className="p-2 bg-green-500/20 rounded-lg">
                                    <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                </div>
                                <p className="text-xs text-slate-400 uppercase tracking-wider">Total Earned</p>
                            </div>
                            <div className="flex items-baseline mb-1">
                                <span className="text-3xl font-bold text-green-400">{earnedFormatted.gas}</span>
                                <span className="text-lg text-slate-400 ml-2">GAS</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-xl font-semibold text-slate-300">{earnedFormatted.usd}</span>
                                <span className="text-xs text-slate-500">≈ USD</span>
                            </div>
                        </div>
                    </div>
                )}

                {/* Network Info */}
                <div className="border-t border-slate-700/50 p-6 grid grid-cols-2 gap-4">
                    <div className="bg-slate-900/50 rounded-xl p-4 text-center">
                        <svg className="w-6 h-6 text-slate-500 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                        </svg>
                        <p className="text-xs text-slate-400">Network</p>
                        <p className="text-sm font-semibold text-white mt-1">Neo N3 Testnet</p>
                    </div>
                    <div className="bg-slate-900/50 rounded-xl p-4 text-center">
                        <svg className="w-6 h-6 text-slate-500 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <p className="text-xs text-slate-400">Status</p>
                        <p className="text-sm font-semibold text-green-400 mt-1">Active</p>
                    </div>
                </div>
            </div>

            {/* Additional Info Card */}
            <div className="mt-6 max-w-3xl mx-auto">
                <div className="bg-slate-900/30 border border-slate-800 rounded-xl p-6">
                    <div className="flex items-start gap-3">
                        <svg className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div>
                            <p className="text-sm font-medium text-white mb-1">Testnet Experiment</p>
                            <p className="text-sm text-slate-400 leading-relaxed">
                                This project runs on Neo N3 Testnet for experimentation. USD values are based on real-time mainnet prices. Keep completing jobs to build your reputation!
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
