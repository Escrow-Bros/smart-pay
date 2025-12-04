'use client';

import { useState } from 'react';
import { UploadedImage } from '@/lib/types';

interface ImageUploadProps {
    images: UploadedImage[];
    onAdd: (image: UploadedImage) => void;
    onRemove: (index: number) => void;
}

export default function ImageUpload({ images, onAdd, onRemove }: ImageUploadProps) {
    const [isDragging, setIsDragging] = useState(false);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (!files) return;

        Array.from(files).forEach((file) => {
            // Check file type
            if (!file.type.startsWith('image/')) {
                alert(`"${file.name}" is not an image file.`);
                return;
            }

            // Read and optimize ALL images
            const reader = new FileReader();
            reader.onloadend = () => {
                const img = new Image();
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
                    ctx?.drawImage(img, 0, 0, width, height);

                    // Compress to 85% quality JPEG
                    canvas.toBlob(
                        (blob) => {
                            if (blob) {
                                const optimizedFile = new File([blob], file.name.replace(/\.\w+$/, '.jpg'), {
                                    type: 'image/jpeg',
                                });
                                const preview = canvas.toDataURL('image/jpeg', 0.85);
                                
                                // Show size reduction if significant
                                const originalSizeMB = (file.size / (1024 * 1024)).toFixed(2);
                                const optimizedSizeMB = (blob.size / (1024 * 1024)).toFixed(2);
                                if (file.size > blob.size * 1.5) {
                                    console.log(`✅ Optimized ${file.name}: ${originalSizeMB}MB → ${optimizedSizeMB}MB`);
                                }
                                
                                onAdd({
                                    file: optimizedFile,
                                    preview,
                                });
                            }
                        },
                        'image/jpeg',
                        0.85
                    );
                };
                img.src = reader.result as string;
            };
            reader.readAsDataURL(file);
        });

        // Reset input
        e.target.value = '';
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        // Simulate a change event for the dropped files
        const dataTransfer = new DataTransfer();
        Array.from(e.dataTransfer.files).forEach(file => dataTransfer.items.add(file));
        const syntheticEvent = {
            target: { files: dataTransfer.files, value: '' }
        } as React.ChangeEvent<HTMLInputElement>;
        handleFileChange(syntheticEvent);
    };

    return (
        <div className="w-full">
            <label className="block text-sm sm:text-base font-medium text-slate-300 mb-3 text-center">
                Reference Photos
            </label>

            <div
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-xl sm:rounded-2xl p-6 sm:p-8 md:p-10 transition-all cursor-pointer ${isDragging
                    ? 'border-cyan-500 bg-slate-900/50'
                    : 'border-slate-700 hover:border-cyan-500/50 hover:bg-slate-900/50'
                    }`}
            >
                <label className="flex flex-col items-center justify-center cursor-pointer">
                    <input
                        type="file"
                        accept="image/*"
                        multiple
                        onChange={handleFileChange}
                        className="hidden"
                    />
                    <svg className="h-10 w-10 sm:h-12 sm:w-12 text-slate-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <p className="text-slate-400 text-sm sm:text-base text-center mb-2">
                        Drop reference images here or click to select
                    </p>
                    <p className="text-slate-600 text-xs text-center">
                        Any size accepted • Auto-optimized for AI
                    </p>
                </label>
            </div>
            <p className="text-xs sm:text-sm text-gray-400 mt-3 text-center">
                💡 All images auto-resized to 1600px & compressed (85% quality) for optimal AI processing
            </p>

            {images.length > 0 && (
                <div className="mt-4">
                    <p className="text-sm font-medium text-slate-300 mb-3 text-center">
                        Uploaded Images ({images.length})
                    </p>
                    {images.map((img, index) => (
                        <div
                            key={index}
                            className="flex items-center mt-2 sm:mt-3 p-2.5 sm:p-3 bg-slate-900 rounded-lg border border-slate-800 hover:border-slate-700 transition-colors"
                        >
                            <img
                                src={img.preview}
                                alt="Preview"
                                className="h-9 w-9 sm:h-10 sm:w-10 object-cover rounded mr-2 sm:mr-3 flex-shrink-0"
                            />
                            <span className="text-slate-300 text-xs sm:text-sm flex-1 truncate min-w-0">
                                {img.file.name}
                            </span>
                            <button
                                onClick={() => onRemove(index)}
                                className="ml-2 p-1.5 hover:bg-red-500/10 rounded transition-colors flex-shrink-0 min-h-[32px] min-w-[32px] touch-manipulation flex items-center justify-center"
                                aria-label="Remove image"
                            >
                                <svg className="h-4 w-4 text-red-400 hover:text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
