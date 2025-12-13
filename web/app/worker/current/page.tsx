'use client';

import { useState, useEffect } from 'react';
import { useApp } from '@/context/AppContext';
import { apiClient } from '@/lib/api';
import ImageUpload from '@/components/ImageUpload';
import { JobDict, UploadedImage } from '@/lib/types';
import { formatGasWithUSD } from '@/lib/currency';
import toast from 'react-hot-toast';
import { showPaymentReceived } from '@/components/PaymentToast';
import {
    MapPin, Loader2, ExternalLink, ClipboardCheck, CheckCircle2, Clock,
    AlertCircle, Eye, X, Info, MapPinned, Briefcase, RefreshCw, Shield,
    Send, Lightbulb, AlertTriangle, CheckCircle, XCircle, Timer
} from 'lucide-react';

interface TimelineStage {
    id: string;
    label: string;
    status: 'completed' | 'current' | 'pending';
    icon: string;
    description: string;
}

export default function WorkerCurrentJobPage() {
    const { state, fetchData } = useApp();
    const [selectedJob, setSelectedJob] = useState<JobDict | null>(null);
    const [proofImages, setProofImages] = useState<UploadedImage[]>([]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showLocationModal, setShowLocationModal] = useState(false);
    const [showLocationPreview, setShowLocationPreview] = useState(false);
    const [detectedLocation, setDetectedLocation] = useState<{ lat: number; lng: number; accuracy: number } | null>(null);
    const [pendingSubmit, setPendingSubmit] = useState(false);
    const [isGettingLocation, setIsGettingLocation] = useState(false);
    const [locationPermission, setLocationPermission] = useState<'prompt' | 'granted' | 'denied'>('prompt');
    const [showVerificationModal, setShowVerificationModal] = useState(false);
    const [verificationThinking, setVerificationThinking] = useState<string[]>([]);

    // Calculate distance between two coordinates using Haversine formula
    const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
        const R = 6371e3; // Earth's radius in meters
        const φ1 = lat1 * Math.PI / 180;
        const φ2 = lat2 * Math.PI / 180;
        const Δφ = (lat2 - lat1) * Math.PI / 180;
        const Δλ = (lon2 - lon1) * Math.PI / 180;

        const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

        return R * c; // Distance in meters
    };

    // Check location permission on mount
    useEffect(() => {
        const checkLocationPermission = async () => {
            if (!navigator.permissions) {
                console.log('Permissions API not supported');
                return;
            }

            try {
                const result = await navigator.permissions.query({ name: 'geolocation' as PermissionName });
                setLocationPermission(result.state as 'prompt' | 'granted' | 'denied');
                console.log('Location permission status:', result.state);

                // Listen for permission changes
                result.onchange = () => {
                    setLocationPermission(result.state as 'prompt' | 'granted' | 'denied');
                    console.log('Location permission changed to:', result.state);
                };
            } catch (error) {
                console.error('Error checking location permission:', error);
            }
        };

        checkLocationPermission();
    }, []);

    // If no jobs, show empty state
    if (!state.currentJobs || state.currentJobs.length === 0) {
        return (
            <div className="animate-fade-in-up">
                <div className="mb-8">
                    <h2 className="text-3xl font-bold text-white mb-2">Current Jobs</h2>
                    <p className="text-slate-400">Your active job assignments.</p>
                </div>

                <div className="text-center py-16 glass border border-slate-800 rounded-2xl">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-slate-800/50 flex items-center justify-center">
                        <Briefcase className="w-8 h-8 text-slate-600" />
                    </div>
                    <h3 className="text-lg font-semibold text-white mb-2">No active jobs</h3>
                    <p className="text-slate-400">Claim a job from Available Jobs to start working.</p>
                </div>
            </div>
        );
    }

    // If jobs exist but none selected, default to first or show list
    // For simplicity, let's show list if not selected, or just default to first if only one
    const activeJob = selectedJob || state.currentJobs[0];

    const handleAddImage = (image: UploadedImage) => {
        setProofImages(prev => [...prev, image]);
    };

    const handleRemoveImage = (index: number) => {
        setProofImages(prev => prev.filter((_, i) => i !== index));
    };

    const loadVerificationThinking = (job: JobDict) => {
        if (!job.verification_summary) return;

        const steps: string[] = [
            `🔍 Starting AI verification for job #${job.job_id}...`,
            `📋 Task: ${job.description.substring(0, 100)}...`,
            `📍 Verifying GPS location (required within 300m)...`,
        ];

        // Add GPS verification result
        if (job.verification_summary.gps_verification) {
            const gps = job.verification_summary.gps_verification;
            if (gps.location_match) {
                steps.push(`✅ Location verified - Worker within ${gps.distance_meters?.toFixed(1)}m of job site`);
            } else {
                steps.push(`❌ Location check failed: ${gps.reasoning}`);
            }
        }

        steps.push(`🖼️  Step 1: Comparing before/after photos...`);
        steps.push(`   - Checking if photos show same location/object`);
        steps.push(`   - Analyzing visual changes and transformations`);

        // Add comparison insights
        if (job.verification_summary.comparison) {
            const comp = job.verification_summary.comparison;
            if (comp.same_location) {
                steps.push(`   ✓ Same location confirmed (${(comp.location_confidence * 100).toFixed(0)}% confidence)`);
            }
            if (comp.transformation_occurred) {
                steps.push(`   ✓ Work transformation detected`);
            }
            if (comp.visual_changes && comp.visual_changes.length > 0) {
                steps.push(`   📝 Visual changes detected:`);
                comp.visual_changes.slice(0, 3).forEach((change: string) => {
                    steps.push(`      • ${change}`);
                });
            }
        }

        steps.push(`✅ Step 2: Verifying requirements...`);

        // Add requirement checks
        if (job.verification_plan) {
            const plan = job.verification_plan;
            if (plan.success_criteria && plan.success_criteria.length > 0) {
                steps.push(`   📋 Checking ${plan.success_criteria.length} success criteria`);
                plan.success_criteria.slice(0, 2).forEach((criterion: string) => {
                    steps.push(`      • ${criterion}`);
                });
            }
        }

        steps.push(`⚖️  Step 3: Making final decision...`);
        steps.push(`   - Analyzing all verification signals`);
        steps.push(`   - Calculating quality score`);

        if (job.verification_summary.verified) {
            steps.push(`✅ APPROVED: ${job.verification_summary.verdict}`);
            steps.push(`📊 Quality Score: ${job.verification_summary.score}/10`);
        } else {
            steps.push(`❌ REJECTED: ${job.verification_summary.verdict}`);
            steps.push(`📊 Quality Score: ${job.verification_summary.score}/10`);
        }

        setVerificationThinking(steps);
    };

    const getJobTimeline = (job: JobDict): TimelineStage[] => {
        const stages: TimelineStage[] = [
            {
                id: 'assigned',
                label: 'Job Assigned',
                status: 'completed',
                icon: '✓',
                description: 'You claimed this job'
            },
            {
                id: 'work_submitted',
                label: 'Work Submitted',
                status: job.proof_photos && job.proof_photos.length > 0 ? 'completed' : job.status === 'IN_PROGRESS' ? 'pending' : 'current',
                icon: '📸',
                description: 'Proof photos uploaded'
            },
            {
                id: 'verification',
                label: 'AI Verification',
                status: job.verification_summary ? 'completed' : job.status === 'IN_PROGRESS' ? 'pending' : 'current',
                icon: job.verification_summary?.verified ? '✓' : '🔍',
                description: job.verification_summary ? (job.verification_summary.verified ? 'Work approved' : 'Work rejected') : 'Analyzing your work'
            },
            {
                id: 'payment',
                label: 'Payment Processing',
                status: job.status === 'COMPLETED' ? 'completed' : job.status === 'PAYMENT_PENDING' ? 'current' : 'pending',
                icon: job.status === 'COMPLETED' ? '✓' : '⏳',
                description: job.status === 'COMPLETED' ? 'Payment confirmed' : job.status === 'PAYMENT_PENDING' ? 'Confirming on blockchain...' : 'Waiting for approval'
            },
            {
                id: 'completed',
                label: 'Completed',
                status: job.status === 'COMPLETED' ? 'completed' : 'pending',
                icon: job.status === 'COMPLETED' ? '🎉' : '⏱️',
                description: job.status === 'COMPLETED' ? 'Funds released to wallet' : 'Pending completion'
            }
        ];

        // Handle disputed status
        if (job.status === 'DISPUTED') {
            stages[2] = {
                id: 'verification',
                label: 'Verification Failed',
                status: 'current',
                icon: '❌',
                description: 'Work needs improvement'
            };
            stages[3].status = 'pending';
            stages[4].status = 'pending';
        }

        return stages;
    };

    // Get location with retry logic
    const getLocationWithRetry = (retryCount = 0): Promise<GeolocationPosition> => {
        return new Promise((resolve, reject) => {
            const timeout = retryCount === 0 ? 10000 : 20000; // First try 10s, retry 20s

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    console.log(`Location obtained (attempt ${retryCount + 1}):`, {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                        accuracy: position.coords.accuracy
                    });
                    resolve(position);
                },
                (error) => {
                    console.error(`Geolocation error (attempt ${retryCount + 1}):`, error);
                    if (retryCount < 1 && error.code !== 1) {
                        // Retry once if it's not a permission denial
                        console.log('Retrying location request...');
                        toast('📍 Getting location, please wait...', { icon: '🔄', duration: 2000 });
                        setTimeout(() => {
                            getLocationWithRetry(retryCount + 1).then(resolve).catch(reject);
                        }, 500);
                    } else {
                        reject(error);
                    }
                },
                {
                    enableHighAccuracy: true,
                    timeout: timeout,
                    maximumAge: 30000 // Accept cached location up to 30 seconds old
                }
            );
        });
    };

    const handleRequestLocation = async () => {
        setShowLocationModal(false);
        setIsGettingLocation(true);

        if (!navigator.geolocation) {
            toast.error('Geolocation is not supported by your browser');
            setPendingSubmit(false);
            setIsGettingLocation(false);
            return;
        }

        try {
            const position = await getLocationWithRetry();

            // Update permission state
            setLocationPermission('granted');

            const workerLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude,
                accuracy: position.coords.accuracy
            };

            // Store detected location and show preview instead of auto-submitting
            setDetectedLocation(workerLocation);
            setIsGettingLocation(false);
            setShowLocationPreview(true);
        } catch (error: any) {
            setPendingSubmit(false);
            setIsGettingLocation(false);

            // Show specific error message based on error code
            if (error.code === 1) {
                toast.error('📍 Location permission denied. Please enable location in your browser settings and try again.', { duration: 6000 });
            } else if (error.code === 2) {
                toast.error('📍 Location unavailable. Please check your GPS settings and try again.', { duration: 6000 });
            } else if (error.code === 3) {
                toast.error('📍 Location request timed out. Please move to a location with better GPS signal and try again.', { duration: 6000 });
            } else {
                toast.error('📍 Unable to get your location. Please refresh the page and try again.', { duration: 6000 });
            }
        }
    };

    // User confirms location is correct
    const handleConfirmLocation = async () => {
        if (!detectedLocation) return;
        setShowLocationPreview(false);
        await submitProofWithLocation(detectedLocation);
    };

    // User wants to retry getting location
    const handleRetryLocation = () => {
        setDetectedLocation(null);
        setShowLocationPreview(false);
        handleRequestLocation();
    };

    const submitProofWithLocation = async (workerLocation: { lat: number; lng: number; accuracy: number }) => {
        try {
            setIsSubmitting(true);

            // Upload images to IPFS
            const ipfsUrls: string[] = await Promise.all(
                proofImages.map(async (img) => {
                    return await apiClient.uploadToIpfs(img.file);
                })
            );

            // Submit proof with location
            const result = await apiClient.submitProof(activeJob.job_id, ipfsUrls, workerLocation);

            if (result.success) {
                const { gas, usd } = formatGasWithUSD(activeJob.amount);
                showPaymentReceived(gas, usd, activeJob.job_id);
                setProofImages([]);
                setSelectedJob(null);  // Clear selection to show updated job
                await fetchData();  // Refresh to show PAYMENT_PENDING status
            } else {
                toast.error('❌ Work rejected: ' + (result.message || result.verification?.reason || 'Did not meet requirements'), {
                    duration: 6000,
                    position: 'top-center',
                });
                // Still refresh to show dispute status
                await fetchData();
            }
        } catch (error) {
            console.error('Submission error:', error);
            toast.error('Failed to submit proof. Please try again.');
        } finally {
            setIsSubmitting(false);
            setPendingSubmit(false);
        }
    };

    const handleSubmit = () => {
        if (proofImages.length === 0) {
            toast.error('Please upload at least one proof photo.');
            return;
        }

        // Start the location request flow
        setPendingSubmit(true);

        if (locationPermission === 'granted') {
            // Permission already granted, request location directly
            handleRequestLocation();
        } else {
            // Show modal to explain why we need location
            setShowLocationModal(true);
        }
    };

    return (
        <div className="animate-fade-in-up">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-white mb-2">Current Jobs</h2>
                <p className="text-slate-400">Complete your work and submit proof to get paid.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Job List Sidebar */}
                <div className="lg:col-span-1 space-y-4">
                    {state.currentJobs.map((job) => {
                        const { gas, usd } = formatGasWithUSD(job.amount);
                        return (
                            <div
                                key={job.job_id}
                                onClick={() => {
                                    setSelectedJob(job);
                                    setProofImages([]); // Clear images when switching jobs
                                }}
                                className={`p-4 rounded-xl border cursor-pointer transition-all ${activeJob.job_id === job.job_id
                                    ? 'bg-slate-800 border-cyan-500 shadow-lg shadow-cyan-900/20'
                                    : 'bg-slate-900/50 border-slate-800 hover:border-slate-700'
                                    }`}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <span className="text-sm font-mono text-slate-400">#{job.job_id}</span>
                                    <div className="flex flex-col items-end">
                                        <span className="text-green-400 font-bold text-sm">{gas} GAS</span>
                                        <span className="text-slate-500 text-xs">{usd}</span>
                                        <span className={`text-xs px-2 py-0.5 rounded-full mt-1 ${job.status === 'DISPUTED'
                                            ? 'bg-red-900/50 text-red-400 border border-red-800'
                                            : 'bg-blue-900/50 text-blue-400 border border-blue-800'
                                            }`}>
                                            {job.status}
                                        </span>
                                    </div>
                                </div>
                                <p className="text-slate-200 text-sm line-clamp-2">{job.description}</p>
                            </div>
                        );
                    })}
                </div>

                {/* Active Job Details */}
                <div className="lg:col-span-2">
                    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-8">
                        <div className="mb-6">
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex items-center gap-3">
                                    <span className="text-cyan-400 font-semibold text-lg">Job #{activeJob.job_id}</span>
                                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${activeJob.status === 'DISPUTED'
                                        ? 'bg-red-900/50 text-red-400 border border-red-800'
                                        : 'bg-blue-900/50 text-blue-400 border border-blue-800'
                                        }`}>
                                        {activeJob.status}
                                    </span>
                                </div>
                                <div className="text-right">
                                    {(() => {
                                        const { gas, usd } = formatGasWithUSD(activeJob.amount);
                                        return (
                                            <>
                                                <div className="flex items-baseline gap-1 justify-end">
                                                    <span className="text-green-400 font-bold text-2xl">{gas} GAS</span>
                                                </div>
                                                <div className="text-slate-500 text-sm">{usd}</div>
                                            </>
                                        );
                                    })()}
                                </div>
                            </div>

                            <p className="text-slate-200 mb-4">{activeJob.description}</p>

                            {activeJob.location && (
                                <div className="flex items-center mb-3 text-slate-400">
                                    <MapPin className="h-5 w-5 mr-2 text-slate-500" />
                                    <span className="text-slate-300">{activeJob.location}</span>
                                </div>
                            )}
                        </div>

                        {/* Verification Plan */}
                        <div className="glass border border-slate-800 rounded-2xl p-6 mb-6">
                            <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                                <ClipboardCheck className="w-5 h-5 text-cyan-500" />
                                Verification Plan
                            </h3>

                            {activeJob.verification_plan ? (
                                <div className="space-y-4">
                                    {/* Task Category */}
                                    {activeJob.verification_plan.task_category && (
                                        <div className="mb-3">
                                            <span className="inline-block px-3 py-1 bg-cyan-900/30 text-cyan-400 rounded-full text-xs font-medium border border-cyan-800">
                                                {activeJob.verification_plan.task_category}
                                            </span>
                                        </div>
                                    )}

                                    {/* Success Criteria */}
                                    {activeJob.verification_plan.success_criteria && activeJob.verification_plan.success_criteria.length > 0 && (
                                        <div>
                                            <h4 className="text-sm font-medium text-green-400 mb-2 uppercase tracking-wider">✓ Success Criteria</h4>
                                            <ul className="space-y-2">
                                                {activeJob.verification_plan.success_criteria.map((item: string, i: number) => (
                                                    <li key={i} className="flex items-start text-slate-300 text-sm">
                                                        <span className="mr-2 text-green-500">•</span>
                                                        {item}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}

                                    {/* Visual Checks */}
                                    {activeJob.verification_plan.visual_checks && activeJob.verification_plan.visual_checks.length > 0 && (
                                        <div>
                                            <h4 className="text-sm font-medium text-cyan-400 mb-2 uppercase tracking-wider">👁️ Visual Checks</h4>
                                            <ul className="space-y-2">
                                                {activeJob.verification_plan.visual_checks.map((item: string, i: number) => (
                                                    <li key={i} className="flex items-start text-slate-300 text-sm">
                                                        <span className="mr-2 text-cyan-500">•</span>
                                                        {item}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}

                                    {/* Rejection Criteria */}
                                    {activeJob.verification_plan.rejection_criteria && activeJob.verification_plan.rejection_criteria.length > 0 && (
                                        <div>
                                            <h4 className="text-sm font-medium text-red-400 mb-2 uppercase tracking-wider">✗ Rejection Criteria</h4>
                                            <ul className="space-y-2">
                                                {activeJob.verification_plan.rejection_criteria.map((item: string, i: number) => (
                                                    <li key={i} className="flex items-start text-slate-300 text-sm">
                                                        <span className="mr-2 text-red-500">•</span>
                                                        {item}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}

                                    {/* Additional Info */}
                                    <div className="flex items-center gap-4 text-xs text-slate-400 pt-2 border-t border-slate-700">
                                        {activeJob.verification_plan.location_required && (
                                            <span className="flex items-center gap-1">
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                                </svg>
                                                Location Required
                                            </span>
                                        )}
                                        {activeJob.verification_plan.comparison_mode && (
                                            <span className="flex items-center gap-1">
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                                </svg>
                                                {activeJob.verification_plan.comparison_mode.replace('_', ' ')}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            ) : (
                                <p className="text-slate-400 text-sm italic">No verification plan available.</p>
                            )}
                        </div>

                        {/* Job Lifecycle Timeline - Show if work has been submitted */}
                        {(activeJob.status !== 'IN_PROGRESS' || (activeJob.proof_photos && activeJob.proof_photos.length > 0)) && (
                            <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-800 mb-6">
                                <h3 className="text-white font-semibold mb-6 flex items-center">
                                    <svg className="w-5 h-5 mr-2 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                    </svg>
                                    Job Progress
                                </h3>

                                <div className="space-y-4">
                                    {getJobTimeline(activeJob).map((stage, index, arr) => (
                                        <div key={stage.id} className="flex items-start gap-4">
                                            {/* Icon */}
                                            <div className="flex flex-col items-center">
                                                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold transition-all ${stage.status === 'completed'
                                                    ? 'bg-green-500/20 text-green-400 border-2 border-green-500'
                                                    : stage.status === 'current'
                                                        ? 'bg-blue-500/20 text-blue-400 border-2 border-blue-500 animate-pulse'
                                                        : 'bg-slate-800/50 text-slate-600 border-2 border-slate-700'
                                                    }`}>
                                                    {stage.icon}
                                                </div>
                                                {index < arr.length - 1 && (
                                                    <div className={`w-0.5 h-12 mt-2 ${stage.status === 'completed' ? 'bg-green-500/50' : 'bg-slate-700'
                                                        }`} />
                                                )}
                                            </div>

                                            {/* Content */}
                                            <div className="flex-1 pb-4">
                                                <h4 className={`font-medium mb-1 ${stage.status === 'completed' ? 'text-green-400' :
                                                    stage.status === 'current' ? 'text-blue-400' :
                                                        'text-slate-500'
                                                    }`}>
                                                    {stage.label}
                                                </h4>
                                                <p className={`text-sm ${stage.status === 'completed' ? 'text-slate-400' :
                                                    stage.status === 'current' ? 'text-slate-300' :
                                                        'text-slate-600'
                                                    }`}>
                                                    {stage.description}
                                                </p>

                                                {/* Special handling for payment pending */}
                                                {stage.id === 'payment' && stage.status === 'current' && activeJob.status === 'PAYMENT_PENDING' && (
                                                    <div className="mt-3 space-y-2">
                                                        <div className="flex items-center gap-2">
                                                            <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                                                                <div className="h-full bg-blue-500 rounded-full animate-pulse" style={{ width: '60%' }} />
                                                            </div>
                                                            <span className="text-xs text-slate-400 whitespace-nowrap">~2-5 min</span>
                                                        </div>
                                                        {activeJob.tx_hash && (
                                                            <a
                                                                href={`https://dora.coz.io/transaction/neo3/testnet/${activeJob.tx_hash}`}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="text-xs text-cyan-500 hover:text-cyan-400 flex items-center gap-1"
                                                            >
                                                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                                                </svg>
                                                                View on blockchain explorer
                                                            </a>
                                                        )}
                                                        <div className="flex gap-2">
                                                            <button
                                                                onClick={fetchData}
                                                                className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg transition-all"
                                                            >
                                                                🔄 Refresh status
                                                            </button>
                                                            <button
                                                                onClick={async () => {
                                                                    try {
                                                                        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/jobs/${activeJob.job_id}/verify-payment`, {
                                                                            method: 'POST'
                                                                        });
                                                                        const data = await response.json();

                                                                        if (data.synced) {
                                                                            toast.success(data.action_taken || 'Payment verified!');
                                                                            await fetchData();
                                                                        } else {
                                                                            toast(data.action_taken || 'Payment still processing', {
                                                                                icon: 'ℹ️',
                                                                            });
                                                                        }
                                                                    } catch (error) {
                                                                        toast.error('Failed to verify payment status');
                                                                    }
                                                                }}
                                                                className="text-xs bg-cyan-800 hover:bg-cyan-700 text-cyan-300 px-3 py-1.5 rounded-lg transition-all"
                                                            >
                                                                🔍 Check payment status
                                                            </button>
                                                        </div>
                                                    </div>
                                                )}

                                                {/* Show verdict for verification stage */}
                                                {stage.id === 'verification' && activeJob.verification_summary && (
                                                    <div className="mt-2 space-y-2">
                                                        <div className={`p-3 rounded-lg text-sm ${activeJob.verification_summary.verified
                                                            ? 'bg-green-900/20 border border-green-800 text-green-300'
                                                            : 'bg-red-900/20 border border-red-800 text-red-300'
                                                            }`}>
                                                            {activeJob.verification_summary.verdict}
                                                        </div>
                                                        <button
                                                            onClick={() => {
                                                                loadVerificationThinking(activeJob);
                                                                setShowVerificationModal(true);
                                                            }}
                                                            className="flex items-center gap-2 text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
                                                        >
                                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                                            </svg>
                                                            View AI thinking process
                                                        </button>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Show submission form if job is IN_PROGRESS or DISPUTED (allow resubmission) */}
                        {(activeJob.status === 'IN_PROGRESS' || activeJob.status === 'DISPUTED') && (
                            <div className="border-t border-slate-700 pt-6">
                                <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                                    <Send className="w-5 h-5 text-cyan-400" />
                                    {activeJob.status === 'DISPUTED' ? 'Resubmit Proof of Completion' : 'Submit Proof of Completion'}
                                </h3>
                                <p className="text-slate-400 text-sm mb-4">
                                    {activeJob.status === 'DISPUTED'
                                        ? 'Your previous submission was disputed. Please upload new photos addressing the issues.'
                                        : 'Upload photos showing the completed work to receive payment.'}
                                </p>

                                <ImageUpload
                                    images={proofImages}
                                    onAdd={handleAddImage}
                                    onRemove={handleRemoveImage}
                                    maxImages={4}
                                    label="Proof Photos"
                                />

                                <button
                                    onClick={handleSubmit}
                                    disabled={isSubmitting || proofImages.length === 0}
                                    className={`w-full mt-4 flex items-center justify-center gap-2 font-semibold py-3.5 rounded-xl transition-all active:scale-95 ${isSubmitting || proofImages.length === 0
                                        ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                                        : 'bg-gradient-to-r from-green-600 to-cyan-600 hover:from-green-500 hover:to-cyan-500 text-white hover:shadow-lg hover:shadow-green-500/30'
                                        }`}
                                >
                                    {isSubmitting ? (
                                        <>
                                            <Loader2 className="w-5 h-5 animate-spin" />
                                            Submitting...
                                        </>
                                    ) : (
                                        <>
                                            <Send className="w-5 h-5" />
                                            Submit for Verification
                                        </>
                                    )}
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Verification Thinking Modal */}
            {showVerificationModal && (
                <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200 p-4">
                    <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-3xl w-full max-h-[85vh] overflow-hidden shadow-2xl animate-in zoom-in duration-200">
                        {/* Header */}
                        <div className="bg-gradient-to-r from-cyan-900/50 to-blue-900/50 border-b border-slate-700 p-6 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="bg-cyan-500/20 p-3 rounded-full">
                                    <svg className="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                                    </svg>
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-white">AI Verification Process</h3>
                                    <p className="text-sm text-slate-400">How the AI verified your work</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setShowVerificationModal(false)}
                                className="text-slate-400 hover:text-white transition-colors p-2 hover:bg-slate-800 rounded-lg"
                            >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>

                        {/* Content */}
                        <div className="overflow-y-auto p-6" style={{ maxHeight: 'calc(85vh - 100px)' }}>
                            <div className="space-y-3">
                                {verificationThinking.map((step, index) => {
                                    const isHeader = step.startsWith('🔍') || step.startsWith('🖼️') || step.startsWith('✅ Step') || step.startsWith('⚖️');
                                    const isSuccess = step.includes('✅') || step.includes('✓');
                                    const isError = step.includes('❌');
                                    const isSubItem = step.startsWith('   ');

                                    return (
                                        <div
                                            key={index}
                                            className={`animate-in slide-in-from-left duration-300 ${isHeader
                                                ? 'font-semibold text-white text-base mt-4 first:mt-0'
                                                : isSubItem
                                                    ? 'text-slate-300 text-sm ml-4 pl-4 border-l-2 border-slate-700'
                                                    : 'text-slate-300 text-sm'
                                                } ${isSuccess ? 'text-green-400' : isError ? 'text-red-400' : ''
                                                }`}
                                            style={{ animationDelay: `${index * 50}ms` }}
                                        >
                                            {step}
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Summary Card */}
                            {activeJob.verification_summary && (
                                <div className={`mt-6 p-4 rounded-xl border-2 ${activeJob.verification_summary.verified
                                    ? 'bg-green-900/20 border-green-700'
                                    : 'bg-red-900/20 border-red-700'
                                    }`}>
                                    <div className="flex items-start justify-between mb-3">
                                        <div>
                                            <h4 className={`font-bold text-lg ${activeJob.verification_summary.verified ? 'text-green-400' : 'text-red-400'
                                                }`}>
                                                {activeJob.verification_summary.verified ? '✅ Work Approved' : '❌ Work Rejected'}
                                            </h4>
                                            <p className="text-slate-300 text-sm mt-1">
                                                {activeJob.verification_summary.verdict}
                                            </p>
                                        </div>
                                        <div className={`px-3 py-1 rounded-full font-bold ${activeJob.verification_summary.verified
                                            ? 'bg-green-500/20 text-green-400'
                                            : 'bg-red-500/20 text-red-400'
                                            }`}>
                                            {activeJob.verification_summary.score}/10
                                        </div>
                                    </div>

                                    {/* Additional Details */}
                                    {activeJob.verification_summary.comparison && (
                                        <div className="mt-3 pt-3 border-t border-slate-700">
                                            <p className="text-xs text-slate-400 uppercase font-semibold mb-2">Verification Details</p>
                                            <div className="grid grid-cols-2 gap-2 text-sm">
                                                <div className="flex items-center gap-2">
                                                    {activeJob.verification_summary.comparison.same_location ? '✓' : '✗'}
                                                    <span className="text-slate-300">Location Match</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    {activeJob.verification_summary.comparison.transformation_occurred ? '✓' : '✗'}
                                                    <span className="text-slate-300">Work Transformation</span>
                                                </div>
                                                {activeJob.verification_summary.gps_verification && (
                                                    <div className="flex items-center gap-2">
                                                        {activeJob.verification_summary.gps_verification.location_match ? '✓' : '✗'}
                                                        <span className="text-slate-300">
                                                            GPS ({activeJob.verification_summary.gps_verification.distance_meters?.toFixed(0)}m)
                                                        </span>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Footer */}
                        <div className="border-t border-slate-700 p-4 bg-slate-900/50">
                            <button
                                onClick={() => setShowVerificationModal(false)}
                                className="w-full bg-slate-800 hover:bg-slate-700 text-white font-semibold py-3 rounded-lg transition-all"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Location Permission Modal */}
            {showLocationModal && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
                    <div className="bg-slate-900 border border-slate-700 rounded-2xl p-8 max-w-md mx-4 shadow-2xl animate-in zoom-in duration-200">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="bg-cyan-500/20 p-3 rounded-full">
                                <MapPin className="h-6 w-6 text-cyan-400" />
                            </div>
                            <h3 className="text-xl font-bold text-white">Location Required</h3>
                        </div>

                        <p className="text-slate-300 mb-6">
                            To verify your work authentically, we need to confirm you're at the job location.
                            Please allow location access to submit your proof of work.
                        </p>

                        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 mb-6">
                            <div className="flex items-start gap-2">
                                <Info className="h-5 w-5 text-cyan-400 mt-0.5 flex-shrink-0" />
                                <p className="text-sm text-slate-400">
                                    Your location is only used for this verification and is not stored permanently.
                                </p>
                            </div>
                        </div>

                        <div className="flex gap-3">
                            <button
                                onClick={() => {
                                    setShowLocationModal(false);
                                    setPendingSubmit(false);
                                }}
                                className="flex-1 px-4 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleRequestLocation}
                                className="flex-1 px-4 py-3 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors font-semibold"
                            >
                                Allow Location
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Getting Location Loading Modal */}
            {isGettingLocation && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
                    <div className="bg-slate-900 border border-slate-700 rounded-2xl p-8 max-w-md mx-4 shadow-2xl text-center">
                        <div className="flex justify-center mb-4">
                            <Loader2 className="h-12 w-12 text-cyan-400 animate-spin" />
                        </div>
                        <h3 className="text-xl font-bold text-white mb-2">Getting Your Location</h3>
                        <p className="text-slate-400">Please wait while we detect your current location...</p>
                    </div>
                </div>
            )}

            {/* Location Preview Modal */}
            {showLocationPreview && detectedLocation && activeJob && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
                    <div className="bg-slate-900 border border-slate-700 rounded-2xl p-8 max-w-md mx-4 shadow-2xl animate-in zoom-in duration-200">
                        {(() => {
                            const distance = calculateDistance(
                                detectedLocation.lat,
                                detectedLocation.lng,
                                activeJob.latitude,
                                activeJob.longitude
                            );
                            const isNearby = distance <= 300;

                            return (
                                <>
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className={`p-3 rounded-full ${isNearby ? 'bg-green-500/20' : 'bg-yellow-500/20'}`}>
                                            <MapPinned className={`h-6 w-6 ${isNearby ? 'text-green-400' : 'text-yellow-400'}`} />
                                        </div>
                                        <h3 className="text-xl font-bold text-white">Confirm Your Location</h3>
                                    </div>

                                    {/* Location Details */}
                                    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 mb-4 space-y-3">
                                        <div className="flex justify-between items-center">
                                            <span className="text-slate-400 text-sm">Your Location</span>
                                            <span className="text-white text-sm font-mono">
                                                {detectedLocation.lat.toFixed(6)}, {detectedLocation.lng.toFixed(6)}
                                            </span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-slate-400 text-sm">Accuracy</span>
                                            <span className="text-white text-sm">±{detectedLocation.accuracy.toFixed(0)}m</span>
                                        </div>
                                        <div className="flex justify-between items-center border-t border-slate-700 pt-3">
                                            <span className="text-slate-400 text-sm">Distance to Job</span>
                                            <span className={`text-sm font-bold ${isNearby ? 'text-green-400' : 'text-yellow-400'}`}>
                                                {distance < 1000 ? `${distance.toFixed(0)}m` : `${(distance / 1000).toFixed(2)}km`}
                                            </span>
                                        </div>
                                    </div>

                                    {/* Status Message */}
                                    {isNearby ? (
                                        <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4 mb-6">
                                            <div className="flex items-start gap-2">
                                                <CheckCircle className="h-5 w-5 text-green-400 mt-0.5 flex-shrink-0" />
                                                <p className="text-sm text-green-300">
                                                    You're within 300m of the job location. Ready to submit!
                                                </p>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 mb-6">
                                            <div className="flex items-start gap-2">
                                                <AlertTriangle className="h-5 w-5 text-yellow-400 mt-0.5 flex-shrink-0" />
                                                <div>
                                                    <p className="text-sm text-yellow-300 font-medium">
                                                        You appear to be {distance.toFixed(0)}m away from the job location.
                                                    </p>
                                                    <p className="text-sm text-yellow-200/70 mt-1">
                                                        Submissions more than 300m away may be rejected. Make sure you're at the right location.
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    <div className="flex gap-3">
                                        <button
                                            onClick={handleRetryLocation}
                                            className="flex-1 px-4 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
                                        >
                                            <RefreshCw className="h-4 w-4" />
                                            Retry
                                        </button>
                                        <button
                                            onClick={handleConfirmLocation}
                                            className={`flex-1 px-4 py-3 text-white rounded-lg transition-colors font-semibold flex items-center justify-center gap-2 ${isNearby
                                                    ? 'bg-green-600 hover:bg-green-500'
                                                    : 'bg-yellow-600 hover:bg-yellow-500'
                                                }`}
                                        >
                                            <CheckCircle2 className="h-4 w-4" />
                                            Confirm & Submit
                                        </button>
                                    </div>
                                </>
                            );
                        })()}
                    </div>
                </div>
            )}
        </div>
    );
}
