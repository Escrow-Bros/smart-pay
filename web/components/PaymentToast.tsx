'use client';

import { toast } from 'react-hot-toast';
import { CheckCircle2, DollarSign, ExternalLink, Sparkles } from 'lucide-react';

interface PaymentToastProps {
    gasAmount: string;
    usdAmount?: string;
    txHash?: string;
    type: 'received' | 'sent' | 'confirmed';
    jobId?: number;
}

// Custom payment toast with animation and styling
export function showPaymentToast({ gasAmount, usdAmount, txHash, type, jobId }: PaymentToastProps) {
    const messages = {
        received: 'Payment Received!',
        sent: 'Payment Sent!',
        confirmed: 'Payment Confirmed!',
    };

    const icons = {
        received: '💰',
        sent: '📤',
        confirmed: '✅',
    };

    toast.custom(
        (t) => (
            <div
                className={`${t.visible ? 'animate-in slide-in-from-right fade-in' : 'animate-out slide-out-to-right fade-out'
                    } max-w-md w-full bg-gradient-to-br from-green-900/90 via-slate-900/95 to-slate-900/90 backdrop-blur-xl border border-green-500/30 shadow-2xl shadow-green-500/20 rounded-2xl pointer-events-auto overflow-hidden`}
            >
                {/* Top accent bar */}
                <div className="h-1 bg-gradient-to-r from-green-500 via-cyan-500 to-green-500 animate-pulse" />

                <div className="p-4">
                    <div className="flex items-start gap-3">
                        {/* Icon */}
                        <div className="flex-shrink-0 w-12 h-12 rounded-full bg-green-500/20 border border-green-500/30 flex items-center justify-center animate-bounce-subtle">
                            <span className="text-2xl">{icons[type]}</span>
                        </div>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                                <h3 className="text-lg font-bold text-white">
                                    {messages[type]}
                                </h3>
                                <Sparkles className="w-4 h-4 text-yellow-400 animate-spin-slow" />
                            </div>

                            {jobId && (
                                <p className="text-sm text-slate-400 mb-2">
                                    Job #{jobId}
                                </p>
                            )}

                            {/* Amount */}
                            <div className="flex items-baseline gap-2">
                                <span className="text-2xl font-bold text-green-400">
                                    {gasAmount} GAS
                                </span>
                                {usdAmount && (
                                    <span className="text-sm text-slate-400">
                                        (~{usdAmount})
                                    </span>
                                )}
                            </div>

                            {/* Transaction link */}
                            {txHash && (
                                <a
                                    href={`https://dora.coz.io/transaction/neo3/testnet/${txHash}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="mt-2 inline-flex items-center gap-1 text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
                                >
                                    <ExternalLink className="w-3 h-3" />
                                    View on blockchain
                                </a>
                            )}
                        </div>

                        {/* Close button */}
                        <button
                            onClick={() => toast.dismiss(t.id)}
                            className="flex-shrink-0 p-1 text-slate-500 hover:text-white transition-colors"
                        >
                            ×
                        </button>
                    </div>
                </div>
            </div>
        ),
        {
            duration: 6000,
            position: 'top-right',
        }
    );
}

// Convenience functions
export function showPaymentReceived(gasAmount: string, usdAmount?: string, jobId?: number, txHash?: string) {
    showPaymentToast({ gasAmount, usdAmount, type: 'received', jobId, txHash });
}

export function showPaymentSent(gasAmount: string, usdAmount?: string, jobId?: number, txHash?: string) {
    showPaymentToast({ gasAmount, usdAmount, type: 'sent', jobId, txHash });
}

export function showPaymentConfirmed(gasAmount: string, usdAmount?: string, jobId?: number, txHash?: string) {
    showPaymentToast({ gasAmount, usdAmount, type: 'confirmed', jobId, txHash });
}
