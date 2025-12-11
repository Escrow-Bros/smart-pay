'use client';

import { useEffect } from 'react';

export default function GoogleMapsDebug() {
    useEffect(() => {
        const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;
        console.log('🗺️ Google Maps API Key:', apiKey);
        console.log('🗺️ API Key length:', apiKey?.length || 0);
        console.log('🗺️ API Key first 10 chars:', apiKey?.substring(0, 10) || 'undefined');
    }, []);

    return null;
}
