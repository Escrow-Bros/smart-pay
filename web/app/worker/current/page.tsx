'use client';

import { useState } from 'react';
import { useApp } from '@/context/AppContext';
import { apiClient } from '@/lib/api';
import ImageUpload from '@/components/ImageUpload';

export default function WorkerCurrentJobPage() {
    const { state } = useApp();

    if (!state.currentJob) {
        return (
            <div className="animate-in fade-in duration-500">
                <div className="mb-8">
                    <h2 className="text-3xl font-bold text-white mb-2">Current Job</h2>
                    <p className="text-slate-400">Your active job assignment.</p>
                </div>

                <div className="text-center py-12 bg-slate-900/30 border border-slate-800 rounded-xl">
                    <p className="text-slate-400 mb-2">No active job</p>
                    <p className="text-slate-500 text-sm">Claim a job from the Available Jobs page to start working.</p>
                </div>
            </div>
        );
    }

    const job = state.currentJob;
    const [proofImages, setProofImages] = useState<{ file: File; preview: string }[]>([]);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleAddImage = (file: File) => {
        const preview = URL.createObjectURL(file);
        setProofImages(prev => [...prev, { file, preview }]);
    };

    const handleRemoveImage = (index: number) => {
        setProofImages(prev => prev.filter((_, i) => i !== index));
    };

    const handleSubmit = async () => {
        if (proofImages.length === 0) {
            alert('Please upload at least one proof photo.');
            return;
        }

        setIsSubmitting(true);
        try {
            // 1. Get Location (Mandatory)
            const getLocation = (): Promise<GeolocationPosition> => {
                return new Promise((resolve, reject) => {
                    if (!navigator.geolocation) {
                        reject(new Error('Geolocation is not supported by your browser'));
                    } else {
                        navigator.geolocation.getCurrentPosition(resolve, reject, {
                            enableHighAccuracy: true,
                            timeout: 10000,
                            maximumAge: 0
                        });
                    }
                });
            };

            let locationData = null;
            try {
                const position = await getLocation();
                locationData = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                    accuracy: position.coords.accuracy
                };
            } catch (locError) {
                console.error('Location error:', locError);
                alert('Location access is required to verify your work. Please enable location services and try again.');
                setIsSubmitting(false);
                return;
            }

            // 2. Upload images to IPFS
            const ipfsUrls = await Promise.all(
                proofImages.map(async (img) => {
                    return await apiClient.uploadToIpfs(img.file);
                })
            );

            // 3. Submit proof with location
            await apiClient.submitProof(job.job_id, ipfsUrls, locationData);

            alert('Proof submitted successfully! Waiting for verification.');
            // Refresh data
            window.location.reload();
        } catch (error) {
            console.error('Submission failed:', error);
            alert('Failed to submit proof. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="animate-in fade-in duration-500">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-white mb-2">Current Job</h2>
                <p className="text-slate-400">Complete your work and submit proof to get paid.</p>
            </div>

            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-8">
                <div className="mb-6">
                    <div className="flex justify-between items-start mb-4">
                        <span className="text-cyan-400 font-semibold text-lg">Job #{job.job_id}</span>
                        <span className="text-green-400 font-bold text-2xl">{job.amount} GAS</span>
                    </div>

                    <p className="text-slate-200 mb-4">{job.description}</p>

                    {job.location && (
                        <div className="flex items-center mb-3">
                            <svg className="h-5 w-5 text-slate-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                            </svg>
                            <span className="text-slate-300">{job.location}</span>
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

                    {job.verification_plan ? (
                        <div className="space-y-4">
                            {/* Checklist */}
                            {job.verification_plan.verification_checklist && (
                                <div>
                                    <h4 className="text-sm font-medium text-slate-400 mb-2 uppercase tracking-wider">Checklist</h4>
                                    <ul className="space-y-2">
                                        {job.verification_plan.verification_checklist.map((item: string, i: number) => (
                                            <li key={i} className="flex items-start text-slate-300 text-sm">
                                                <span className="mr-2 text-cyan-500">•</span>
                                                {item}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* Quality Indicators */}
                            {job.verification_plan.quality_indicators && (
                                <div>
                                    <h4 className="text-sm font-medium text-slate-400 mb-2 uppercase tracking-wider">Quality Indicators</h4>
                                    <ul className="space-y-2">
                                        {job.verification_plan.quality_indicators.map((item: string, i: number) => (
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
    );
}
