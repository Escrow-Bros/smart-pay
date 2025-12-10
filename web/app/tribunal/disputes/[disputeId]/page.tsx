'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import type { DisputeDict } from '@/lib/types';

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
        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/disputes/${disputeId}`
            );
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

        const action = approveWorker ? 'approve' : 'refund';
        if (!confirm(`Are you sure you want to ${action} this dispute? This action will be recorded on the blockchain.`)) {
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
                alert(`Dispute resolved successfully!\nTransaction: ${data.transaction.tx_hash}`);
                router.push('/tribunal');
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

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-gray-500">Loading dispute details...</div>
            </div>
        );
    }

    if (error && !dispute) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                <p className="text-red-800">{error}</p>
                <Link href="/tribunal" className="text-blue-600 hover:underline mt-4 inline-block">
                    ← Back to Tribunal
                </Link>
            </div>
        );
    }

    if (!dispute) return null;

    const isResolved = dispute.status === 'RESOLVED';

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-start justify-between">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <h1 className="text-2xl font-bold text-gray-900">
                                Dispute #{dispute.dispute_id}
                            </h1>
                            <StatusBadge status={dispute.status} />
                        </div>
                        <p className="text-sm text-gray-500">
                            Raised on {new Date(dispute.raised_at).toLocaleString()}
                        </p>
                    </div>
                    <Link
                        href="/tribunal/disputes"
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                    >
                        ← Back to All Disputes
                    </Link>
                </div>
            </div>

            {/* Job Details */}
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Job Details</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <InfoField label="Job ID" value={`#${dispute.job_id}`} />
                    <InfoField label="Amount" value={`${dispute.amount} GAS`} />
                    <InfoField label="Description" value={dispute.description || 'N/A'} />
                    <InfoField label="Client" value={shortenAddress(dispute.client_address || '')} />
                    <InfoField label="Worker" value={shortenAddress(dispute.worker_address || '')} />
                </div>
            </div>

            {/* Dispute Information */}
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Dispute Information</h2>
                <div className="space-y-4">
                    <InfoField label="Raised By" value={shortenAddress(dispute.raised_by || '')} />
                    <InfoField label="Reason" value={dispute.reason} isLong />
                    {dispute.ai_verdict && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                AI Analysis Verdict
                            </label>
                            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                                <p className="text-sm text-purple-900">
                                    {typeof dispute.ai_verdict === 'string' 
                                        ? dispute.ai_verdict 
                                        : dispute.ai_verdict?.verdict || dispute.ai_verdict?.summary || JSON.stringify(dispute.ai_verdict, null, 2)}
                                </p>
                                {dispute.confidence_score != null && (
                                    <div className="mt-2">
                                        <span className="text-xs text-purple-700">
                                            Confidence: {(dispute.confidence_score * 100).toFixed(1)}%
                                        </span>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Photo Comparison */}
            {((dispute.reference_photos && dispute.reference_photos.length > 0) || 
              (dispute.proof_photos && dispute.proof_photos.length > 0)) && (
                <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-lg font-semibold text-gray-900 mb-4">Photo Comparison</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {dispute.reference_photos && dispute.reference_photos.length > 0 && (
                            <div>
                                <h3 className="text-sm font-medium text-gray-700 mb-2">Reference (Client)</h3>
                                <img
                                    src={dispute.reference_photos[0]}
                                    alt="Reference"
                                    className="w-full h-64 object-cover rounded-lg border border-gray-300"
                                />
                            </div>
                        )}
                        {dispute.proof_photos && dispute.proof_photos.length > 0 && (
                            <div>
                                <h3 className="text-sm font-medium text-gray-700 mb-2">Proof (Worker)</h3>
                                <img
                                    src={dispute.proof_photos[0]}
                                    alt="Proof"
                                    className="w-full h-64 object-cover rounded-lg border border-gray-300"
                                />
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Resolution Section */}
            {isResolved ? (
                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                    <h2 className="text-lg font-semibold text-green-900 mb-4">✅ Resolution</h2>
                    <div className="space-y-3">
                        <InfoField 
                            label="Resolved By" 
                            value={shortenAddress(dispute.resolved_by || '')} 
                        />
                        <InfoField 
                            label="Resolved At" 
                            value={dispute.resolved_at ? new Date(dispute.resolved_at).toLocaleString() : 'N/A'} 
                        />
                        <InfoField 
                            label="Outcome" 
                            value={dispute.resolution === 'APPROVED' ? 'Worker Approved (95% payment)' : 'Client Refunded (100%)'} 
                        />
                        {dispute.resolution_notes && (
                            <InfoField label="Notes" value={dispute.resolution_notes} isLong />
                        )}
                        {dispute.transaction_hash && (
                            <InfoField 
                                label="Transaction Hash" 
                                value={dispute.transaction_hash} 
                            />
                        )}
                    </div>
                </div>
            ) : (
                <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-lg font-semibold text-gray-900 mb-4">⚖️ Resolve Dispute</h2>
                    
                    {error && (
                        <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
                            <p className="text-sm text-red-800">{error}</p>
                        </div>
                    )}

                    <div className="mb-6">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Resolution Notes (Optional)
                        </label>
                        <textarea
                            value={resolutionNotes}
                            onChange={(e) => setResolutionNotes(e.target.value)}
                            rows={4}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="Add any notes about your decision..."
                            disabled={isResolving}
                        />
                    </div>

                    <div className="flex gap-4">
                        <button
                            onClick={() => handleResolve(true)}
                            disabled={isResolving}
                            className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            {isResolving ? 'Processing...' : '✅ Approve Worker'}
                        </button>
                        <button
                            onClick={() => handleResolve(false)}
                            disabled={isResolving}
                            className="flex-1 bg-red-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            {isResolving ? 'Processing...' : '💰 Refund Client'}
                        </button>
                    </div>

                    <div className="mt-4 text-sm text-gray-600 bg-gray-50 rounded-lg p-4">
                        <p className="font-medium mb-2">ℹ️ Resolution Actions:</p>
                        <ul className="list-disc list-inside space-y-1">
                            <li><strong>Approve Worker:</strong> Worker receives 95% of payment (5% platform fee). Job marked as completed.</li>
                            <li><strong>Refund Client:</strong> Client receives 100% refund. Worker receives nothing. Job marked as failed.</li>
                        </ul>
                    </div>
                </div>
            )}
        </div>
    );
}

function InfoField({ label, value, isLong = false }: { label: string; value: string; isLong?: boolean }) {
    return (
        <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
            <p className={`text-sm text-gray-900 ${isLong ? '' : 'truncate'}`}>
                {value || 'N/A'}
            </p>
        </div>
    );
}

function StatusBadge({ status }: { status: string }) {
    const colorClasses = {
        PENDING: 'bg-red-100 text-red-800',
        UNDER_REVIEW: 'bg-yellow-100 text-yellow-800',
        RESOLVED: 'bg-green-100 text-green-800',
    }[status] || 'bg-gray-100 text-gray-800';

    return (
        <span className={`px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full ${colorClasses}`}>
            {status.replace('_', ' ')}
        </span>
    );
}

function shortenAddress(address: string): string {
    if (!address || address.length < 10) return address;
    return `${address.slice(0, 8)}...${address.slice(-6)}`;
}
