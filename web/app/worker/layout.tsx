'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useApp } from '@/context/AppContext';

export default function WorkerLayout({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const { state } = useApp();

    const navItems = [
        { href: '/worker/jobs', label: 'Available Jobs', icon: '🔍' },
        { href: '/worker/current', label: 'Current Jobs', icon: '⚡' },
        { href: '/worker/wallet', label: 'Wallet', icon: '💼' },
    ];

    return (
        <div className="min-h-screen bg-slate-950 flex">
            {/* Sidebar */}
            <div className="w-64 bg-slate-900/50 border-r border-slate-800 flex flex-col">
                <div className="p-6 border-b border-slate-800">
                    <Link href="/" className="text-2xl font-bold text-white flex items-center gap-2">
                        🛡️ GigShield
                    </Link>
                    <p className="text-sm text-slate-500 mt-1">Worker Mode</p>
                </div>

                <div className="flex-1 p-4">
                    <nav className="space-y-2">
                        {navItems.map((item) => (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${pathname === item.href
                                    ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-300'
                                    }`}
                            >
                                <span className="text-xl">{item.icon}</span>
                                <span className="font-medium">{item.label}</span>
                            </Link>
                        ))}
                    </nav>
                </div>

                <div className="p-4 border-t border-slate-800">
                    <div className="bg-slate-800/50 rounded-xl p-4 mb-3">
                        <p className="text-xs text-slate-500 mb-2">Connected as</p>
                        <p className="text-sm text-white font-semibold mb-3">{state.currentUser || 'Guest'}</p>
                        <p className="text-xs text-slate-500 mb-1">Balance</p>
                        <p className="text-2xl font-bold text-green-400">
                            {state.walletBalance.toFixed(2)} <span className="text-sm text-slate-500">GAS</span>
                        </p>
                        {state.workerStats && (
                            <div className="mt-3 pt-3 border-t border-slate-700/50">
                                <p className="text-xs text-slate-400">
                                    {state.workerStats.completed_jobs} jobs completed
                                </p>
                            </div>
                        )}
                    </div>
                    <Link
                        href="/"
                        className="flex items-center justify-center gap-2 w-full bg-slate-700 hover:bg-slate-600 text-white py-2 px-4 rounded-xl transition-all text-sm"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                        </svg>
                        Switch Role
                    </Link>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 overflow-auto">
                <div className="max-w-5xl mx-auto p-8">
                    {children}
                </div>
            </div>
        </div>
    );
}
