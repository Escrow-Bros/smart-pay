'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import type { DisputeDict } from '@/lib/types';
import toast from 'react-hot-toast';
import { ArrowLeft, Scale, CheckCircle2, XCircle, AlertTriangle, Clock, MapPin, User, Wallet, Image, Loader2, ExternalLink } from 'lucide-react';
import PhotoLightbox from '@/components/PhotoLightbox';

export default function DisputeDetailPage() {
    const params = useParams();
    const router = useRouter();
    const disputeId = params.disputeId as string;

    const [dispute, setDispute] = useState<DisputeDict | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isResolving, setIsResolving] = useState(false);
    const [resolutionNotes, setResolutionNotes] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        fetchDispute();
    }, [disputeId]);

    const fetchDispute = async () => {
        setIsLoading(true);
        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/disputes/${disputeId}`
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();

            if (data.success) {
                setDispute(data.dispute);
            } else {
                setError('Dispute not found');
            }
        } catch (err) {
            console.error('Failed to fetch dispute:', err);
            setError('Failed to load dispute details');
        } finally {
            setIsLoading(false);
        }
    };

    const handleResolve = async (approveWorker: boolean) => {
        if (!dispute) return;

        const action = approveWorker ? 'approve the worker' : 'refund the client';
        if (!confirm(`Are you sure you want to ${action}? This action will be recorded on the blockchain.`)) {
            return;
        }

        setIsResolving(true);
        setError('');

        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/disputes/resolve`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        dispute_id: parseInt(disputeId),
                        approve_worker: approveWorker,
                        resolution_notes: resolutionNotes || undefined,
                    }),
                }
            );

            const data = await response.json();

            if (data.success) {
                const txHash: string | undefined = data?.transaction?.tx_hash;
                toast.success(txHash ? `Dispute resolved! TX: ${txHash.slice(0, 10)}...` : 'Dispute resolved!', {
                    duration: 5000,
                    position: 'top-center',
                });
                setTimeout(() => router.push('/tribunal'), 1500);
            } else {
                setError(data.error || 'Failed to resolve dispute');
            }
        } catch (err) {
            console.error('Failed to resolve dispute:', err);
            setError('Network error. Please try again.');
        } finally {
            setIsResolving(false);
        }
    };

    const handleDismiss = async () => {
        if (!dispute) return;

        if (!confirm('Dismiss this dispute? The job will be reset so the worker can retry.')) {
            return;
        }

        setIsResolving(true);
        setError('');

        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/disputes/dismiss`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        dispute_id: parseInt(disputeId),
                        reason: resolutionNotes || 'Technical issue',
                    }),
                }
            );

            const data = await response.json();

            if (data.success) {
                toast.success('Dispute dismissed. Worker can retry.', {
                    duration: 4000,
                    position: 'top-center',
                });
                setTimeout(() => router.push('/tribunal'), 1500);
            } else {
                setError(data.error || 'Failed to dismiss dispute');
            }
        } catch (err) {
            console.error('Failed to dismiss dispute:', err);
            setError('Network error. Please try again.');
        } finally {
            setIsResolving(false);
        }
    };

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center h-64 animate-fade-in-up">
                <Loader2 className="w-8 h-8 text-purple-400 animate-spin mb-4" />
                <p className="text-slate-400">Loading dispute details...</p>
            </div>
        );
    }

    if (error && !dispute) {
        return (
            <div className="glass border border-red-500/30 bg-red-500/10 rounded-2xl p-8 text-center animate-fade-in-up">
                <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
                <p className="text-red-400 mb-4">{error}</p>
                <Link href="/tribunal" className="text-purple-400 hover:text-purple-300 transition-colors">
                    ← Back to Tribunal
                </Link>
            </div>
        );
    }

    if (!dispute) return null;

    const isResolved = dispute.status === 'RESOLVED';

    return (
        <div className="space-y-6 animate-fade-in-up">
            {/* Header */}
            <div className="glass border border-slate-800 rounded-2xl p-6">
                <div className="flex items-start justify-between">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <h1 className="text-2xl font-bold text-white">
                                Dispute #{dispute.dispute_id}
                            </h1>
                            <StatusBadge status={dispute.status} />
                        </div>
                        <p className="text-sm text-slate-400 flex items-center gap-2">
                            <Clock className="w-4 h-4" />
                            Raised on {new Date(dispute.raised_at).toLocaleString()}
                        </p>
                    </div>
                    <Link
                        href="/tribunal/disputes"
                        className="flex items-center gap-2 text-purple-400 hover:text-purple-300 text-sm font-medium transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Back to Disputes
                    </Link>
                </div>
            </div>

            {/* Job Details */}
            <div className="glass border border-slate-800 rounded-2xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Scale className="w-5 h-5 text-purple-400" />
                    Job Details
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <InfoField label="Job ID" value={`#${dispute.job_id}`} icon={<Scale className="w-4 h-4" />} />
                    <InfoField label="Amount" value={dispute.amount != null ? `${dispute.amount} GAS` : 'N/A'} icon={<Wallet className="w-4 h-4" />} />
                    <InfoField label="Job Description" value={dispute.description || 'N/A'} isLong />
                    <InfoField label="Dispute Reason" value={dispute.reason || 'N/A'} isLong />
                    <InfoField label="Client" value={shortenAddress(dispute.client_address || '')} icon={<User className="w-4 h-4" />} />
                    <InfoField label="Worker" value={shortenAddress(dispute.worker_address || '')} icon={<User className="w-4 h-4" />} />
                </div>
            </div>

            {/* AI Verdict */}
            {dispute.ai_verdict && typeof dispute.ai_verdict === 'object' && (
                <div className="glass border border-purple-500/30 bg-gradient-to-br from-purple-500/5 to-transparent rounded-2xl p-6">
                    <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        🤖 AI Analysis Verdict
                    </h2>
                    <div className="flex items-center justify-between mb-4">
                        <span className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold ${dispute.ai_verdict.verified
                            ? 'bg-green-500/20 text-green-400'
                            : 'bg-red-500/20 text-red-400'
                            }`}>
                            {dispute.ai_verdict.verified ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                            {dispute.ai_verdict.verdict || (dispute.ai_verdict.verified ? 'APPROVED' : 'REJECTED')}
                        </span>
                        {dispute.ai_verdict.confidence != null && (
                            <span className="text-sm text-purple-400">
                                Confidence: {(dispute.ai_verdict.confidence * 100).toFixed(1)}%
                            </span>
                        )}
                    </div>
                    <p className="text-sm text-slate-300 mb-4">{dispute.ai_verdict.reason || 'No reason provided'}</p>

                    {/* Score Breakdown */}
                    {dispute.ai_verdict.breakdown &&
                        typeof dispute.ai_verdict.breakdown === 'object' &&
                        !Array.isArray(dispute.ai_verdict.breakdown) && (
                            <div className="border-t border-purple-500/20 pt-4 mt-4">
                                <p className="text-xs font-semibold text-purple-300 mb-3">Score Breakdown:</p>
                                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                                    {Object.entries(dispute.ai_verdict.breakdown).map(([key, value]: [string, unknown]) => (
                                        <div key={key} className="bg-slate-800/50 rounded-xl p-3 text-center">
                                            <p className="text-purple-400 text-lg font-bold">{value != null ? String(value) : 'N/A'}</p>
                                            <p className="text-xs text-slate-400 capitalize">{key.replace(/_/g, ' ')}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                    {/* GPS Data */}
                    {dispute.ai_verdict.gps_data &&
                        typeof dispute.ai_verdict.gps_data === 'object' && (
                            <div className="border-t border-purple-500/20 pt-4 mt-4">
                                <p className="text-xs font-semibold text-purple-300 mb-2 flex items-center gap-2">
                                    <MapPin className="w-4 h-4" /> GPS Verification
                                </p>

                                {/* Check if GPS verification failed (system error) vs distance too far */}
                                {dispute.ai_verdict.gps_data.verification_failed ? (
                                    <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-3 mb-2">
                                        <div className="flex items-center gap-2 mb-1">
                                            <AlertTriangle className="w-4 h-4 text-orange-400" />
                                            <span className="text-sm font-semibold text-orange-400">GPS Verification Error</span>
                                        </div>
                                        <p className="text-xs text-orange-300">
                                            System could not verify location - likely a technical issue, not worker fraud.
                                        </p>
                                        <p className="text-xs text-slate-400 mt-1">
                                            {dispute.ai_verdict.gps_data.reasoning}
                                        </p>
                                    </div>
                                ) : (
                                    <div className="flex gap-4 text-sm flex-wrap">
                                        <span className="text-slate-400">
                                            Distance: <strong className={`${dispute.ai_verdict.gps_data.distance_meters != null &&
                                                dispute.ai_verdict.gps_data.distance_meters > 300
                                                ? 'text-red-400'
                                                : 'text-green-400'
                                                }`}>
                                                {dispute.ai_verdict.gps_data.distance_meters != null
                                                    ? `${dispute.ai_verdict.gps_data.distance_meters}m`
                                                    : 'N/A'}
                                            </strong>
                                        </span>
                                        <span className={`font-semibold ${dispute.ai_verdict.gps_data.tier === 'failed' ||
                                            dispute.ai_verdict.gps_data.tier === 'error'
                                            ? 'text-red-400'
                                            : dispute.ai_verdict.gps_data.tier === 'excellent'
                                                ? 'text-green-400'
                                                : 'text-yellow-400'
                                            }`}>
                                            {dispute.ai_verdict.gps_data.tier?.toUpperCase() || 'N/A'}
                                        </span>
                                        {dispute.ai_verdict.gps_data.distance_meters != null &&
                                            dispute.ai_verdict.gps_data.distance_meters > 300 && (
                                                <span className="text-xs text-red-400">
                                                    (Max: 300m)
                                                </span>
                                            )}
                                    </div>
                                )}

                                {/* Show reasoning if available */}
                                {!dispute.ai_verdict.gps_data.verification_failed &&
                                    dispute.ai_verdict.gps_data.reasoning && (
                                        <p className="text-xs text-slate-400 mt-2">
                                            {dispute.ai_verdict.gps_data.reasoning}
                                        </p>
                                    )}
                            </div>
                        )}
                </div>
            )}

            {/* Photo Comparison */}
            {((dispute.reference_photos && dispute.reference_photos.length > 0) ||
                (dispute.proof_photos && dispute.proof_photos.length > 0)) && (
                    <div className="glass border border-slate-800 rounded-2xl p-6">
                        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <Image className="w-5 h-5 text-purple-400" />
                            Photo Evidence
                            <span className="text-xs text-slate-500 font-normal">
                                (Click to enlarge)
                            </span>
                        </h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {dispute.reference_photos && dispute.reference_photos.length > 0 && (
                                <div>
                                    <PhotoLightbox
                                        photos={dispute.reference_photos}
                                        title="📋 Reference Photos (Client)"
                                        columns={2}
                                    />
                                </div>
                            )}
                            {dispute.proof_photos && dispute.proof_photos.length > 0 && (
                                <div>
                                    <PhotoLightbox
                                        photos={dispute.proof_photos}
                                        title="✅ Proof Photos (Worker)"
                                        columns={2}
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                )}

            {/* Resolution Section */}
            {isResolved ? (
                <div className="glass border border-green-500/30 bg-gradient-to-br from-green-500/10 to-transparent rounded-2xl p-6">
                    <h2 className="text-lg font-semibold text-green-400 mb-4 flex items-center gap-2">
                        <CheckCircle2 className="w-5 h-5" />
                        Resolution Complete
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <InfoField label="Resolved By" value={shortenAddress(dispute.resolved_by || '')} />
                        <InfoField label="Resolved At" value={dispute.resolved_at ? new Date(dispute.resolved_at).toLocaleString() : 'N/A'} />
                        <InfoField
                            label="Outcome"
                            value={
                                dispute.resolution === 'APPROVED'
                                    ? 'Worker Approved (95% payment)'
                                    : dispute.resolution === 'DISMISSED'
                                        ? 'Dismissed (Worker can retry)'
                                        : 'Client Refunded (100%)'
                            }
                        />
                        {dispute.transaction_hash && (
                            <div>
                                <p className="text-xs text-slate-400 mb-1">Transaction</p>
                                <a
                                    href={`https://dora.coz.io/transaction/neo3/testnet/0x${dispute.transaction_hash}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center gap-1 text-purple-400 hover:text-purple-300 text-sm"
                                >
                                    <ExternalLink className="w-3 h-3" />
                                    {dispute.transaction_hash.slice(0, 12)}...
                                </a>
                            </div>
                        )}
                    </div>
                    {dispute.resolution_notes && (
                        <div className="mt-4 pt-4 border-t border-green-500/20">
                            <p className="text-xs text-slate-400 mb-1">Resolution Notes</p>
                            <p className="text-sm text-slate-300">{dispute.resolution_notes}</p>
                        </div>
                    )}
                </div>
            ) : (
                <div className="glass border border-slate-800 rounded-2xl p-6">
                    <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <Scale className="w-5 h-5 text-purple-400" />
                        Resolve Dispute
                    </h2>

                    {error && (
                        <div className="mb-4 bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                            <p className="text-sm text-red-400">{error}</p>
                        </div>
                    )}

                    <div className="mb-6">
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Resolution Notes (Optional)
                        </label>
                        <textarea
                            value={resolutionNotes}
                            onChange={(e) => setResolutionNotes(e.target.value)}
                            rows={3}
                            className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                            placeholder="Add any notes about your decision..."
                            disabled={isResolving}
                        />
                    </div>

                    <div className="space-y-3">
                        <div className="flex gap-4">
                            <button
                                onClick={() => handleResolve(true)}
                                disabled={isResolving}
                                className="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-6 py-3 rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-green-500/20"
                            >
                                {isResolving ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                                Approve Worker
                            </button>
                            <button
                                onClick={() => handleResolve(false)}
                                disabled={isResolving}
                                className="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-500 hover:to-pink-500 text-white px-6 py-3 rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-red-500/20"
                            >
                                {isResolving ? <Loader2 className="w-4 h-4 animate-spin" /> : <XCircle className="w-4 h-4" />}
                                Refund Client
                            </button>
                        </div>

                        <button
                            onClick={handleDismiss}
                            disabled={isResolving}
                            className="w-full flex items-center justify-center gap-2 bg-yellow-500/20 border border-yellow-500/30 text-yellow-400 px-6 py-3 rounded-xl font-medium hover:bg-yellow-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                            {isResolving ? <Loader2 className="w-4 h-4 animate-spin" /> : <AlertTriangle className="w-4 h-4" />}
                            Dismiss (Technical Issue)
                        </button>
                    </div>

                    <div className="mt-4 text-xs text-slate-500 bg-slate-800/30 rounded-xl p-4">
                        <p className="font-medium mb-2 text-slate-400">Resolution Actions:</p>
                        <ul className="space-y-1">
                            <li><strong className="text-green-400">Approve Worker:</strong> Worker gets 95% payment</li>
                            <li><strong className="text-red-400">Refund Client:</strong> Client gets 100% back</li>
                            <li><strong className="text-yellow-400">Dismiss:</strong> Reset job, worker can retry</li>
                        </ul>
                    </div>
                </div>
            )}
        </div>
    );
}

function InfoField({ label, value, icon, isLong = false }: { label: string; value: string; icon?: React.ReactNode; isLong?: boolean }) {
    return (
        <div className={isLong ? 'col-span-full' : ''}>
            <p className="text-xs text-slate-400 mb-1 flex items-center gap-1.5">
                {icon}
                {label}
            </p>
            <p className={`text-sm text-white ${isLong ? '' : 'truncate'}`}>
                {value || 'N/A'}
            </p>
        </div>
    );
}

function StatusBadge({ status }: { status: string }) {
    // Simplify: Only PENDING (unresolved) and RESOLVED
    const isPending = status !== 'RESOLVED';

    return (
        <span className={`flex items-center gap-1.5 px-3 py-1 text-sm font-semibold rounded-full ${isPending
            ? 'bg-yellow-500/20 text-yellow-400'
            : 'bg-green-500/20 text-green-400'
            }`}>
            {isPending ? <Clock className="w-3 h-3" /> : <CheckCircle2 className="w-3 h-3" />}
            {isPending ? 'PENDING' : 'RESOLVED'}
        </span>
    );
}

function shortenAddress(address: string): string {
    if (!address || address.length < 10) return address;
    return `${address.slice(0, 8)}...${address.slice(-6)}`;
}
