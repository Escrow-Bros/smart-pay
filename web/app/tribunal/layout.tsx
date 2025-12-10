'use client';

import { ReactNode } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function TribunalLayout({ children }: { children: ReactNode }) {
    const pathname = usePathname();

    const navItems = [
        { href: '/tribunal', label: 'Dashboard', exact: true },
        { href: '/tribunal/disputes', label: 'All Disputes' },
    ];

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">⚖️ Tribunal</h1>
                                <p className="text-sm text-gray-600">Dispute Resolution System</p>
                            </div>
                            <span className="px-3 py-1 bg-purple-100 text-purple-700 text-xs font-semibold rounded-full">
                                ADMIN MODE
                            </span>
                        </div>
                        <Link 
                            href="/"
                            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                        >
                            ← Switch Role
                        </Link>
                    </div>
                </div>
            </header>

            {/* Navigation */}
            <nav className="bg-white border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="flex space-x-8">
                        {navItems.map((item) => {
                            const isActive = item.exact 
                                ? pathname === item.href
                                : pathname?.startsWith(item.href);
                            
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                                        isActive
                                            ? 'border-blue-500 text-blue-600'
                                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                                >
                                    {item.label}
                                </Link>
                            );
                        })}
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 py-8">
                {children}
            </main>
        </div>
    );
}
