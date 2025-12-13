'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useApp } from '@/context/AppContext';
import { formatGasWithUSD } from '@/lib/currency';
import { useState, useEffect } from 'react';
import { Search, Zap, Wallet, Gem, Menu, X, ArrowLeftRight, Clock } from 'lucide-react';

export default function WorkerLayout({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const { state } = useApp();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    // Prevent body scroll when mobile menu is open
    useEffect(() => {
        if (isMobileMenuOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
        return () => {
            document.body.style.overflow = '';
        };
    }, [isMobileMenuOpen]);

    const navItems = [
        { href: '/worker/jobs', label: 'Available Jobs', icon: Search },
        { href: '/worker/current', label: 'Current Jobs', icon: Zap },
        { href: '/worker/history', label: 'History', icon: Clock },
        { href: '/worker/wallet', label: 'Wallet', icon: Wallet },
    ];

    return (
        <div className="min-h-screen bg-slate-950 flex flex-col md:flex-row">
            {/* Mobile Header */}
            <div className="md:hidden bg-slate-900/50 border-b border-slate-800 p-4 flex items-center justify-between sticky top-0 z-40">
                <Link href="/" className="text-xl font-bold text-white flex items-center gap-2">
                    <Gem className="w-5 h-5 text-green-400" />
                    GigSmartPay
                </Link>
                <button
                    onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                    className="text-white p-2 hover:bg-slate-800 rounded-lg transition-colors"
                    aria-label="Toggle menu"
                >
                    {isMobileMenuOpen ? (
                        <X className="w-6 h-6" />
                    ) : (
                        <Menu className="w-6 h-6" />
                    )}
                </button>
            </div>

            {/* Mobile Overlay */}
            {isMobileMenuOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-50 md:hidden"
                    onClick={() => setIsMobileMenuOpen(false)}
                />
            )}

            {/* Sidebar - Desktop always visible, Mobile toggleable */}
            <div className={`
                fixed md:static inset-0 z-[60] md:z-auto
                transform transition-transform duration-300 ease-in-out
                ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
                w-64 md:w-64 bg-slate-900/95 md:bg-slate-900/50 md:border-r border-slate-800 flex flex-col
                md:min-h-screen h-[100dvh]
            `}>
                <div className="p-6 border-b border-slate-800">
                    <Link href="/" className="text-2xl font-bold text-white flex items-center gap-2">
                        <Gem className="w-6 h-6 text-green-400" />
                        GigSmartPay
                    </Link>
                    <div className="flex items-center gap-2 mt-2">
                        <p className="text-sm text-slate-500">Worker Mode</p>
                        <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs font-semibold rounded">
                            DEMO
                        </span>
                    </div>
                </div>

                <div className="flex-1 p-4 overflow-y-auto">
                    <nav className="space-y-2">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    onClick={() => setIsMobileMenuOpen(false)}
                                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${pathname === item.href
                                        ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                                        : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-300'
                                        }`}
                                >
                                    <Icon className="w-5 h-5" />
                                    <span className="font-medium">{item.label}</span>
                                </Link>
                            );
                        })}
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
                        <p className="text-xs text-slate-400 mt-1">≈ {formatGasWithUSD(state.walletBalance).usd}</p>
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
                        <ArrowLeftRight className="w-4 h-4" />
                        Switch Role
                    </Link>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 overflow-auto w-full">
                <div className="max-w-full sm:max-w-2xl md:max-w-4xl lg:max-w-6xl xl:max-w-7xl mx-auto p-6 sm:p-8 md:p-10 lg:p-12">
                    {children}
                </div>
            </div>
        </div>
    );
}
