import reflex as rx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.components.layout import layout
from app.components.landing import landing_page
from app.components.client_view import client_view
from app.components.worker_view import worker_view
from app.states.global_state import GlobalState

# Get Google Maps API key from environment
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

def index() -> rx.Component:
    """Landing page with role selection."""
    return landing_page()

def app_page() -> rx.Component:
    """Main application page based on selected role."""
    return layout(rx.cond(GlobalState.user_mode, client_view(), worker_view()))

app = rx.App(
    theme=rx.theme(appearance="light"),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
    head_components=[
        rx.script(src=f"https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAPS_API_KEY}&libraries=places&callback=Function.prototype"),
        rx.script("""
function initLocationAutocomplete() {
    if (typeof google === 'undefined' || !google.maps || !google.maps.places) {
        setTimeout(initLocationAutocomplete, 200);
        return;
    }
    
    const input = document.getElementById('location-autocomplete-input');
    const suggestionsDiv = document.getElementById('location-suggestions');
    
    if (!input || !suggestionsDiv) {
        setTimeout(initLocationAutocomplete, 200);
        return;
    }
    
    let sessionToken = new google.maps.places.AutocompleteSessionToken();
    const placesService = new google.maps.places.PlacesService(document.createElement('div'));
    let debounceTimer;
    
    function searchLocation(query) {
        if (query.length < 3) {
            suggestionsDiv.classList.add('hidden');
            return;
        }
        
        const autocompleteService = new google.maps.places.AutocompleteService();
        
        autocompleteService.getPlacePredictions({
            input: query,
            sessionToken: sessionToken,
            types: ['geocode', 'establishment']
        }, (predictions, status) => {
            if (status === google.maps.places.PlacesServiceStatus.OK && predictions) {
                displaySuggestions(predictions);
            } else if (status === google.maps.places.PlacesServiceStatus.ZERO_RESULTS) {
                suggestionsDiv.innerHTML = '<div class="p-3 text-slate-400 text-sm">No locations found</div>';
                suggestionsDiv.classList.remove('hidden');
            } else {
                suggestionsDiv.classList.add('hidden');
            }
        });
    }
    
    function displaySuggestions(predictions) {
        suggestionsDiv.innerHTML = '';
        suggestionsDiv.classList.remove('hidden');
        
        predictions.slice(0, 5).forEach(prediction => {
            const div = document.createElement('div');
            div.className = 'p-3 hover:bg-slate-800 cursor-pointer border-b border-slate-700 last:border-0 transition-colors';
            
            const mainText = prediction.structured_formatting.main_text;
            const secondaryText = prediction.structured_formatting.secondary_text || '';
            
            div.innerHTML = `
                <div class="flex items-start">
                    <svg class="h-4 w-4 text-cyan-400 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    </svg>
                    <div class="flex-1">
                        <div class="text-sm text-slate-200 font-medium">${mainText}</div>
                        ${secondaryText ? `<div class="text-xs text-slate-400 mt-0.5">${secondaryText}</div>` : ''}
                    </div>
                </div>
            `;
            
            div.onclick = () => selectLocation(prediction);
            suggestionsDiv.appendChild(div);
        });
    }
    
    function selectLocation(prediction) {
        suggestionsDiv.classList.add('hidden');
        
        placesService.getDetails({
            placeId: prediction.place_id,
            fields: ['geometry', 'formatted_address'],
            sessionToken: sessionToken
        }, (place, status) => {
            if (status === google.maps.places.PlacesServiceStatus.OK && place.geometry) {
                const lat = place.geometry.location.lat();
                const lng = place.geometry.location.lng();
                const address = place.formatted_address;
                
                // Store coordinates in data attributes (survives re-renders)
                input.setAttribute('data-lat', lat);
                input.setAttribute('data-lng', lng);
                
                // IMPORTANT: Update the input value AND trigger Reflex state update
                input.value = address;
                
                // Trigger events to ensure state is updated (avoid input to prevent re-search)
                input.dispatchEvent(new Event('change', { bubbles: true }));
                input.dispatchEvent(new Event('blur', { bubbles: true }));

                // Update hidden reactive inputs so Reflex state captures coordinates
                const latInput = document.getElementById('hidden-lat');
                const lngInput = document.getElementById('hidden-lng');
                if (latInput && lngInput) {
                    latInput.value = lat;
                    lngInput.value = lng;
                    latInput.dispatchEvent(new Event('change', { bubbles: true }));
                    lngInput.dispatchEvent(new Event('change', { bubbles: true }));
                }
                
                // Also store globally as backup
                window.lastSelectedLocation = { lat, lng, address };
                
                console.log('✅ Location selected and saved:', { address, lat, lng });

                // Suppress autocomplete search briefly to avoid dropdown reappearing after re-render
                window.locationAutocompleteSuppressUntil = Date.now() + 1500;
                
                sessionToken = new google.maps.places.AutocompleteSessionToken();
            }
        });
    }
    
    input.addEventListener('input', (e) => {
        if (window.locationAutocompleteSuppressUntil && Date.now() < window.locationAutocompleteSuppressUntil) {
            suggestionsDiv.classList.add('hidden');
            return;
        }
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => searchLocation(e.target.value.trim()), 800);
    });
    
    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !suggestionsDiv.contains(e.target)) {
            suggestionsDiv.classList.add('hidden');
        }
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLocationAutocomplete);
} else {
    setTimeout(initLocationAutocomplete, 500);
}

// Clear location data on page load to prevent stale data
window.addEventListener('load', function() {
    const input = document.getElementById('location-autocomplete-input');
    if (input) {
        input.removeAttribute('data-lat');
        input.removeAttribute('data-lng');
    }
});

// Helper function to extract coordinates before form submission
window.extractLocationCoordinates = function() {
    const input = document.getElementById('location-autocomplete-input');
    if (input) {
        const lat = parseFloat(input.getAttribute('data-lat')) || 0.0;
        const lng = parseFloat(input.getAttribute('data-lng')) || 0.0;
        console.log('📍 Extracted coordinates:', { lat, lng, address: input.value });
        return { lat, lng, address: input.value };
    }
    return { lat: 0.0, lng: 0.0, address: '' };
};

// Restore location data after page re-renders (e.g., after image upload)
const observer = new MutationObserver(function() {
    const input = document.getElementById('location-autocomplete-input');
    const latInput = document.getElementById('hidden-lat');
    const lngInput = document.getElementById('hidden-lng');
    if (input && window.lastSelectedLocation) {
        // Restore data attributes and input value
        if (!input.getAttribute('data-lat') && window.lastSelectedLocation.lat) {
            input.setAttribute('data-lat', window.lastSelectedLocation.lat);
            input.setAttribute('data-lng', window.lastSelectedLocation.lng);
        }
        if (window.lastSelectedLocation.address && input.value !== window.lastSelectedLocation.address) {
            input.value = window.lastSelectedLocation.address;
            // Trigger state update without re-search
            input.dispatchEvent(new Event('change', { bubbles: true }));
            // Hide suggestions if they were left open
            suggestionsDiv.classList.add('hidden');
        }
        // Restore hidden inputs and trigger change for Reflex state
        if (latInput && lngInput && window.lastSelectedLocation.lat) {
            latInput.value = window.lastSelectedLocation.lat;
            lngInput.value = window.lastSelectedLocation.lng;
            latInput.dispatchEvent(new Event('change', { bubbles: true }));
            lngInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
});

// Watch for DOM changes
if (document.body) {
    observer.observe(document.body, { childList: true, subtree: true });
}
        """),
    ],
)

# Landing page
app.add_page(index, route="/")

# Main app page with polling
app.add_page(app_page, route="/app", on_load=GlobalState.start_polling)
