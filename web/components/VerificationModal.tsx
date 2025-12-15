import { X, CheckCircle2, XCircle, MapPin, AlertTriangle, Image as ImageIcon, Eye } from 'lucide-react';
import { JobDict } from '@/lib/types';
import { useEffect, useState } from 'react';
import {
    GPSVerification,
    Comparison,
    isGPSVerification,
    isComparison,
    getVerificationStatus
} from '@/lib/verification';

interface VerificationModalProps {
    isOpen: boolean;
    onClose: () => void;
    job: JobDict | null;
}

export default function VerificationModal({ isOpen, onClose, job }: VerificationModalProps) {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        if (isOpen) {
            setIsVisible(true);
        } else {
            const timer = setTimeout(() => setIsVisible(false), 300);
            return () => clearTimeout(timer);
        }
    }, [isOpen]);

    if (!isVisible && !isOpen) return null;
    if (!job) return null;

    const status = getVerificationStatus(job);
    if (!status) return null;

    const { result: r, score, isApproved } = status;

    // GPS Data - verification_summary uses 'gps_data', not 'gps_verification'
    const gpsData = (r as any).gps_data ?? r.gps_verification ?? r.breakdown?.visual_location;
    const gps: GPSVerification = isGPSVerification(gpsData) ? gpsData : {};
    const distanceMeters = gps.distance_meters;
    const gpsTier = (gpsData as any)?.tier;

    // Derive GPS match from tier or distance (API doesn't return location_match directly)
    const gpsMatch = gpsTier === 'excellent' || gpsTier === 'good' || gpsTier === 'acceptable' ||
        (distanceMeters != null && distanceMeters <= 300);

    // Visual Checks - verification_summary uses 'quality_indicators'
    const qualityIndicators = (r as any).quality_indicators;
    const comparisonData = r.comparison ?? r.breakdown?.comparison;
    const comparison: Comparison = isComparison(comparisonData) ? comparisonData : {};

    // Use quality_indicators if available (from verification_summary)
    const sameObject = qualityIndicators?.location_verified ?? comparison.same_object;
    const transformationOccurred = qualityIndicators?.transformation_clear ?? comparison.transformation_occurred;

    const issues = r.issues;

    return (
        <div className={`fixed inset-0 z-50 flex items-start justify-center pt-20 pb-10 px-4 transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
                onClick={onClose}
            ></div>

            {/* Modal Content */}
            <div className={`relative w-full max-w-2xl bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl flex flex-col max-h-[85vh] transform transition-all duration-300 ${isOpen ? 'scale-100 translate-y-0' : 'scale-95 translate-y-4'}`}>

                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-slate-700 bg-slate-800/50">
                    <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-full ${isApproved ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                            {isApproved ? <CheckCircle2 className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
                        </div>
                        <div>
                            <h3 className="text-xl font-bold text-white">AI Verification Report</h3>
                            <p className="text-sm text-slate-400">Job #{job.job_id}</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 text-slate-400 hover:text-white hover:bg-slate-700/50 rounded-full transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Body - Scrollable Area */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6 min-h-0">

                    {/* Score Card */}
                    <div className="flex items-center justify-between bg-slate-800/50 p-6 rounded-xl border border-slate-700">
                        <div>
                            <p className="text-slate-400 text-sm font-medium uppercase tracking-wider">Overall Score</p>
                            <div className="text-4xl font-bold text-white mt-1">{score}<span className="text-slate-500 text-2xl font-normal">/100</span></div>
                        </div>
                        <div className={`text-right ${isApproved ? 'text-green-400' : 'text-red-400'}`}>
                            <p className="font-bold text-lg">{isApproved ? 'PASSED' : 'FAILED'}</p>
                            <p className="text-sm opacity-80">{isApproved ? 'Payment Authorized' : 'Dispute Raised'}</p>
                        </div>
                    </div>

                    {/* Reasoning Alert */}
                    <div className={`p-4 rounded-xl border ${isApproved ? 'bg-blue-500/10 border-blue-500/20' : 'bg-red-500/10 border-red-500/20'}`}>
                        <div className="flex gap-3">
                            <Eye className={`w-5 h-5 flex-shrink-0 ${isApproved ? 'text-blue-400' : 'text-red-400'}`} />
                            <div>
                                <h4 className={`font-semibold mb-1 ${isApproved ? 'text-blue-400' : 'text-red-400'}`}>AI Analysis</h4>
                                <p className="text-slate-300 text-sm leading-relaxed">
                                    {r.reason || r.reasoning || "No detailed reasoning provided."}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Score Breakdown */}
                    {r.breakdown && typeof r.breakdown === 'object' && (
                        <div className="bg-slate-800/30 p-5 rounded-xl border border-slate-700">
                            <h4 className="font-semibold text-slate-200 mb-4 text-sm">Score Breakdown</h4>
                            <div className="space-y-3">
                                {Object.entries(r.breakdown).map(([key, value]) => {
                                    const scoreValue = typeof value === 'number' ? value : 0;
                                    const maxScore = key === 'gps_quality' || key === 'transformation' ? 25 :
                                        key === 'visual_location' ? 20 : 15;
                                    const percentage = (scoreValue / maxScore) * 100;

                                    return (
                                        <div key={key}>
                                            <div className="flex items-center justify-between mb-1.5">
                                                <span className="text-xs text-slate-400 capitalize">
                                                    {key.replace(/_/g, ' ')}
                                                </span>
                                                <span className="text-xs font-semibold text-slate-300">
                                                    {scoreValue}/{maxScore}
                                                </span>
                                            </div>
                                            <div className="h-1.5 bg-slate-700/50 rounded-full overflow-hidden">
                                                <div
                                                    className={`h-full transition-all duration-500 ${percentage >= 80 ? 'bg-green-500' :
                                                        percentage >= 60 ? 'bg-yellow-500' :
                                                            'bg-red-500'
                                                        }`}
                                                    style={{ width: `${Math.min(percentage, 100)}%` }}
                                                />
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    {/* Breakdown Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* GPS Verification */}
                        <div className="bg-slate-800/30 p-4 rounded-xl border border-slate-700">
                            <div className="flex items-center gap-2 mb-3">
                                <MapPin className="w-4 h-4 text-cyan-400" />
                                <h4 className="font-semibold text-slate-200">GPS Location</h4>
                            </div>
                            <div className="flex items-center gap-2 flex-wrap">
                                {gpsTier ? (
                                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium uppercase ${gpsTier === 'excellent' ? 'bg-green-500/10 text-green-400 border border-green-500/20' :
                                        gpsTier === 'good' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                                            gpsTier === 'acceptable' ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20' :
                                                'bg-red-500/10 text-red-400 border border-red-500/20'
                                        }`}>
                                        {gpsTier === 'excellent' && <CheckCircle2 className="w-3 h-3" />}
                                        {gpsTier}
                                    </span>
                                ) : gpsMatch ? (
                                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-green-500/10 text-green-400 border border-green-500/20">
                                        <CheckCircle2 className="w-3 h-3" /> MATCHED
                                    </span>
                                ) : (
                                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20">
                                        <XCircle className="w-3 h-3" /> MISMATCH
                                    </span>
                                )}
                                {distanceMeters != null && (
                                    <span className="text-xs text-slate-500">
                                        ({Math.round(distanceMeters)}m from site)
                                    </span>
                                )}
                            </div>
                        </div>

                        {/* Visual Transformation */}
                        <div className="bg-slate-800/30 p-4 rounded-xl border border-slate-700">
                            <div className="flex items-center gap-2 mb-3">
                                <ImageIcon className="w-4 h-4 text-purple-400" />
                                <h4 className="font-semibold text-slate-200">Work Visible</h4>
                            </div>
                            <div className="flex flex-col gap-2">
                                <div className="flex items-center justify-between text-sm">
                                    <span className="text-slate-400">Object Match</span>
                                    {sameObject === true ? (
                                        <CheckCircle2 className="w-4 h-4 text-green-400" />
                                    ) : sameObject === false ? (
                                        <XCircle className="w-4 h-4 text-red-400" />
                                    ) : (
                                        <span className="text-slate-500 text-xs">Unknown</span>
                                    )}
                                </div>
                                <div className="flex items-center justify-between text-sm">
                                    <span className="text-slate-400">Transformation</span>
                                    {transformationOccurred === true ? (
                                        <CheckCircle2 className="w-4 h-4 text-green-400" />
                                    ) : transformationOccurred === false ? (
                                        <XCircle className="w-4 h-4 text-red-400" />
                                    ) : (
                                        <span className="text-slate-500 text-xs">Unknown</span>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Issues List (if any) */}
                    {issues && issues.length > 0 && (
                        <div className="bg-slate-800/30 p-4 rounded-xl border border-slate-700">
                            <div className="flex items-center gap-2 mb-3">
                                <AlertTriangle className="w-4 h-4 text-yellow-400" />
                                <h4 className="font-semibold text-slate-200">Flagged Issues</h4>
                            </div>
                            <ul className="space-y-2">
                                {issues.map((issue, i) => (
                                    <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                                        <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-yellow-500 flex-shrink-0"></span>
                                        {issue}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-4 bg-slate-800/50 border-t border-slate-700 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors text-sm font-medium"
                    >
                        Close Report
                    </button>
                </div>
            </div>
        </div>
    );
}
