'use client';

import { useState } from 'react';

interface ImageUploadProps {
    images: { file: File; preview: string }[];
    onAdd: (image: { file: File; preview: string }) => void;
    onRemove: (index: number) => void;
}

export default function ImageUpload({ images, onAdd, onRemove }: ImageUploadProps) {
    const [isDragging, setIsDragging] = useState(false);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (!files) return;

        const MAX_SIZE_KB = 700;
        const MAX_SIZE_BYTES = MAX_SIZE_KB * 1024;

        Array.from(files).forEach((file) => {
            // Check file size
            if (file.size > MAX_SIZE_BYTES) {
                alert(`Image "${file.name}" is too large (${(file.size / 1024).toFixed(0)}KB). Please upload images smaller than ${MAX_SIZE_KB}KB.`);
                return;
            }

            // Check file type (already present in original, keeping it)
            if (!file.type.startsWith('image/')) {
                return;
            }

            const reader = new FileReader();
            reader.onloadend = () => {
                onAdd({
                    file,
                    preview: reader.result as string,
                });
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
        <div className="mb-6">
            <label className="block text-sm font-medium text-slate-300 mb-3">
                Reference Photos
            </label>

            <div
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-xl p-8 transition-all cursor-pointer ${isDragging
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
                    <svg className="h-10 w-10 text-slate-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <p className="text-slate-400 text-sm text-center">
                        Drop reference images here or click to select
                    </p>
                    <p className="text-slate-600 text-xs mt-1">
                        Supports JPG, PNG - Multiple files allowed
                    </p>
                </label>
            </div>
            <p className="text-sm text-gray-400 mt-2">
                ⚠️ Max size: 700KB per image
            </p>

            {images.length > 0 && (
                <div className="mt-3">
                    <p className="text-sm font-medium text-slate-300 mb-3">Uploaded Images</p>
                    {images.map((img, index) => (
                        <div
                            key={index}
                            className="flex items-center mt-3 p-3 bg-slate-900 rounded-lg border border-slate-800 hover:border-slate-700 transition-colors"
                        >
                            <img
                                src={img.preview}
                                alt="Preview"
                                className="h-10 w-10 object-cover rounded mr-3"
                            />
                            <span className="text-slate-300 text-sm flex-1 truncate">{img.file.name}</span>
                            <button
                                onClick={() => onRemove(index)}
                                className="ml-2 p-1 hover:bg-red-500/10 rounded transition-colors"
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
