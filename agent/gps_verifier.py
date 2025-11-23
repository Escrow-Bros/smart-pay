"""
GPS Location Verifier - TASK-014 Integration
Verifies that proof photos were taken at the correct job location

This is part of the Detective agent (context verification)
"""
import math
from typing import Dict, Optional, Tuple

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two GPS coordinates using Haversine formula
    
    Args:
        lat1, lon1: First location (reference photo location)
        lat2, lon2: Second location (proof photo location)
    
    Returns:
        Distance in meters
    """
    # Earth radius in meters
    R = 6371000
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance

def verify_gps_location(
    reference_gps: Dict,
    proof_gps: Dict,
    max_distance_meters: float = 50.0
) -> Dict:
    """
    Verify that proof photo was taken at the job location
    
    Args:
        reference_gps: {"latitude": float, "longitude": float, "accuracy": float}
        proof_gps: {"latitude": float, "longitude": float, "accuracy": float}
        max_distance_meters: Maximum allowed distance (default 50 meters)
    
    Returns:
        {
            "location_match": bool,
            "distance_meters": float,
            "confidence": float,
            "reasoning": str
        }
    """
    try:
        # Extract coordinates
        ref_lat = reference_gps.get("latitude")
        ref_lon = reference_gps.get("longitude")
        ref_accuracy = reference_gps.get("accuracy", 10)  # meters
        
        proof_lat = proof_gps.get("latitude")
        proof_lon = proof_gps.get("longitude")
        proof_accuracy = proof_gps.get("accuracy", 10)  # meters
        
        # Validate inputs
        if None in [ref_lat, ref_lon, proof_lat, proof_lon]:
            return {
                "location_match": False,
                "distance_meters": None,
                "confidence": 0.0,
                "reasoning": "Missing GPS coordinates in one or both photos"
            }
        
        # Calculate distance
        distance = calculate_distance(ref_lat, ref_lon, proof_lat, proof_lon)
        
        # Account for GPS accuracy
        # If GPS accuracy is poor, increase tolerance
        total_accuracy = ref_accuracy + proof_accuracy
        adjusted_max_distance = max_distance_meters + total_accuracy
        
        # Determine match
        location_match = distance <= adjusted_max_distance
        
        # Calculate confidence based on distance and accuracy
        if location_match:
            # Confidence decreases as distance approaches limit
            confidence = 1.0 - (distance / adjusted_max_distance)
            confidence = max(0.5, min(1.0, confidence))  # Clamp between 0.5-1.0
        else:
            # Low confidence if locations don't match
            confidence = 0.1
        
        # Generate reasoning
        if location_match:
            reasoning = f"Photos taken {distance:.1f}m apart (within {adjusted_max_distance:.1f}m tolerance)"
        else:
            reasoning = f"Photos taken {distance:.1f}m apart (exceeds {adjusted_max_distance:.1f}m limit)"
        
        return {
            "location_match": location_match,
            "distance_meters": round(distance, 2),
            "confidence": round(confidence, 3),
            "reasoning": reasoning,
            "gps_accuracy": {
                "reference": ref_accuracy,
                "proof": proof_accuracy,
                "total": total_accuracy
            }
        }
        
    except Exception as e:
        return {
            "location_match": False,
            "distance_meters": None,
            "confidence": 0.0,
            "reasoning": f"GPS verification error: {str(e)}"
        }

def extract_gps_from_exif(image_bytes: bytes) -> Optional[Dict]:
    """
    Extract GPS coordinates from image EXIF data
    
    Args:
        image_bytes: Raw image bytes
    
    Returns:
        {"latitude": float, "longitude": float, "accuracy": float} or None
    """
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS, GPSTAGS
        from io import BytesIO
        
        # Open image
        image = Image.open(BytesIO(image_bytes))
        
        # Get EXIF data
        exif_data = image._getexif()
        
        if not exif_data:
            return None
        
        # Find GPS Info tag
        gps_info = None
        for tag, value in exif_data.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_info = value
                break
        
        if not gps_info:
            return None
        
        # Decode GPS data
        gps_data = {}
        for key in gps_info.keys():
            decode = GPSTAGS.get(key, key)
            gps_data[decode] = gps_info[key]
        
        # Extract latitude
        lat = gps_data.get('GPSLatitude')
        lat_ref = gps_data.get('GPSLatitudeRef')
        
        # Extract longitude
        lon = gps_data.get('GPSLongitude')
        lon_ref = gps_data.get('GPSLongitudeRef')
        
        if not all([lat, lat_ref, lon, lon_ref]):
            return None
        
        # Convert to decimal degrees
        def to_decimal(coord):
            d, m, s = coord
            return float(d) + float(m) / 60 + float(s) / 3600
        
        latitude = to_decimal(lat)
        if lat_ref == 'S':
            latitude = -latitude
        
        longitude = to_decimal(lon)
        if lon_ref == 'W':
            longitude = -longitude
        
        # Try to get accuracy (if available)
        accuracy = gps_data.get('GPSHPositioningError', 10)  # Default 10m
        
        return {
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": float(accuracy),
            "timestamp": gps_data.get('GPSDateStamp'),
            "altitude": gps_data.get('GPSAltitude')
        }
        
    except ImportError:
        print("⚠️ Pillow not installed. Run: pip install Pillow")
        return None
    except Exception as e:
        print(f"⚠️ Could not extract GPS from image: {e}")
        return None

# ============================================================================
# INTEGRATION WITH APRO ORACLE (TASK-014 - FUTURE)
# ============================================================================

async def verify_with_apro_oracle(
    gps_location: Dict,
    timestamp: str,
    expected_conditions: Dict = None
) -> Dict:
    """
    TODO (TASK-014): Integrate with Apro Oracle
    
    Verifies:
    - Weather at location matches expected
    - Timestamp is within work window
    - Location is valid
    
    Args:
        gps_location: {"latitude": float, "longitude": float}
        timestamp: ISO timestamp from photo
        expected_conditions: Expected weather, time window, etc.
    
    Returns:
        {
            "weather_match": bool,
            "timestamp_valid": bool,
            "location_valid": bool,
            "confidence": float
        }
    """
    # TODO: Implement Apro Oracle SDK integration
    # This will call external oracle for:
    # - Weather verification
    # - Timestamp validation
    # - Location verification
    
    print("⚠️ Apro Oracle integration pending (TASK-014)")
    
    return {
        "weather_match": True,  # Placeholder
        "timestamp_valid": True,
        "location_valid": True,
        "confidence": 0.8
    }

