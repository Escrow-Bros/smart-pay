'use client';

import { ReactNode, useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Scale, LayoutDashboard, List, ArrowLeft, Menu, X } from 'lucide-react';

export default function TribunalLayout({ children }: { children: ReactNode }) {
    const pathname = usePathname();
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

            {/* Mobile Header */}
            <div className="md:hidden relative glass border-b border-slate-800 p-4 flex items-center justify-between sticky top-0 z-40">
                <div className="flex items-center gap-2">
                    <Scale className="w-5 h-5 text-purple-400" />
                    <span className="text-lg font-bold text-white">AI Tribunal</span>
                </div>
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

            {/* Mobile Menu Drawer */}
            <div className={`
                fixed top-0 right-0 z-[60] md:hidden
                transform transition-transform duration-300 ease-in-out
                ${isMobileMenuOpen ? 'translate-x-0' : 'translate-x-full'}
                w-64 bg-slate-900 border-l border-slate-800 h-screen
            `}>
                <div className="p-6 border-b border-slate-800">
                    <div className="flex items-center gap-2 mb-2">
                        <Scale className="w-5 h-5 text-purple-400" />
                        <span className="text-lg font-bold text-white">AI Tribunal</span>
                    </div>
                    <span className="px-2 py-0.5 bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs font-semibold rounded-full">
                        ADMIN
                    </span>
                </div>
                <div className="p-4 space-y-2">
                    {navItems.map((item) => {
                        const isActive = item.exact
                            ? pathname === item.href
                            : pathname?.startsWith(item.href) && pathname !== '/tribunal';

                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                onClick={() => setIsMobileMenuOpen(false)}
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${isActive
                                    ? 'bg-purple-500/20 text-purple-400'
                                    : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                                    }`}
                            >
                                <item.icon className="w-5 h-5" />
                                {item.label}
                            </Link>
                        );
                    })}
                </div>
                <div className="absolute bottom-8 left-0 right-0 px-4">
                    <Link
                        href="/"
                        onClick={() => setIsMobileMenuOpen(false)}
                        className="flex items-center justify-center gap-2 w-full bg-slate-700 hover:bg-slate-600 text-white py-2 px-4 rounded-xl transition-all text-sm"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Switch Role
                    </Link>
                </div>
            </div>

            {/* Desktop Header - Hidden on mobile */}
            <header className="hidden md:block relative glass border-b border-slate-800 sticky top-0 z-50">
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

            {/* Navigation - Horizontal scroll on mobile */}
            <nav className="hidden md:block relative glass border-b border-slate-800">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="flex space-x-1 overflow-x-auto">
                        {navItems.map((item) => {
                            const isActive = item.exact
                                ? pathname === item.href
                                : pathname?.startsWith(item.href) && pathname !== '/tribunal';

                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={`flex items-center gap-2 py-3 px-4 border-b-2 font-medium text-sm transition-all whitespace-nowrap ${isActive
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
