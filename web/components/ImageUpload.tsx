'use client';

import { useState, useRef } from 'react';
import { UploadedImage } from '@/lib/types';
import toast from 'react-hot-toast';
import { ImagePlus, X, Image, AlertCircle } from 'lucide-react';

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

        Array.from(files).forEach((file) => {
            // Check file type
            if (!file.type.startsWith('image/')) {
                toast.error(`"${file.name}" is not an image file.`);
                return;
            }

            // Check for duplicates
            if (isDuplicate(file)) {
                skippedDuplicate++;
                return;
            }

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
                        toast.error(`Failed to process "${file.name}". Please try again.`);
                        return;
                    }
                    ctx.drawImage(img, 0, 0, width, height);

                    // Compress to 85% quality JPEG
                    canvas.toBlob(
                        (blob) => {
                            if (!blob) {
                                console.error(`Failed to create blob for "${file.name}". Attempting fallback...`);

                                try {
                                    const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
                                    fetch(dataUrl)
                                        .then(res => res.blob())
                                        .then(fallbackBlob => {
                                            pendingCountRef.current--;
                                            if (fallbackBlob) {
                                                const optimizedFile = new File([fallbackBlob], file.name.replace(/\.\w+$/, '.jpg'), {
                                                    type: 'image/jpeg',
                                                });
                                                onAdd({
                                                    file: optimizedFile,
                                                    preview: dataUrl,
                                                });
                                            } else {
                                                throw new Error('Fallback blob creation failed');
                                            }
                                        }).catch(() => {
                                            pendingCountRef.current--;
                                            toast.error(`Failed to process "${file.name}".`);
                                        });
                                } catch (error) {
                                    pendingCountRef.current--;
                                    toast.error(`Failed to process "${file.name}". Please try again.`);
                                }
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

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (!files) return;

        processFiles(files);

        // Reset input
        e.target.value = '';
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (!isAtLimit) {
            processFiles(e.dataTransfer.files);
        }
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

            {/* Drop zone */}
            <div
                onDragOver={(e) => { e.preventDefault(); if (!isAtLimit) setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-xl sm:rounded-2xl p-6 sm:p-8 transition-all ${isAtLimit
                    ? 'border-slate-700 bg-slate-900/30 cursor-not-allowed opacity-60'
                    : isDragging
                        ? 'border-cyan-500 bg-cyan-500/5 cursor-pointer'
                        : 'border-slate-700 hover:border-cyan-500/50 hover:bg-slate-900/50 cursor-pointer'
                    }`}
            >
                <label className={`flex flex-col items-center justify-center ${isAtLimit ? 'cursor-not-allowed' : 'cursor-pointer'}`}>
                    <input
                        type="file"
                        accept="image/*"
                        multiple
                        onChange={handleFileChange}
                        className="hidden"
                        disabled={isAtLimit}
                    />
                    <div className={`p-4 rounded-full mb-4 transition-colors ${isAtLimit
                        ? 'bg-slate-800/50'
                        : isDragging ? 'bg-cyan-500/20' : 'bg-slate-800'
                        }`}>
                        {isAtLimit ? (
                            <AlertCircle className="h-8 w-8 sm:h-10 sm:w-10 text-yellow-500" />
                        ) : (
                            <ImagePlus className={`h-8 w-8 sm:h-10 sm:w-10 ${isDragging ? 'text-cyan-400' : 'text-slate-500'}`} />
                        )}
                    </div>
                    {isAtLimit ? (
                        <>
                            <p className="text-yellow-400 text-sm sm:text-base text-center mb-1 font-medium">
                                Maximum {maxImages} images reached
                            </p>
                            <p className="text-slate-500 text-xs text-center">
                                Remove an image to add more
                            </p>
                        </>
                    ) : (
                        <>
                            <p className="text-slate-400 text-sm sm:text-base text-center mb-1">
                                Drop images here or click to select
                            </p>
                            <p className="text-slate-600 text-xs text-center">
                                {remainingSlots} slot{remainingSlots !== 1 ? 's' : ''} remaining • Auto-optimized for AI
                            </p>
                        </>
                    )}
                </label>
            </div>

            {/* Uploaded images grid */}
            {images.length > 0 && (
                <div className="mt-4">
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        {images.map((img, index) => (
                            <div
                                key={index}
                                className="relative group aspect-square rounded-xl overflow-hidden border border-slate-700 hover:border-cyan-500/50 transition-colors"
                            >
                                <img
                                    src={img.preview}
                                    alt={`Image ${index + 1}`}
                                    className="w-full h-full object-cover"
                                />
                                {/* Overlay with file info */}
                                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                                    <div className="absolute bottom-2 left-2 right-2">
                                        <p className="text-white text-xs truncate">{img.file.name}</p>
                                        <p className="text-slate-400 text-xs">{(img.file.size / 1024).toFixed(0)}KB</p>
                                    </div>
                                </div>
                                {/* Remove button */}
                                <button
                                    onClick={() => onRemove(index)}
                                    className="absolute top-2 right-2 p-1.5 bg-red-500/80 hover:bg-red-500 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                                    aria-label="Remove image"
                                >
                                    <X className="h-4 w-4 text-white" />
                                </button>
                                {/* Image number badge */}
                                <div className="absolute top-2 left-2 px-2 py-0.5 bg-black/60 rounded text-xs text-white font-medium">
                                    {index + 1}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
