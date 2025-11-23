'use client';

import { useRouter } from 'next/navigation';
import { useApp } from '@/context/AppContext';

export default function Home() {
  const router = useRouter();
  const { selectRole } = useApp();

  const handleSelectRole = (isClient: boolean) => {
    selectRole(isClient);
    router.push(isClient ? '/client/create' : '/worker/jobs');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
            GigShield 🛡️
          </h1>
          <p className="text-xl text-slate-400">
            Decentralized Gig Platform on Neo N3 Blockchain
          </p>
          <p className="text-sm text-slate-500 mt-2">
            AI-powered escrow • Visual verification • Natural language jobs
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Client Card */}
          <button
            onClick={() => handleSelectRole(true)}
            className="group relative bg-gradient-to-br from-cyan-500/10 to-blue-600/10 border border-cyan-500/30 rounded-3xl p-8 hover:border-cyan-400 transition-all hover:shadow-xl hover:shadow-cyan-500/20"
          >
            <div className="text-6xl mb-4">💼</div>
            <h2 className="text-2xl font-bold text-white mb-2">
              Login as Client
            </h2>
            <p className="text-slate-400 text-sm mb-4">
              Post gigs, lock funds in escrow, and get work done
            </p>
            <ul className="text-left text-slate-500 text-xs space-y-1">
              <li>✓ Natural language job creation</li>
              <li>✓ Automatic fund escrow</li>
              <li>✓ AI visual verification</li>
            </ul>
            <div className="mt-6 text-cyan-400 font-semibold flex items-center justify-center gap-2 group-hover:gap-3 transition-all">
              Get Started
              <span>→</span>
            </div>
          </button>

          {/* Worker Card */}
          <button
            onClick={() => handleSelectRole(false)}
            className="group relative bg-gradient-to-br from-green-500/10 to-emerald-600/10 border border-green-500/30 rounded-3xl p-8 hover:border-green-400 transition-all hover:shadow-xl hover:shadow-green-500/20"
          >
            <div className="text-6xl mb-4">👷</div>
            <h2 className="text-2xl font-bold text-white mb-2">
              Login as Gig Worker
            </h2>
            <p className="text-slate-400 text-sm mb-4">
              Browse jobs, claim gigs, and earn crypto
            </p>
            <ul className="text-left text-slate-500 text-xs space-y-1">
              <li>✓ Browse available gigs</li>
              <li>✓ Auto-claim (first-come-first-served)</li>
              <li>✓ Submit proof & get paid</li>
            </ul>
            <div className="mt-6 text-green-400 font-semibold flex items-center justify-center gap-2 group-hover:gap-3 transition-all">
              Browse Jobs
              <span>→</span>
            </div>
          </button>
        </div>

        <div className="mt-12 text-center text-slate-600 text-sm">
          <p>Powered by Neo N3 • IPFS • Sudo AI</p>
        </div>
      </div>
    </div>
  );
}
