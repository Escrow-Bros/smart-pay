'use client';

import { useState, useEffect, useRef } from 'react';

interface LocationPickerProps {
    value: string;
    onChange: (address: string, lat: number, lng: number) => void;
}

export default function LocationPicker({ value, onChange }: LocationPickerProps) {
    const [suggestions, setSuggestions] = useState<google.maps.places.AutocompletePrediction[]>([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);
    const suggestionsRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (
                suggestionsRef.current &&
                !suggestionsRef.current.contains(e.target as Node) &&
                !inputRef.current?.contains(e.target as Node)
            ) {
                setShowSuggestions(false);
            }
        };

        document.addEventListener('click', handleClickOutside);
        return () => document.removeEventListener('click', handleClickOutside);
    }, []);

    const handleInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const query = e.target.value;
        onChange(query, 0, 0); // Update address but clear coordinates until selection

        if (query.length < 3) {
            setSuggestions([]);
            setShowSuggestions(false);
            return;
        }

        if (!window.google?.maps?.places) {
            console.error('Google Maps not loaded');
            return;
        }

        const service = new google.maps.places.AutocompleteService();
        service.getPlacePredictions(
            { input: query, types: ['geocode', 'establishment'] },
            (predictions, status) => {
                if (status === google.maps.places.PlacesServiceStatus.OK && predictions) {
                    setSuggestions(predictions);
                    setShowSuggestions(true);
                }
            }
        );
    };

    const handleSelectLocation = (prediction: google.maps.places.AutocompletePrediction) => {
        const service = new google.maps.places.PlacesService(document.createElement('div'));

        service.getDetails(
            {
                placeId: prediction.place_id,
                fields: ['geometry', 'formatted_address'],
            },
            (place, status) => {
                if (status === google.maps.places.PlacesServiceStatus.OK && place?.geometry?.location) {
                    const lat = place.geometry.location.lat();
                    const lng = place.geometry.location.lng();
                    const address = place.formatted_address || prediction.description;

                    onChange(address, lat, lng);
                    setShowSuggestions(false);

                    console.log('✅ Location selected:', { address, lat, lng });
                }
            }
        );
    };

    return (
        <div className="mb-6">
            <label className="block text-sm font-medium text-slate-300 mb-2">
                Job Location
            </label>

            <div className="relative">
                <input
                    ref={inputRef}
                    type="text"
                    value={value}
                    onChange={handleInputChange}
                    placeholder="Start typing an address (e.g., '123 Main St, San Francisco')..."
                    className="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-4 text-slate-200 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-all placeholder:text-slate-600 text-sm"
                    autoComplete="off"
                />

                {showSuggestions && suggestions.length > 0 && (
                    <div
                        ref={suggestionsRef}
                        className="absolute z-50 mt-2 w-full bg-slate-900 border border-slate-700 rounded-xl overflow-hidden shadow-xl"
                    >
                        {suggestions.slice(0, 5).map((prediction) => (
                            <div
                                key={prediction.place_id}
                                onClick={() => handleSelectLocation(prediction)}
                                className="p-3 hover:bg-slate-800 cursor-pointer border-b border-slate-700 last:border-0 transition-colors flex items-start gap-2"
                            >
                                <svg className="h-4 w-4 text-cyan-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                                <div className="flex-1">
                                    <div className="text-sm text-slate-200 font-medium">
                                        {prediction.structured_formatting.main_text}
                                    </div>
                                    {prediction.structured_formatting.secondary_text && (
                                        <div className="text-xs text-slate-400 mt-0.5">
                                            {prediction.structured_formatting.secondary_text}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <p className="text-xs text-slate-500 mt-2">
                💡 Start typing to search for an address. Select from suggestions for precise coordinates.
            </p>
        </div>
    );
}
