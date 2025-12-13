'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useApp } from '@/context/AppContext';
import { Briefcase, HardHat, BookOpen, ArrowRight, Scale, Shield, Zap, Eye, Coins, CheckCircle2, TrendingUp } from 'lucide-react';

export default function Home() {
  const router = useRouter();
  const { selectRole } = useApp();

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
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -left-1/4 w-[600px] h-[600px] bg-cyan-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 -right-1/4 w-[600px] h-[600px] bg-purple-500/10 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-500/5 rounded-full blur-3xl"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 py-8 md:py-16">
        {/* Demo Mode Banner */}
        <div className="mb-8 animate-fade-in-up">
          <div className="inline-flex items-center gap-2 bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/30 rounded-full px-4 py-2 mx-auto">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-purple-500"></span>
            </span>
            <span className="text-purple-300 font-medium text-sm">Demo Mode Active</span>
          </div>
        </div>

        {/* Hero Section */}
        <div className="text-center mb-16 animate-fade-in-up">
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-4 tracking-tight">
            Gig<span className="gradient-text">SmartPay</span>
          </h1>
          <p className="text-xl md:text-2xl text-slate-300 mb-3 font-light">
            Trustless Gig Work Powered by <span className="text-cyan-400 font-medium">AI</span> + <span className="text-purple-400 font-medium">Blockchain</span>
          </p>
          <p className="text-slate-500 text-sm md:text-base max-w-2xl mx-auto">
            Post jobs in plain English. Workers get paid instantly when our AI verifies the work is done.
            No middlemen. No disputes. Just code that works.
          </p>

          {/* Stats Banner */}
          <div className="flex flex-wrap justify-center gap-6 md:gap-10 mt-10 mb-8">
            <div className="flex items-center gap-2 animate-fade-in-up stagger-1">
              <div className="w-10 h-10 rounded-xl bg-cyan-500/10 flex items-center justify-center">
                <Coins className="w-5 h-5 text-cyan-400" />
              </div>
              <div className="text-left">
                <p className="text-white font-bold text-lg">5%</p>
                <p className="text-slate-500 text-xs">Platform Fee</p>
              </div>
            </div>
            <div className="flex items-center gap-2 animate-fade-in-up stagger-2">
              <div className="w-10 h-10 rounded-xl bg-green-500/10 flex items-center justify-center">
                <Eye className="w-5 h-5 text-green-400" />
              </div>
              <div className="text-left">
                <p className="text-white font-bold text-lg">AI</p>
                <p className="text-slate-500 text-xs">Visual Verification</p>
              </div>
            </div>
            <div className="flex items-center gap-2 animate-fade-in-up stagger-3">
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center">
                <Zap className="w-5 h-5 text-purple-400" />
              </div>
              <div className="text-left">
                <p className="text-white font-bold text-lg">Instant</p>
                <p className="text-slate-500 text-xs">Crypto Payments</p>
              </div>
            </div>
            <div className="flex items-center gap-2 animate-fade-in-up stagger-4">
              <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center">
                <Shield className="w-5 h-5 text-blue-400" />
              </div>
              <div className="text-left">
                <p className="text-white font-bold text-lg">100%</p>
                <p className="text-slate-500 text-xs">Trustless Escrow</p>
              </div>
            </div>
          </div>

          <Link
            href="/how-it-works"
            className="inline-flex items-center gap-2 px-6 py-3 bg-slate-800/50 hover:bg-slate-700/50 text-slate-300 rounded-full text-sm font-medium transition-all border border-slate-700 hover:border-slate-600 hover:scale-105"
          >
            <BookOpen className="w-4 h-4" /> Learn How It Works
          </Link>
        </div>

        {/* Role Selection Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-16">
          {/* Client Card */}
          <button
            onClick={() => handleSelectRole('client')}
            className="group relative bg-gradient-to-br from-cyan-500/5 to-blue-600/5 glass border border-cyan-500/20 rounded-3xl p-8 hover:border-cyan-400/50 transition-all duration-300 hover:scale-[1.02] hover-glow-cyan animate-fade-in-up stagger-1"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-3xl"></div>
            <div className="relative">
              <div className="mb-5 w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Briefcase className="w-8 h-8 text-cyan-400" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">
                I Need Work Done
              </h2>
              <p className="text-slate-400 text-sm mb-5">
                Post gigs, lock funds in escrow, and get work done
              </p>
              <ul className="text-left text-slate-500 text-sm space-y-2 mb-6">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-cyan-500" />
                  Natural language job creation
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-cyan-500" />
                  Automatic fund escrow
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-cyan-500" />
                  AI visual verification
                </li>
              </ul>
              <div className="flex items-center justify-center gap-2 text-cyan-400 font-semibold group-hover:gap-3 transition-all">
                Post a Job
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          </button>

          {/* Worker Card */}
          <button
            onClick={() => handleSelectRole('worker')}
            className="group relative bg-gradient-to-br from-green-500/5 to-emerald-600/5 glass border border-green-500/20 rounded-3xl p-8 hover:border-green-400/50 transition-all duration-300 hover:scale-[1.02] hover-glow-green animate-fade-in-up stagger-2"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-3xl"></div>
            <div className="relative">
              <div className="mb-5 w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-green-500/20 to-emerald-600/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <HardHat className="w-8 h-8 text-green-400" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">
                I Want to Earn
              </h2>
              <p className="text-slate-400 text-sm mb-5">
                Browse jobs, claim gigs, and get paid in crypto
              </p>
              <ul className="text-left text-slate-500 text-sm space-y-2 mb-6">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                  Browse available gigs
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                  First-come-first-served claims
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                  Instant payment on approval
                </li>
              </ul>
              <div className="flex items-center justify-center gap-2 text-green-400 font-semibold group-hover:gap-3 transition-all">
                Find Work
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          </button>

          {/* Tribunal Card */}
          <button
            onClick={() => handleSelectRole('tribunal')}
            className="group relative bg-gradient-to-br from-purple-500/5 to-pink-600/5 glass border border-purple-500/20 rounded-3xl p-8 hover:border-purple-400/50 transition-all duration-300 hover:scale-[1.02] hover-glow-purple animate-fade-in-up stagger-3"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-3xl"></div>
            <div className="relative">
              <div className="mb-5 w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-600/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Scale className="w-8 h-8 text-purple-400" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">
                AI Tribunal
              </h2>
              <p className="text-slate-400 text-sm mb-5">
                Review disputes and resolve conflicts
              </p>
              <ul className="text-left text-slate-500 text-sm space-y-2 mb-6">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-purple-500" />
                  View all disputes
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-purple-500" />
                  AI verdict analysis
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-purple-500" />
                  Manual resolution
                </li>
              </ul>
              <div className="flex items-center justify-center gap-2 text-purple-400 font-semibold group-hover:gap-3 transition-all">
                Open Dashboard
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          </button>
        </div>

        {/* How It Works Quick Preview */}
        <div className="glass rounded-3xl p-8 mb-12 animate-fade-in-up">
          <h3 className="text-xl font-bold text-white text-center mb-8">How It Works</h3>
          <div className="grid md:grid-cols-4 gap-6 text-center">
            <div className="group">
              <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-cyan-500/10 flex items-center justify-center text-cyan-400 font-bold text-lg group-hover:scale-110 transition-transform">
                1
              </div>
              <p className="text-sm text-slate-300 font-medium">Client Posts Job</p>
              <p className="text-xs text-slate-500 mt-1">Describe task, funds locked in escrow</p>
            </div>
            <div className="group">
              <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-green-500/10 flex items-center justify-center text-green-400 font-bold text-lg group-hover:scale-110 transition-transform">
                2
              </div>
              <p className="text-sm text-slate-300 font-medium">Worker Claims & Completes</p>
              <p className="text-xs text-slate-500 mt-1">Do the work, submit proof photos</p>
            </div>
            <div className="group">
              <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400 font-bold text-lg group-hover:scale-110 transition-transform">
                3
              </div>
              <p className="text-sm text-slate-300 font-medium">AI Verifies Work</p>
              <p className="text-xs text-slate-500 mt-1">Vision AI compares before/after</p>
            </div>
            <div className="group">
              <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400 font-bold text-lg group-hover:scale-110 transition-transform">
                4
              </div>
              <p className="text-sm text-slate-300 font-medium">Instant Payment</p>
              <p className="text-xs text-slate-500 mt-1">GAS released to worker wallet</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-slate-600 text-sm space-y-2">
          <div className="flex items-center justify-center gap-6 text-slate-500">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              Neo N3 TestNet
            </span>
            <span>IPFS Storage</span>
            <span>GPT-4o Vision</span>
          </div>
          <p className="text-slate-600">
            Built with ❤️ for trustless gig economy
          </p>
        </div>
      </div>
    </div>
  );
}
