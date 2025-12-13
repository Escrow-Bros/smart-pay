'use client';

import { useState, useEffect, useRef, type KeyboardEvent } from 'react';
import { X, ChevronLeft, ChevronRight, ZoomIn } from 'lucide-react';

interface PhotoLightboxProps {
    photos: string[];
    title?: string;
    columns?: 2 | 3 | 4;
}

export default function PhotoLightbox({ photos, title, columns = 2 }: PhotoLightboxProps) {
    const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
    const modalRef = useRef<HTMLDivElement>(null);

    const openLightbox = (index: number) => setSelectedIndex(index);
    const closeLightbox = () => setSelectedIndex(null);

    const goNext = () => {
        if (selectedIndex !== null && photos.length > 0) {
            setSelectedIndex((selectedIndex + 1) % photos.length);
        }
    };

    const goPrev = () => {
        if (selectedIndex !== null && photos.length > 0) {
            setSelectedIndex((selectedIndex - 1 + photos.length) % photos.length);
        }
    };

    // Handle keyboard navigation
    const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowRight') goNext();
        if (e.key === 'ArrowLeft') goPrev();
    };

    // Focus modal when opened
    useEffect(() => {
        if (selectedIndex !== null && modalRef.current) {
            modalRef.current.focus();
        }
    }, [selectedIndex]);

    const gridCols = {
        2: 'grid-cols-2',
        3: 'grid-cols-3',
        4: 'grid-cols-2 sm:grid-cols-4',
    };

    // Early return after all hooks
    if (!photos || photos.length === 0) {
        return (
            <div className="text-center py-8 text-slate-500 text-sm">
                No photos available
            </div>
        );
    }

    return (
        <>
            {title && (
                <h4 className="text-sm font-medium text-slate-400 mb-3 flex items-center gap-2">
                    {title}
                    <span className="text-xs text-slate-500">({photos.length})</span>
                </h4>
            )}

            {/* Thumbnail Grid */}
            <div className={`grid ${gridCols[columns]} gap-2`}>
                {photos.map((photo, index) => (
                    <button
                        key={index}
                        onClick={() => openLightbox(index)}
                        className="group relative aspect-square rounded-xl overflow-hidden border border-slate-700 hover:border-cyan-500/50 transition-all hover:scale-[1.02]"
                    >
                        <img
                            src={photo}
                            alt={`Photo ${index + 1}`}
                            width={80}
                            height={80}
                            loading="lazy"
                            className="w-full h-full object-cover"
                        />
                        {/* Hover overlay */}
                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                            <ZoomIn className="w-6 h-6 text-white" />
                        </div>
                        {/* Index badge */}
                        <div className="absolute top-2 left-2 px-2 py-0.5 bg-black/60 rounded text-xs text-white font-medium">
                            {index + 1}
                        </div>
                    </button>
                ))}
            </div>

            {/* Lightbox Modal */}
            {selectedIndex !== null && (
                <div
                    ref={modalRef}
                    role="dialog"
                    aria-modal="true"
                    aria-label="Photo lightbox"
                    className="fixed inset-0 bg-black/90 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200"
                    onClick={closeLightbox}
                    onKeyDown={handleKeyDown}
                    tabIndex={-1}
                >
                    {/* Close button */}
                    <button
                        onClick={closeLightbox}
                        className="absolute top-4 right-4 p-2 text-white/70 hover:text-white hover:bg-white/10 rounded-lg transition-colors z-10"
                    >
                        <X className="w-6 h-6" />
                    </button>

                    {/* Counter */}
                    <div className="absolute top-4 left-4 px-3 py-1.5 bg-white/10 rounded-lg text-white text-sm font-medium">
                        {selectedIndex + 1} / {photos.length}
                    </div>

                    {/* Navigation buttons */}
                    {photos.length > 1 && (
                        <>
                            <button
                                onClick={(e) => { e.stopPropagation(); goPrev(); }}
                                className="absolute left-4 p-3 text-white/70 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                            >
                                <ChevronLeft className="w-8 h-8" />
                            </button>
                            <button
                                onClick={(e) => { e.stopPropagation(); goNext(); }}
                                className="absolute right-4 p-3 text-white/70 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                            >
                                <ChevronRight className="w-8 h-8" />
                            </button>
                        </>
                    )}

                    {/* Main image */}
                    <div
                        className="max-w-[90vw] max-h-[85vh] relative"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <img
                            src={photos[selectedIndex]}
                            alt={`Photo ${selectedIndex + 1}`}
                            className="max-w-full max-h-[85vh] object-contain rounded-lg shadow-2xl"
                        />
                    </div>

                    {/* Thumbnail strip at bottom */}
                    {photos.length > 1 && (
                        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2 p-2 bg-black/50 rounded-xl">
                            {photos.map((photo, index) => (
                                <button
                                    key={index}
                                    onClick={(e) => { e.stopPropagation(); setSelectedIndex(index); }}
                                    className={`w-12 h-12 rounded-lg overflow-hidden border-2 transition-all ${index === selectedIndex
                                        ? 'border-cyan-500 scale-110'
                                        : 'border-transparent opacity-60 hover:opacity-100'
                                        }`}
                                >
                                    <img
                                        src={photo}
                                        alt={`Thumbnail ${index + 1}`}
                                        width={48}
                                        height={48}
                                        className="w-full h-full object-cover"
                                    />
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </>
    );
}
