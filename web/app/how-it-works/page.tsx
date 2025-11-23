'use client';

import Link from 'next/link';
import Image from 'next/image';

export default function HowItWorks() {
    return (
        <div className="min-h-screen bg-slate-950 text-white p-4 md:p-8">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-12">
                    <Link href="/" className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                        GigSmartPay 🛡️
                    </Link>
                    <Link
                        href="/"
                        className="px-6 py-2 bg-slate-900 border border-slate-700 rounded-full hover:border-cyan-500 transition-colors text-sm"
                    >
                        ← Back to Home
                    </Link>
                </div>

                <div className="text-center mb-16">
                    <h1 className="text-4xl md:text-6xl font-bold mb-6">
                        How It <span className="text-cyan-400">Works</span>
                    </h1>
                    <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                        A decentralized gig economy platform powered by Neo N3 blockchain and AI visual verification.
                    </p>
                </div>

                {/* Step 1: Client Creates Job */}
                <div className="grid md:grid-cols-2 gap-12 items-center mb-24">
                    <div className="order-2 md:order-1">
                        <div className="relative rounded-2xl overflow-hidden border border-slate-800 shadow-2xl shadow-cyan-900/20">
                            <Image
                                src="/landing/create-job.png"
                                alt="Create Job Interface"
                                width={800}
                                height={600}
                                className="w-full h-auto"
                            />
                        </div>
                    </div>
                    <div className="order-1 md:order-2 space-y-6">
                        <div className="inline-block px-4 py-1 bg-cyan-500/10 text-cyan-400 rounded-full text-sm font-medium border border-cyan-500/20">
                            Step 1: For Clients
                        </div>
                        <h2 className="text-3xl font-bold">Smart Job Creation</h2>
                        <p className="text-slate-400 text-lg">
                            Clients describe tasks in natural language. Our AI automatically parses requirements, sets up verification criteria, and locks funds in a smart contract escrow.
                        </p>
                        <ul className="space-y-3 text-slate-300">
                            <li className="flex items-center gap-3">
                                <span className="text-cyan-400">✓</span> Natural Language Processing
                            </li>
                            <li className="flex items-center gap-3">
                                <span className="text-cyan-400">✓</span> Automatic Escrow Locking
                            </li>
                            <li className="flex items-center gap-3">
                                <span className="text-cyan-400">✓</span> Reference Photo Uploads
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Step 2: Worker Finds Jobs */}
                <div className="grid md:grid-cols-2 gap-12 items-center mb-24">
                    <div className="space-y-6">
                        <div className="inline-block px-4 py-1 bg-green-500/10 text-green-400 rounded-full text-sm font-medium border border-green-500/20">
                            Step 2: For Workers
                        </div>
                        <h2 className="text-3xl font-bold">Browse & Claim Gigs</h2>
                        <p className="text-slate-400 text-lg">
                            Workers browse available gigs on the blockchain. Smart contracts ensure fair, first-come-first-served claiming without intermediaries.
                        </p>
                        <ul className="space-y-3 text-slate-300">
                            <li className="flex items-center gap-3">
                                <span className="text-green-400">✓</span> Transparent Pricing in GAS
                            </li>
                            <li className="flex items-center gap-3">
                                <span className="text-green-400">✓</span> Instant Claiming
                            </li>
                            <li className="flex items-center gap-3">
                                <span className="text-green-400">✓</span> Location-based Filtering
                            </li>
                        </ul>
                    </div>
                    <div className="relative rounded-2xl overflow-hidden border border-slate-800 shadow-2xl shadow-green-900/20">
                        <Image
                            src="/landing/available-jobs.png"
                            alt="Available Jobs Interface"
                            width={800}
                            height={600}
                            className="w-full h-auto"
                        />
                    </div>
                </div>

                {/* Step 3: AI Verification */}
                <div className="grid md:grid-cols-2 gap-12 items-center mb-24">
                    <div className="order-2 md:order-1">
                        <div className="relative rounded-2xl overflow-hidden border border-slate-800 shadow-2xl shadow-purple-900/20">
                            <Image
                                src="/landing/submit-proof.png"
                                alt="Submit Proof Interface"
                                width={800}
                                height={600}
                                className="w-full h-auto"
                            />
                        </div>
                    </div>
                    <div className="order-1 md:order-2 space-y-6">
                        <div className="inline-block px-4 py-1 bg-purple-500/10 text-purple-400 rounded-full text-sm font-medium border border-purple-500/20">
                            Step 3: AI Verification
                        </div>
                        <h2 className="text-3xl font-bold">Proof & Payment</h2>
                        <p className="text-slate-400 text-lg">
                            Workers submit photo proof. Our "Eye Agent" AI analyzes the images against the original requirements and reference photos to verify the work.
                        </p>
                        <ul className="space-y-3 text-slate-300">
                            <li className="flex items-center gap-3">
                                <span className="text-purple-400">✓</span> Visual Comparison
                            </li>
                            <li className="flex items-center gap-3">
                                <span className="text-purple-400">✓</span> GPS Location Verification
                            </li>
                            <li className="flex items-center gap-3">
                                <span className="text-purple-400">✓</span> Instant Smart Contract Payout
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Step 4: Wallet & History */}
                <div className="grid md:grid-cols-2 gap-12 items-center mb-24">
                    <div className="space-y-6">
                        <div className="inline-block px-4 py-1 bg-orange-500/10 text-orange-400 rounded-full text-sm font-medium border border-orange-500/20">
                            Step 4: Management
                        </div>
                        <h2 className="text-3xl font-bold">Wallet & History</h2>
                        <p className="text-slate-400 text-lg">
                            Track earnings, view job history, and manage your crypto wallet directly within the platform.
                        </p>
                    </div>
                    <div className="relative rounded-2xl overflow-hidden border border-slate-800 shadow-2xl shadow-orange-900/20">
                        <Image
                            src="/landing/wallet.png"
                            alt="Wallet Interface"
                            width={800}
                            height={600}
                            className="w-full h-auto"
                        />
                    </div>
                </div>

                {/* CTA */}
                <div className="text-center py-12 bg-slate-900/50 rounded-3xl border border-slate-800">
                    <h2 className="text-3xl font-bold mb-6">Ready to get started?</h2>
                    <Link
                        href="/"
                        className="inline-block px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full font-bold text-lg hover:shadow-lg hover:shadow-cyan-500/25 transition-all"
                    >
                        Launch App
                    </Link>
                </div>
            </div>
        </div>
    );
}
