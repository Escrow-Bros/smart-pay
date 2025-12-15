'use client';

import Link from 'next/link';
import Image from 'next/image';
import { Shield, ArrowLeft, Gem, Briefcase, HardHat, Scale, Users } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useApp } from '@/context/AppContext';
import { useState } from 'react';

type FlowType = 'client' | 'worker' | 'tribunal';

export default function HowItWorks() {
    const router = useRouter();
    const { selectRole } = useApp();
    const [activeTab, setActiveTab] = useState<FlowType>('client');

    const handleSelectRole = (role: 'client' | 'worker' | 'tribunal') => {
        if (role === 'tribunal') {
            router.push('/tribunal');
        } else {
            const isClient = role === 'client';
            selectRole(isClient);
            router.push(isClient ? '/client/create' : '/worker/jobs');
        }
    };

    return (
        <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black text-white p-4 md:p-8 selection:bg-cyan-500/30">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-16">
                    <Link href="/" className="group flex items-center gap-2 transition-transform hover:scale-105">
                        <div className="relative">
                            <Gem className="w-8 h-8 text-cyan-400 relative z-10" />
                            <div className="absolute inset-0 bg-cyan-400/50 blur-lg rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                        <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                            GigSmartPay
                        </span>
                    </Link>
                    <Link
                        href="/"
                        className="px-6 py-2.5 bg-white/5 border border-white/10 rounded-full hover:bg-white/10 hover:border-cyan-500/50 transition-all text-sm font-medium flex items-center gap-2 backdrop-blur-sm group"
                    >
                        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" /> Back to Home
                    </Link>
                </div>

                {/* Hero */}
                <div className="text-center mb-20 relative">
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[300px] bg-cyan-500/20 blur-[100px] rounded-full -z-10" />

                    <h1 className="text-5xl md:text-7xl font-bold mb-8 tracking-tight">
                        How It <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 animate-gradient">Works</span>
                    </h1>
                    <p className="text-xl md:text-2xl text-slate-300 max-w-2xl mx-auto mb-16 leading-relaxed font-light">
                        Three simple, secure flows for <span className="text-cyan-400 font-medium">Clients</span>, <span className="text-green-400 font-medium">Workers</span>, and <span className="text-purple-400 font-medium">Arbiters</span>.
                    </p>

                    {/* Tab Navigation */}
                    <div className="flex flex-wrap justify-center gap-4 p-2 bg-white/5 backdrop-blur-md rounded-full inline-flex border border-white/10">
                        <button
                            onClick={() => setActiveTab('client')}
                            className={`flex items-center gap-2.5 px-8 py-3 rounded-full font-semibold transition-all duration-300 ${activeTab === 'client'
                                ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-[0_0_20px_rgba(6,182,212,0.4)] ring-1 ring-white/20'
                                : 'text-slate-400 hover:text-white hover:bg-white/5'
                                }`}
                        >
                            <Briefcase className="w-5 h-5" />
                            For Clients
                        </button>
                        <button
                            onClick={() => setActiveTab('worker')}
                            className={`flex items-center gap-2.5 px-8 py-3 rounded-full font-semibold transition-all duration-300 ${activeTab === 'worker'
                                ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white shadow-[0_0_20px_rgba(34,197,94,0.4)] ring-1 ring-white/20'
                                : 'text-slate-400 hover:text-white hover:bg-white/5'
                                }`}
                        >
                            <HardHat className="w-5 h-5" />
                            For Workers
                        </button>
                        <button
                            onClick={() => setActiveTab('tribunal')}
                            className={`flex items-center gap-2.5 px-8 py-3 rounded-full font-semibold transition-all duration-300 ${activeTab === 'tribunal'
                                ? 'bg-gradient-to-r from-purple-600 to-violet-600 text-white shadow-[0_0_20px_rgba(168,85,247,0.4)] ring-1 ring-white/20'
                                : 'text-slate-400 hover:text-white hover:bg-white/5'
                                }`}
                        >
                            <Scale className="w-5 h-5" />
                            For Arbiters
                        </button>
                    </div>
                </div>

                {/* CLIENT FLOW */}
                {activeTab === 'client' && (
                    <div className="animate-in fade-in slide-in-from-bottom-8 duration-500">
                        <ClientFlow />
                    </div>
                )}

                {/* WORKER FLOW */}
                {activeTab === 'worker' && (
                    <div className="animate-in fade-in slide-in-from-bottom-8 duration-500">
                        <WorkerFlow />
                    </div>
                )}

                {/* TRIBUNAL FLOW */}
                {activeTab === 'tribunal' && (
                    <div className="animate-in fade-in slide-in-from-bottom-8 duration-500">
                        <TribunalFlow />
                    </div>
                )}

                {/* CTA */}
                <div className="mt-24 text-center py-16 bg-gradient-to-b from-slate-900/50 to-slate-900 border border-slate-800/50 rounded-[40px] relative overflow-hidden group">
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-purple-500/10 to-green-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                    <div className="relative z-10">
                        <h2 className="text-4xl font-bold mb-8 bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">Ready to get started?</h2>
                        <div className="flex flex-col sm:flex-row gap-6 justify-center">
                            <button
                                onClick={() => handleSelectRole('client')}
                                className="px-10 py-5 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full font-bold text-lg hover:shadow-[0_0_30px_rgba(6,182,212,0.4)] hover:-translate-y-1 transition-all flex items-center justify-center gap-3 group/btn"
                            >
                                <Briefcase className="w-6 h-6 group-hover/btn:scale-110 transition-transform" />
                                Hire Talent
                            </button>
                            <button
                                onClick={() => handleSelectRole('worker')}
                                className="px-10 py-5 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full font-bold text-lg hover:shadow-[0_0_30px_rgba(34,197,94,0.4)] hover:-translate-y-1 transition-all flex items-center justify-center gap-3 group/btn"
                            >
                                <HardHat className="w-6 h-6 group-hover/btn:scale-110 transition-transform" />
                                Find Work
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

// ========== CLIENT FLOW COMPONENT ==========
function ClientFlow() {
    return (
        <div className="mb-24">
            <div className="flex items-center gap-6 mb-16 p-6 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-sm">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/20 flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.15)]">
                    <Briefcase className="w-8 h-8 text-cyan-400" />
                </div>
                <div>
                    <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">For Clients: Define, Deploy & Manage</h2>
                    <p className="text-slate-400 text-lg">Hire workers and pay only when work is verified</p>
                </div>
            </div>

            {/* Client steps */}
            <div className="space-y-32">
                {/* Step 1 */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="order-2 md:order-1 relative">
                        <div className="absolute -inset-4 bg-cyan-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-cyan-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/client_1_ai_chat.png" alt="AI Job Definition" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                    <div className="order-1 md:order-2 space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-cyan-500/10 text-cyan-400 rounded-full text-sm font-bold border border-cyan-500/20 shadow-[0_0_10px_rgba(6,182,212,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                            Step 1
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-cyan-400 transition-colors">AI-Powered Job Definition</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Simply describe your task in natural language. Our AI Agent parses your intent and automatically structures the smart contract parameters for you.
                        </p>
                    </div>
                </div>

                {/* Step 2 */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-cyan-500/10 text-cyan-400 rounded-full text-sm font-bold border border-cyan-500/20 shadow-[0_0_10px_rgba(6,182,212,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                            Step 2
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-cyan-400 transition-colors">Define Verification Logic</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Set precise GPS geofences and upload reference imagery. These become the immutable "ground truth" that the AI Validator checks against.
                        </p>
                    </div>
                    <div className="relative">
                        <div className="absolute -inset-4 bg-cyan-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-cyan-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/client_2_set_logic.png" alt="Set Verification Logic" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                </div>

                {/* Step 3 */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="order-2 md:order-1 relative">
                        <div className="absolute -inset-4 bg-cyan-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-cyan-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/client_3_preview.png" alt="Smart Contract Preview" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                    <div className="order-1 md:order-2 space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-cyan-500/10 text-cyan-400 rounded-full text-sm font-bold border border-cyan-500/20 shadow-[0_0_10px_rgba(6,182,212,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                            Step 3
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-cyan-400 transition-colors">Smart Contract Preview</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Review all job parameters and contract terms. Ensure your deadlines, payment amounts, and requirements are airtight before deployment.
                        </p>
                    </div>
                </div>

                {/* Step 4 */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-cyan-500/10 text-cyan-400 rounded-full text-sm font-bold border border-cyan-500/20 shadow-[0_0_10px_rgba(6,182,212,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                            Step 4
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-cyan-400 transition-colors">Secure Escrow Funding</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Upon deployment, your GAS tokens are programmatically locked in a smart contract escrow. Funds remain secure until proof of work is verified.
                        </p>
                    </div>
                    <div className="relative">
                        <div className="absolute -inset-4 bg-cyan-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-cyan-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/client_4_escrow.png" alt="Escrow Funding" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                </div>

                {/* Step 5 */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="order-2 md:order-1 relative">
                        <div className="absolute -inset-4 bg-cyan-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-cyan-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/client_5_activation.png" alt="Immutable Activation" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                    <div className="order-1 md:order-2 space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-cyan-500/10 text-cyan-400 rounded-full text-sm font-bold border border-cyan-500/20 shadow-[0_0_10px_rgba(6,182,212,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                            Step 5
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-cyan-400 transition-colors">Immutable Activation</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Your job is officially live. The creation transaction is recorded on the Neo N3 blockchain, guaranteeing transparency and trust for all workers.
                        </p>
                    </div>
                </div>

                {/* Step 6 */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-cyan-500/10 text-cyan-400 rounded-full text-sm font-bold border border-cyan-500/20 shadow-[0_0_10px_rgba(6,182,212,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                            Step 6
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-cyan-400 transition-colors">Project Monitoring</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Track the status of your active jobs and view attached proof photos directly in your dashboard once work is submitted.
                        </p>
                    </div>
                    <div className="relative">
                        <div className="absolute -inset-4 bg-cyan-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-cyan-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/client_6_monitor.png" alt="Project Monitoring" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                </div>

                {/* Step 7 */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="order-2 md:order-1 relative">
                        <div className="absolute -inset-4 bg-cyan-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-cyan-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/client_7_wallet.png" alt="Asset Management" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                    <div className="order-1 md:order-2 space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-cyan-500/10 text-cyan-400 rounded-full text-sm font-bold border border-cyan-500/20 shadow-[0_0_10px_rgba(6,182,212,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                            Step 7
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-cyan-400 transition-colors">Asset Management</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Monitor your GAS balance, track escrow deductions, and manage your crypto assets in real-time with full transparency.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

// ========== WORKER FLOW COMPONENT ==========
function WorkerFlow() {
    return (
        <div className="mb-24">
            <div className="flex items-center gap-6 mb-16 p-6 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-sm">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/20 flex items-center justify-center shadow-[0_0_15px_rgba(34,197,94,0.15)]">
                    <Users className="w-8 h-8 text-green-400" />
                </div>
                <div>
                    <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">For Workers: Prove, Earn & Protect</h2>
                    <p className="text-slate-400 text-lg">Get paid instantly not just for work, but for proof</p>
                </div>
            </div>

            <div className="space-y-32">
                {/* Step 1: Browse Jobs */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="order-2 md:order-1 relative">
                        <div className="absolute -inset-4 bg-green-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-green-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/worker_1_browse.png" alt="Smart Discovery" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                    <div className="order-1 md:order-2 space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-green-500/10 text-green-400 rounded-full text-sm font-bold border border-green-500/20 shadow-[0_0_10px_rgba(34,197,94,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                            Step 1
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-green-400 transition-colors">Smart Discovery</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Find nearby high-value gigs instantly on our interactive map. Filter by reward amount, difficulty, and distance.
                        </p>
                    </div>
                </div>

                {/* Step 2: Job Intel */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-green-500/10 text-green-400 rounded-full text-sm font-bold border border-green-500/20 shadow-[0_0_10px_rgba(34,197,94,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                            Step 2
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-green-400 transition-colors">Job Intel</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Review complete requirements, reference photos, and exact location data before you claim to ensure it's the right fit.
                        </p>
                    </div>
                    <div className="relative">
                        <div className="absolute -inset-4 bg-green-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-green-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/worker_2_details.png" alt="Job Intel" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                </div>

                {/* Step 3: Proof Submission */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="order-2 md:order-1 relative">
                        <div className="absolute -inset-4 bg-green-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-green-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/worker_3_verify.png" alt="Proof Submission" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                    <div className="order-1 md:order-2 space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-green-500/10 text-green-400 rounded-full text-sm font-bold border border-green-500/20 shadow-[0_0_10px_rgba(34,197,94,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                            Step 3
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-green-400 transition-colors">Proof Submission</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Upload your completion photos securely. Our system automatically validates your GPS coordinates in real-time.
                        </p>
                    </div>
                </div>

                {/* Step 4: AI Analysis */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-purple-500/10 text-purple-400 rounded-full text-sm font-bold border border-purple-500/20 shadow-[0_0_10px_rgba(168,85,247,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
                            Step 4
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-purple-400 transition-colors">AI Analysis</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Our proprietary Eye Agent AI analyzes your visual evidence, comparing it pixel-by-pixel against the client's requirements.
                        </p>
                    </div>
                    <div className="relative">
                        <div className="absolute -inset-4 bg-purple-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-purple-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/worker_4_analysis.png" alt="AI Analysis" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                </div>

                {/* Step 5: Verification Report */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="order-2 md:order-1 relative">
                        <div className="absolute -inset-4 bg-purple-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-purple-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/worker_5_report.png" alt="Verification Report" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                    <div className="order-1 md:order-2 space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-purple-500/10 text-purple-400 rounded-full text-sm font-bold border border-purple-500/20 shadow-[0_0_10px_rgba(168,85,247,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
                            Step 5
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-purple-400 transition-colors">Verification Report</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Receive an instant pass/fail verdict with a detailed quality score breakdown. No more waiting days for manual approval.
                        </p>
                    </div>
                </div>

                {/* Step 6: Payment Processing */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-green-500/10 text-green-400 rounded-full text-sm font-bold border border-green-500/20 shadow-[0_0_10px_rgba(34,197,94,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                            Step 6
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-green-400 transition-colors">Payment Processing</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Upon verified approval, the smart contract automatically initiates the release of locked funds from escrow.
                        </p>
                    </div>
                    <div className="relative">
                        <div className="absolute -inset-4 bg-green-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-green-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/worker_6_processing.png" alt="Payment Processing" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                </div>

                {/* Step 7: Instant Settlement */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="order-2 md:order-1 relative">
                        <div className="absolute -inset-4 bg-green-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-green-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/worker_7_payout.png" alt="Instant Settlement" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                    <div className="order-1 md:order-2 space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-green-500/10 text-green-400 rounded-full text-sm font-bold border border-green-500/20 shadow-[0_0_10px_rgba(34,197,94,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                            Step 7
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-green-400 transition-colors">Instant Settlement</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            GAS tokens arrive in your wallet immediately. Transactions are final, global, and fee-minimized.
                        </p>
                    </div>
                </div>

                {/* Step 8: Dispute Protection */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-red-500/10 text-red-400 rounded-full text-sm font-bold border border-red-500/20 shadow-[0_0_10px_rgba(248,113,113,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-red-400 animate-pulse" />
                            Step 8
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-red-400 transition-colors">Dispute Protection</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Work unfairly rejected? Instantly create a dispute. Your evidence is sent to the decentralized Tribunal for human + AI review.
                        </p>
                    </div>
                    <div className="relative">
                        <div className="absolute -inset-4 bg-red-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-red-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/worker_8_dispute.png" alt="Dispute Protection" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                </div>

                {/* Step 9: Work History */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="order-2 md:order-1 relative">
                        <div className="absolute -inset-4 bg-blue-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-blue-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/worker_9_history.png" alt="Work History" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                    <div className="order-1 md:order-2 space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-blue-500/10 text-blue-400 rounded-full text-sm font-bold border border-blue-500/20 shadow-[0_0_10px_rgba(96,165,250,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
                            Step 9
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-blue-400 transition-colors">Work History</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Build your on-chain reputation. View all completed jobs and verification scores in your permanent record.
                        </p>
                    </div>
                </div>

                {/* Step 10: Earnings Wallet */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-green-500/10 text-green-400 rounded-full text-sm font-bold border border-green-500/20 shadow-[0_0_10px_rgba(34,197,94,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                            Step 10
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-green-400 transition-colors">Earnings Wallet</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Track your cumulative earnings and view real-time GAS transactions. Your money is yours, instantly and visibly.
                        </p>
                    </div>
                    <div className="relative">
                        <div className="absolute -inset-4 bg-green-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-green-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/worker_10_wallet.png" alt="Earnings Wallet" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

// ========== TRIBUNAL FLOW COMPONENT ==========
function TribunalFlow() {
    return (
        <div className="mb-24">
            <div className="flex items-center gap-6 mb-16 p-6 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-sm">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500/20 to-indigo-500/20 border border-purple-500/20 flex items-center justify-center shadow-[0_0_15px_rgba(168,85,247,0.15)]">
                    <Scale className="w-8 h-8 text-purple-400" />
                </div>
                <div>
                    <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">For Tribunal: Fair Adjudication</h2>
                    <p className="text-slate-400 text-lg">Decentralized dispute resolution powered by AI</p>
                </div>
            </div>

            <div className="space-y-32">
                {/* Step 1: Dashboard */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="order-2 md:order-1 relative">
                        <div className="absolute -inset-4 bg-purple-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-purple-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/tribunal_1_dashboard.png" alt="Dispute Command Center" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                    <div className="order-1 md:order-2 space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-purple-500/10 text-purple-400 rounded-full text-sm font-bold border border-purple-500/20 shadow-[0_0_10px_rgba(168,85,247,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
                            Step 1
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-purple-400 transition-colors">Dispute Command Center</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Visual dashboard for Tribunal members to monitor active disputes, case health, and system-wide resolution metrics.
                        </p>
                    </div>
                </div>

                {/* Step 2: Evidence Review */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-purple-500/10 text-purple-400 rounded-full text-sm font-bold border border-purple-500/20 shadow-[0_0_10px_rgba(168,85,247,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
                            Step 2
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-purple-400 transition-colors">Evidence Review</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Deep dive into worker proof vs. client claims. Review GPS data, visual evidence, and AI analysis reports side-by-side.
                        </p>
                    </div>
                    <div className="relative">
                        <div className="absolute -inset-4 bg-purple-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-purple-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/tribunal_2_review.png" alt="Evidence Review" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                </div>

                {/* Step 3: On-Chain Resolution */}
                <div className="grid md:grid-cols-2 gap-16 items-center group">
                    <div className="order-2 md:order-1 relative">
                        <div className="absolute -inset-4 bg-purple-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
                        <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-black/50 group-hover:shadow-purple-500/20 transition-all duration-500 group-hover:-translate-y-1">
                            <Image src="/landing/v2/tribunal_3_verdict.png" alt="On-Chain Resolution" width={800} height={600} className="w-full h-auto" />
                        </div>
                    </div>
                    <div className="order-1 md:order-2 space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-purple-500/10 text-purple-400 rounded-full text-sm font-bold border border-purple-500/20 shadow-[0_0_10px_rgba(168,85,247,0.2)]">
                            <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
                            Step 3
                        </div>
                        <h3 className="text-4xl font-bold text-white group-hover:text-purple-400 transition-colors">On-Chain Resolution</h3>
                        <p className="text-slate-300 text-xl leading-relaxed font-light">
                            Issue final verdicts that execute programmatic payouts. Decisions are immutable and recorded on the Neo N3 blockchain.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
