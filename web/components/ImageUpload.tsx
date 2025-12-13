'use client';

import { useState, useRef, useEffect } from 'react';
import { UploadedImage } from '@/lib/types';
import toast from 'react-hot-toast';
import { ImagePlus, X, Image, AlertCircle, Camera } from 'lucide-react';

interface ImageUploadProps {
    images: UploadedImage[];
    onAdd: (image: UploadedImage) => void;
    onRemove: (index: number) => void;
    maxImages?: number;
    label?: string;
}

export default function ImageUpload({
    images,
    onAdd,
    onRemove,
    maxImages = 4,
    label = "Reference Photos"
}: ImageUploadProps) {
    const [isDragging, setIsDragging] = useState(false);
    const pendingCountRef = useRef(0);

    // Camera state
    const [isCameraOpen, setIsCameraOpen] = useState(false);
    const videoRef = useRef<HTMLVideoElement>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const mountedRef = useRef(true);
    const dialogRef = useRef<HTMLDivElement>(null);

    // Track component mount status
    useEffect(() => {
        mountedRef.current = true;
        return () => {
            mountedRef.current = false;
        };
    }, []);

    // Cleanup stream on unmount
    useEffect(() => {
        return () => {
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
        };
    }, []);

    // Bind stream to video element when modal opens
    useEffect(() => {
        if (isCameraOpen && videoRef.current && streamRef.current) {
            videoRef.current.srcObject = streamRef.current;
        }
    }, [isCameraOpen]);

    // Handle escape key and focus trap
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (!isCameraOpen) return;

            if (e.key === 'Escape') {
                stopCamera();
                return;
            }

            if (e.key === 'Tab') {
                const modal = dialogRef.current;
                if (!modal) return;

                const focusableElements = modal.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                if (focusableElements.length === 0) return;

                const firstElement = focusableElements[0] as HTMLElement;
                const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }
            }
        };

        let previousActiveElement: HTMLElement | null = null;

        if (isCameraOpen) {
            previousActiveElement = document.activeElement as HTMLElement;
            window.addEventListener('keydown', handleKeyDown);

            // Focus first element when modal opens
            setTimeout(() => {
                const firstButton = dialogRef.current?.querySelector('button') as HTMLElement | null;
                firstButton?.focus();
            }, 50);

            return () => {
                window.removeEventListener('keydown', handleKeyDown);
                previousActiveElement?.focus();
            };
        }
    }, [isCameraOpen]);

    const remainingSlots = maxImages - images.length;
    const isAtLimit = remainingSlots <= 0;

    // Check for duplicate by filename + file size
    const isDuplicate = (file: File): boolean => {
        return images.some(img =>
            img.file.name === file.name && img.file.size === file.size
        );
    };

    const processFiles = (files: FileList) => {
        let added = 0;
        let skippedDuplicate = 0;
        let skippedLimit = 0;

        // Calculate effective count including pending uploads
        const effectiveCount = images.length + pendingCountRef.current;

        // Track seen files within this batch to prevent duplicates
        const seenKeys = new Set(
            images.map(img => `${img.file.name}-${img.file.size}`)
        );

        Array.from(files).forEach((file) => {
            const key = `${file.name}-${file.size}`;

            // Check file type
            if (!file.type.startsWith('image/')) {
                toast.error(`"${file.name}" is not an image file.`);
                return;
            }

            // Check file size (5MB limit)
            if (file.size > 5 * 1024 * 1024) {
                toast.error(`"${file.name}" exceeds the 5MB size limit.`);
                return;
            }

            // Check for duplicates (both existing and within this batch)
            if (seenKeys.has(key) || isDuplicate(file)) {
                skippedDuplicate++;
                return;
            }
            seenKeys.add(key);

            // Check limit with pending count
            if (effectiveCount + added >= maxImages) {
                skippedLimit++;
                return;
            }

            added++;
            pendingCountRef.current++;

            // Read and optimize ALL images
            const reader = new FileReader();
            reader.onload = () => {
                const img = new window.Image();
                img.onload = () => {
                    // Resize if too large (max 1600x1600 for good quality vs token balance)
                    const MAX_DIMENSION = 1600;
                    let width = img.width;
                    let height = img.height;

                    if (width > MAX_DIMENSION || height > MAX_DIMENSION) {
                        if (width > height) {
                            height = Math.round((height * MAX_DIMENSION) / width);
                            width = MAX_DIMENSION;
                        } else {
                            width = Math.round((width * MAX_DIMENSION) / height);
                            height = MAX_DIMENSION;
                        }
                    }

                    // Create canvas and compress
                    const canvas = document.createElement('canvas');
                    canvas.width = width;
                    canvas.height = height;
                    const ctx = canvas.getContext('2d');
                    if (!ctx) {
                        pendingCountRef.current--;
                        toast.error(`Failed to process "${file.name}". Please try again.`);
                        return;
                    }
                    ctx.drawImage(img, 0, 0, width, height);

                    // Compress to 85% quality JPEG
                    canvas.toBlob(
                        (blob) => {
                            if (!blob) {
                                console.error(`Failed to create blob for "${file.name}".`);
                                pendingCountRef.current--;
                                toast.error(`Failed to process "${file.name}". Please try again.`);
                                return;
                            }

                            pendingCountRef.current--;
                            const optimizedFile = new File([blob], file.name.replace(/\.\w+$/, '.jpg'), {
                                type: 'image/jpeg',
                            });
                            const preview = canvas.toDataURL('image/jpeg', 0.85);

                            onAdd({
                                file: optimizedFile,
                                preview,
                            });
                        },
                        'image/jpeg',
                        0.85
                    );
                };
                img.onerror = () => {
                    pendingCountRef.current--;
                    toast.error(`Failed to load "${file.name}". The image may be corrupted.`);
                };
                img.src = reader.result as string;
            };
            reader.onerror = () => {
                pendingCountRef.current--;
                toast.error(`Failed to read "${file.name}". Please try again.`);
            };
            reader.readAsDataURL(file);
        });

        // Show feedback for skipped files
        if (skippedDuplicate > 0) {
            toast.error(`${skippedDuplicate} duplicate image(s) skipped.`, { icon: '🔄' });
        }
        if (skippedLimit > 0) {
            toast.error(`${skippedLimit} image(s) skipped. Maximum ${maxImages} images allowed.`, { icon: '📷' });
        }
    };

    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment' } // Prefer rear camera on mobile
            });

            // Check if component is still mounted
            if (!mountedRef.current) {
                stream.getTracks().forEach(track => track.stop());
                return;
            }

            streamRef.current = stream;
            setIsCameraOpen(true);
        } catch (err) {
            console.error("Error accessing camera:", err);
            toast.error("Could not access camera. Please check permissions.");
        }
    };

    const stopCamera = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
        setIsCameraOpen(false);
    };

    const capturePhoto = () => {
        if (!videoRef.current) return;

        // Check if at limit
        if (images.length + pendingCountRef.current >= maxImages) {
            toast.error(`Maximum ${maxImages} images allowed.`);
            stopCamera();
            return;
        }

        // Validate video is ready
        if (videoRef.current.videoWidth === 0 || videoRef.current.videoHeight === 0) {
            toast.error("Camera not ready. Please try again.");
            return;
        }

        const canvas = document.createElement('canvas');
        canvas.width = videoRef.current.videoWidth;
        canvas.height = videoRef.current.videoHeight;
        const ctx = canvas.getContext('2d');
        if (!ctx) {
            toast.error("Failed to access canvas context. Please try again.");
            return;
        }

        ctx.drawImage(videoRef.current, 0, 0);

        canvas.toBlob((blob) => {
            if (!blob) {
                toast.error("Failed to capture photo.");
                return;
            }

            const file = new File([blob], `capture-${Date.now()}.jpg`, { type: 'image/jpeg' });

            // Re-use processFiles logic for consistency (resize, compress, add)
            // We wrap it in a DataTransfer to mimic file selection
            const dt = new DataTransfer();
            dt.items.add(file);
            processFiles(dt.files);

            stopCamera();
            toast.success("Photo captured!");
        }, 'image/jpeg', 0.9);
    };

    return (
        <div className="w-full">
            {/* Header with label and count */}
            <div className="flex items-center justify-between mb-3">
                <label className="text-sm sm:text-base font-medium text-slate-300">
                    {label}
                </label>
                <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${isAtLimit
                    ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                    : 'bg-slate-800/50 text-slate-400 border border-slate-700'
                    }`}>
                    <Image className="w-3.5 h-3.5" />
                    {images.length}/{maxImages}
                </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 justify-items-center sm:justify-items-start">
                {/* Upload Button */}
                {!isAtLimit && (
                    <div className="relative group aspect-square">
                        <input
                            type="file"
                            accept="image/*"
                            multiple
                            className={`
                                absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10
                                rounded-2xl border-2 border-dashed transition-all duration-300
                                ${isDragging
                                    ? 'border-cyan-500 bg-cyan-500/10 scale-95'
                                    : 'border-slate-700 bg-slate-800/30 hover:border-cyan-500/50 hover:bg-slate-800/50'
                                }
                            `}
                            aria-label="Add images"
                            onChange={(e) => {
                                if (e.target.files) {
                                    processFiles(e.target.files);
                                    e.target.value = ''; // Reset
                                }
                            }}
                            onDragOver={(e) => {
                                e.preventDefault();
                                setIsDragging(true);
                            }}
                            onDragLeave={() => setIsDragging(false)}
                            onDrop={(e) => {
                                e.preventDefault();
                                setIsDragging(false);
                                processFiles(e.dataTransfer.files);
                            }}
                        />
                        <div
                            className={`
                                w-full h-full rounded-2xl border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center gap-3
                                ${isDragging
                                    ? 'border-cyan-500 bg-cyan-500/10 scale-95'
                                    : 'border-slate-700 bg-slate-800/30 hover:border-cyan-500/50 hover:bg-slate-800/50'
                                }
                            `}
                        >
                            <div className="p-3 bg-slate-800 rounded-full group-hover:scale-110 transition-transform duration-300 shadow-lg shadow-black/20">
                                <ImagePlus className="w-6 h-6 text-cyan-400" />
                            </div>
                            <span className="text-xs font-medium text-slate-400 group-hover:text-cyan-400 transition-colors">
                                Upload
                            </span>
                        </div>
                    </div>
                )}

                {/* Camera Button */}
                {!isAtLimit && (
                    <button
                        onClick={startCamera}
                        className="relative group aspect-square rounded-2xl border-2 border-dashed border-slate-700 bg-slate-800/30 hover:border-purple-500/50 hover:bg-slate-800/50 transition-all duration-300 flex flex-col items-center justify-center gap-3"
                    >
                        <div className="p-3 bg-slate-800 rounded-full group-hover:scale-110 transition-transform duration-300 shadow-lg shadow-black/20">
                            <Camera className="w-6 h-6 text-purple-400" />
                        </div>
                        <span className="text-xs font-medium text-slate-400 group-hover:text-purple-400 transition-colors">
                            Take Photo
                        </span>
                    </button>
                )}

                {/* Image Previews */}
                {images.map((img, index) => (
                    <div
                        key={`${img.file.name}-${index}`}
                        className="group relative aspect-square rounded-2xl overflow-hidden bg-slate-800 border border-slate-700 shadow-lg animate-in zoom-in duration-300"
                    >
                        <img
                            src={img.preview}
                            alt={`Preview ${index + 1}`}
                            width={200}
                            height={200}
                            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                        />
                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                        <button
                            onClick={() => onRemove(index)}
                            className="absolute top-2 right-2 p-1.5 bg-red-500/80 hover:bg-red-500 rounded-lg transition-colors opacity-0 group-hover:opacity-100 focus-visible:opacity-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-red-400"
                            aria-label="Remove image"
                        >
                            <X className="w-4 h-4 text-white" />
                        </button>

                        <div className="absolute bottom-2 left-2 right-2 px-2 py-1 bg-black/60 backdrop-blur-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                            <p className="text-[10px] text-white truncate font-medium">
                                {img.file.name}
                            </p>
                            <p className="text-[9px] text-slate-300">
                                {(img.file.size / 1024).toFixed(1)} KB
                            </p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Camera Modal */}
            {
                isCameraOpen && (
                    <div
                        ref={dialogRef}
                        className="fixed inset-0 z-50 bg-black flex flex-col"
                        role="dialog"
                        aria-modal="true"
                        aria-label="Camera capture"
                    >
                        <div className="relative flex-1 bg-black flex items-center justify-center overflow-hidden">
                            <video
                                ref={videoRef}
                                autoPlay
                                playsInline
                                className="w-full h-full object-cover"
                            />

                            {/* Camera Overlay UI */}
                            <div className="absolute top-0 left-0 right-0 p-4 flex justify-between items-start bg-gradient-to-b from-black/50 to-transparent">
                                <button
                                    onClick={stopCamera}
                                    className="p-2 bg-black/40 backdrop-blur-md rounded-full text-white hover:bg-black/60 transition-colors"
                                >
                                    <X className="w-6 h-6" />
                                </button>
                                <div className="px-3 py-1 bg-red-500/80 backdrop-blur-md rounded-full flex items-center gap-2">
                                    <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                                    <span className="text-xs font-bold text-white uppercase tracking-wider">Live</span>
                                </div>
                            </div>

                            {/* Capture Controls */}
                            <div className="absolute bottom-0 left-0 right-0 p-8 flex justify-center items-center bg-gradient-to-t from-black/80 to-transparent">
                                <button
                                    onClick={capturePhoto}
                                    className="w-20 h-20 rounded-full border-4 border-white flex items-center justify-center group hover:scale-105 transition-transform active:scale-95"
                                >
                                    <div className="w-16 h-16 bg-white rounded-full group-active:scale-90 transition-transform" />
                                </button>
                            </div>
                        </div>
                    </div>
                )
            }

            {/* Helper Text */}
            <div className="flex items-start gap-2 text-xs text-slate-500 px-1">
                <AlertCircle className="w-4 h-4 flex-shrink-0 text-slate-600" />
                <p>
                    Supported formats: JPG, PNG. Max size: 5MB.
                    <br />
                    Images are analyzed by AI for verification.
                </p>
            </div>
        </div >
    );
}
