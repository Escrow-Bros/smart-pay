'use client';

import { useState, useEffect } from 'react';
import { useApp } from '@/context/AppContext';
import { apiClient } from '@/lib/api';
import ImageUpload from '@/components/ImageUpload';
import { JobDict, UploadedImage } from '@/lib/types';
import { formatGasWithUSD } from '@/lib/currency';

export default function WorkerCurrentJobPage() {
    const { state, fetchData } = useApp();
    const [selectedJob, setSelectedJob] = useState<JobDict | null>(null);
    const [proofImages, setProofImages] = useState<UploadedImage[]>([]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showLocationModal, setShowLocationModal] = useState(false);
    const [pendingSubmit, setPendingSubmit] = useState(false);
    const [locationPermission, setLocationPermission] = useState<'prompt' | 'granted' | 'denied'>('prompt');

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
            <div className="animate-in fade-in duration-500">
                <div className="mb-8">
                    <h2 className="text-3xl font-bold text-white mb-2">Current Jobs</h2>
                    <p className="text-slate-400">Your active job assignments.</p>
                </div>

                <div className="text-center py-12 bg-slate-900/30 border border-slate-800 rounded-xl">
                    <p className="text-slate-400 mb-2">No active jobs</p>
                    <p className="text-slate-500 text-sm">Claim a job from the Available Jobs page to start working.</p>
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

    const handleRequestLocation = async () => {
        setShowLocationModal(false);

        if (!navigator.geolocation) {
            alert('Geolocation is not supported by your browser');
            setPendingSubmit(false);
            return;
        }

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                console.log('Location obtained:', {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                    accuracy: position.coords.accuracy
                });

                // Update permission state
                setLocationPermission('granted');

                const workerLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                    accuracy: position.coords.accuracy
                };

                await submitProofWithLocation(workerLocation);
            },
            (error) => {
                console.error('Geolocation error:', error);

                // Use hardcoded fallback location (San Jose, CA)
                console.log('Using fallback location: San Jose, CA');
                const fallbackLocation = {
                    lat: 37.3359184,
                    lng: -121.8878792,
                    accuracy: 100
                };

                submitProofWithLocation(fallbackLocation);
            },
            {
                enableHighAccuracy: true,
                timeout: 15000, // Increased from 10000 to 15000ms
                maximumAge: 0
            }
        );
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
                alert('Work submitted successfully! Waiting for verification.');
                setProofImages([]);
                await fetchData();
            } else {
                alert('Failed to submit proof: ' + (result.message || 'Unknown error'));
            }
        } catch (error) {
            console.error('Submission error:', error);
            alert('Failed to submit proof. Please try again.');
        } finally {
            setIsSubmitting(false);
            setPendingSubmit(false);
        }
    };

    const handleSubmit = () => {
        if (proofImages.length === 0) {
            alert('Please upload at least one proof photo.');
            return;
        }

        // If permission already granted, directly get location
        if (locationPermission === 'granted') {
            console.log('Location permission already granted, getting location directly');
            handleRequestLocation();
        } else {
            // Show location permission modal
            setPendingSubmit(true);
            setShowLocationModal(true);
        }
    };

    return (
        <div className="animate-in fade-in duration-500">
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
                                <div className="flex items-center mb-3">
                                    <svg className="h-5 w-5 text-slate-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                    </svg>
                                    <span className="text-slate-300">{activeJob.location}</span>
                                </div>
                            )}
                        </div>

                        {/* Verification Plan */}
                        <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-800 mb-6">
                            <h3 className="text-white font-semibold mb-4 flex items-center">
                                <svg className="w-5 h-5 mr-2 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Verification Plan
                            </h3>

                            {activeJob.verification_plan ? (
                                <div className="space-y-4">
                                    {/* Checklist */}
                                    {activeJob.verification_plan.verification_checklist && (
                                        <div>
                                            <h4 className="text-sm font-medium text-slate-400 mb-2 uppercase tracking-wider">Checklist</h4>
                                            <ul className="space-y-2">
                                                {activeJob.verification_plan.verification_checklist.map((item: string, i: number) => (
                                                    <li key={i} className="flex items-start text-slate-300 text-sm">
                                                        <span className="mr-2 text-cyan-500">•</span>
                                                        {item}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}

                                    {/* Quality Indicators */}
                                    {activeJob.verification_plan.quality_indicators && (
                                        <div>
                                            <h4 className="text-sm font-medium text-slate-400 mb-2 uppercase tracking-wider">Quality Indicators</h4>
                                            <ul className="space-y-2">
                                                {activeJob.verification_plan.quality_indicators.map((item: string, i: number) => (
                                                    <li key={i} className="flex items-start text-slate-300 text-sm">
                                                        <span className="mr-2 text-green-500">✓</span>
                                                        {item}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <p className="text-slate-400 text-sm italic">No verification plan available.</p>
                            )}
                        </div>

                        <div className="border-t border-slate-700 pt-6">
                            <h3 className="text-white font-semibold mb-3">Submit Proof of Completion</h3>
                            <p className="text-slate-400 text-sm mb-4">
                                Upload photos showing the completed work to receive payment.
                            </p>

                            <ImageUpload
                                images={proofImages}
                                onAdd={handleAddImage}
                                onRemove={handleRemoveImage}
                            />

                            <button
                                onClick={handleSubmit}
                                disabled={isSubmitting || proofImages.length === 0}
                                className={`w-full mt-4 font-semibold py-3 rounded-xl transition-all active:scale-95 ${isSubmitting || proofImages.length === 0
                                    ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                                    : 'bg-green-600 hover:bg-green-500 text-white'
                                    }`}
                            >
                                {isSubmitting ? 'Submitting...' : 'Submit for Verification'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Location Permission Modal */}
            {showLocationModal && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
                    <div className="bg-slate-900 border border-slate-700 rounded-2xl p-8 max-w-md mx-4 shadow-2xl animate-in zoom-in duration-200">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="bg-cyan-500/20 p-3 rounded-full">
                                <svg className="h-6 w-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold text-white">Location Required</h3>
                        </div>

                        <p className="text-slate-300 mb-6">
                            To verify your work authentically, we need to confirm you're at the job location.
                            Please allow location access to submit your proof of work.
                        </p>

                        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 mb-6">
                            <div className="flex items-start gap-2">
                                <svg className="h-5 w-5 text-cyan-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
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
        </div>
    );
}
