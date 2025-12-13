'use client';

import { ReactNode } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Scale, LayoutDashboard, List, ArrowLeft } from 'lucide-react';

export default function TribunalLayout({ children }: { children: ReactNode }) {
    const pathname = usePathname();

    const navItems = [
        { href: '/tribunal', label: 'Dashboard', icon: LayoutDashboard, exact: true },
        { href: '/tribunal/disputes', label: 'All Disputes', icon: List },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
            {/* Background Effects */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/4 -left-1/4 w-[600px] h-[600px] bg-purple-500/5 rounded-full blur-3xl"></div>
                <div className="absolute bottom-1/4 -right-1/4 w-[600px] h-[600px] bg-pink-500/5 rounded-full blur-3xl"></div>
            </div>

            {/* Header */}
            <header className="relative glass border-b border-slate-800 sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center">
                                    <Scale className="w-5 h-5 text-purple-400" />
                                </div>
                                <div>
                                    <h1 className="text-xl font-bold text-white">AI Tribunal</h1>
                                    <p className="text-xs text-slate-500">Dispute Resolution System</p>
                                </div>
                            </div>
                            <span className="px-3 py-1 bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs font-semibold rounded-full">
                                ADMIN
                            </span>
                        </div>
                        <Link
                            href="/"
                            className="flex items-center gap-2 text-sm text-slate-400 hover:text-white font-medium transition-colors"
                        >
                            <ArrowLeft className="w-4 h-4" />
                            Switch Role
                        </Link>
                    </div>
                </div>
            </header>

            {/* Navigation */}
            <nav className="relative glass border-b border-slate-800">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="flex space-x-1">
                        {navItems.map((item) => {
                            const isActive = item.exact
                                ? pathname === item.href
                                : pathname?.startsWith(item.href) && pathname !== '/tribunal';

                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={`flex items-center gap-2 py-3 px-4 border-b-2 font-medium text-sm transition-all ${isActive
                                            ? 'border-purple-500 text-purple-400 bg-purple-500/5'
                                            : 'border-transparent text-slate-400 hover:text-white hover:bg-slate-800/50'
                                        }`}
                                >
                                    <item.icon className="w-4 h-4" />
                                    {item.label}
                                </Link>
                            );
                        })}
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="relative max-w-7xl mx-auto px-4 py-8">
                {children}
            </main>
        </div>
    );
}
