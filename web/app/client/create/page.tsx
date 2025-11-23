'use client';

import { useState } from 'react';
import { useApp } from '@/context/AppContext';
import LocationPicker from '@/components/LocationPicker';
import ImageUpload from '@/components/ImageUpload';
import { apiClient } from '@/lib/api';

export default function CreateJobPage() {
    const { state, setJobDescription, setJobLocation, addUploadedImage, removeUploadedImage } = useApp();

    const [isDrafting, setIsDrafting] = useState(false);
    const [isCreating, setIsCreating] = useState(false);
    const [draftCriteria, setDraftCriteria] = useState('');
    const [draftPrice, setDraftPrice] = useState(0);
    const [draftMessage, setDraftMessage] = useState('');
    const [progress, setProgress] = useState(0);
    const [logs, setLogs] = useState<string[]>([]);

    const handleLocationChange = (address: string, lat: number, lng: number) => {
        setJobLocation(address, lat, lng);
    };

    const handleDraftContract = async () => {
        // Validate inputs
        if (!state.jobDescription) {
            alert('Please enter job description');
            return;
        }
        if (!state.clientUploadedImages.length) {
            alert('Please upload at least one reference photo');
            return;
        }
        if (!state.jobLocation || state.jobLatitude === 0 || state.jobLongitude === 0) {
            alert('Please select a location from the dropdown suggestions');
            return;
        }

        setIsDrafting(false);
        setIsCreating(true);
        setLogs(['Analyzing request with AI...']);
        setProgress(0.05);

        try {
            // Call AI analysis
            const formData = new FormData();
            formData.append('message', state.jobDescription);
            formData.append('location', state.jobLocation);

            // In production, you'd upload the actual file here
            // For now, we'll use a placeholder
            const blob = new Blob(['placeholder'], { type: 'image/jpeg' });
            formData.append('reference_image', blob, state.clientUploadedImages[0]);

            const result = await apiClient.analyzeJob(formData);

            if (result.valid === false) {
                alert(result.message || 'AI analysis failed. Please refine your request.');
                setIsCreating(false);
                return;
            }

            setDraftCriteria(result.data?.acceptance_criteria || result.acceptance_criteria || '');
            setDraftPrice(result.data?.suggested_price || result.suggested_price || 5.0);
            setDraftMessage(result.message || 'Draft ready for review');
            setIsDrafting(true);
            setProgress(0.15);
            setIsCreating(false);
            setLogs([...logs, 'AI criteria attached to job details']);
        } catch (error) {
            console.error('Draft error:', error);
            alert('Network error during AI analysis');
            setIsCreating(false);
        }
    };

    const handleConfirmCreate = async () => {
        setIsCreating(true);
        setProgress(0.20);
        setLogs([...logs, 'Uploading images to IPFS...']);

        try {
            // In production, upload images to IPFS
            // For now, use placeholder URLs
            const ipfsUrls = state.clientUploadedImages.map(
                (_, i) => `ipfs://placeholder-${i}`
            );

            setProgress(0.35);
            setLogs([...logs, 'Creating job (DB + blockchain)...']);

            const payload = {
                client_address: state.walletAddress,
                description: state.jobDescription,
                reference_photos: ipfsUrls,
                location: state.jobLocation,
                latitude: state.jobLatitude,
                longitude: state.jobLongitude,
                amount: draftPrice > 0 ? draftPrice : 5.0,
            };

            console.log('Creating job:', payload);

            const result = await apiClient.createJob(payload);

            if (result.job) {
                setProgress(0.50);
                setLogs([...logs, `Submitted tx: ${result.job.tx_hash}`]);

                // Wait for confirmation
                await new Promise(resolve => setTimeout(resolve, 3000));

                setProgress(1.0);
                alert(`Job created successfully! ID: ${result.job.job_id}`);

                // Reset form
                setJobDescription('');
                setJobLocation('', 0, 0);
                while (state.clientUploadedImages.length > 0) {
                    removeUploadedImage(0);
                }
                setIsDrafting(false);
                setDraftCriteria('');
                setDraftPrice(0);
            } else {
                throw new Error('Failed to create job');
            }
        } catch (error) {
            console.error('Create error:', error);
            alert('Failed to create job');
        } finally {
            setIsCreating(false);
        }
    };

    return (
        <div className="animate-in fade-in duration-500">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-white mb-2">Create New Job</h2>
                <p className="text-slate-400">
                    Define the task and payment for your blockchain-secured gig.
                </p>
            </div>

            <div className="bg-slate-950/50 rounded-3xl p-8 border border-slate-800">
                {/* Job Description */}
                <div className="mb-6">
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                        Job Description
                    </label>
                    <textarea
                        value={state.jobDescription}
                        onChange={(e) => setJobDescription(e.target.value)}
                        placeholder="Describe your task details, requirements, expectations, and payment amount (e.g., 'Clean the garage and organize all tools on shelves. Will pay 5 GAS.')..."
                        className="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-4 text-slate-200 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none min-h-[150px] transition-all placeholder:text-slate-600 text-sm"
                    />
                </div>

                {/* Location Picker */}
                <LocationPicker
                    value={state.jobLocation}
                    onChange={handleLocationChange}
                />

                {/* Image Upload */}
                <ImageUpload
                    images={state.clientUploadedImages}
                    onAdd={addUploadedImage}
                    onRemove={removeUploadedImage}
                />

                {/* Action Buttons */}
                <div className="flex justify-end">
                    {isDrafting ? (
                        <>
                            <button
                                onClick={handleConfirmCreate}
                                disabled={isCreating}
                                className="mr-3 bg-green-600 text-white font-semibold py-3 px-6 rounded-xl hover:bg-green-500 transition-all disabled:opacity-50"
                            >
                                Confirm & Create
                            </button>
                            <button
                                onClick={() => setIsDrafting(false)}
                                disabled={isCreating}
                                className="bg-slate-700 text-white font-semibold py-3 px-6 rounded-xl hover:bg-slate-600 transition-all disabled:opacity-50"
                            >
                                Edit
                            </button>
                        </>
                    ) : (
                        <button
                            onClick={handleDraftContract}
                            disabled={isCreating}
                            className="flex items-center justify-center bg-gradient-to-r from-cyan-500 to to-blue-600 text-white font-semibold py-3 px-8 rounded-xl hover:shadow-lg hover:shadow-cyan-500/20 transition-all active:scale-95 disabled:opacity-50"
                        >
                            {isCreating ? 'Processing...' : (
                                <>
                                    Draft Contract
                                    <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                    </svg>
                                </>
                            )}
                        </button>
                    )}
                </div>

                {/* Draft Preview & Progress */}
                <div className="mt-4 p-4 bg-slate-900 rounded-xl border border-slate-800">
                    {isDrafting && (
                        <div className="mb-4">
                            <h3 className="text-slate-200 text-sm font-semibold mb-2">Contract Preview</h3>
                            {draftCriteria && (
                                <div className="mb-3">
                                    <p className="text-xs text-slate-400 mb-1">Acceptance Criteria:</p>
                                    <pre className="text-xs text-slate-300 whitespace-pre-wrap bg-slate-800 p-3 rounded">
                                        {draftCriteria}
                                    </pre>
                                </div>
                            )}
                            {draftPrice > 0 && (
                                <div className="mb-3">
                                    <p className="text-xs text-slate-400 mb-1">Suggested Price:</p>
                                    <span className="text-xs text-slate-300">{draftPrice} GAS</span>
                                </div>
                            )}
                            {draftMessage && (
                                <div className="text-xs text-slate-400">{draftMessage}</div>
                            )}
                        </div>
                    )}

                    <progress
                        value={progress}
                        max={1}
                        className="w-full h-2 bg-slate-800 rounded overflow-hidden mb-3"
                    />

                    {logs.map((line, i) => (
                        <div key={i} className="text-xs text-slate-400 mb-1">{line}</div>
                    ))}
                </div>
            </div>
        </div>
    );
}
