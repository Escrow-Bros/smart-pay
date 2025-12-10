"""
GPS Location Verifier
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
    max_distance_meters: float = 300.0
) -> Dict:
    """
    Verify that proof photo was taken at the job location
    
    Uses tiered verification based on max_distance_meters:
    - Tier 1 (Excellent): 0 to 40% of max - High confidence
    - Tier 2 (Good): 40% to 70% of max - Medium-high confidence
    - Tier 3 (Acceptable): 70% to 100% of max - Lower confidence but pass
    - Tier 4 (Failed): Beyond max - Reject
    
    GPS accuracy (from both devices) is added to max_distance_meters as a tolerance buffer.
    
    Args:
        reference_gps: {"latitude": float, "longitude": float, "accuracy": float}
        proof_gps: {"lat": float, "lng": float, "accuracy": float}
        max_distance_meters: Maximum allowed distance in meters (default 300m = typical job site radius)
    
    Returns:
        {
            "location_match": bool,
            "distance_meters": float,
            "confidence": float,
            "reasoning": str,
            "tier": str,  # 'excellent', 'good', 'acceptable', 'failed'
            "threshold_used": float  # actual max with GPS accuracy buffer
        }
    """
    try:
        # Extract coordinates
        ref_lat = reference_gps.get("latitude")
        ref_lon = reference_gps.get("longitude")
        ref_accuracy = reference_gps.get("accuracy", 10)  # meters
        
        proof_lat = proof_gps.get("lat")
        proof_lon = proof_gps.get("lng")
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
        
        # Account for GPS accuracy - add as tolerance buffer
        total_accuracy = ref_accuracy + proof_accuracy
        adjusted_max_distance = max_distance_meters + total_accuracy
        
        # Calculate tier thresholds based on max_distance_meters
        # This makes the tiers scale proportionally with the configured max
        tier1_threshold = max_distance_meters * 0.4   # Excellent: 0-40% of max
        tier2_threshold = max_distance_meters * 0.7   # Good: 40-70% of max
        tier3_threshold = max_distance_meters         # Acceptable: 70-100% of max
        
        # Tiered verification with dynamic thresholds
        if distance <= tier1_threshold:
            tier = 'excellent'
            location_match = True
            confidence = 1.0 - (distance / tier1_threshold) * 0.2  # 0.8-1.0 range
            reasoning = f"Worker at job site ({distance:.1f}m away - excellent)"
        elif distance <= tier2_threshold:
            tier = 'good'
            location_match = True
            range_size = tier2_threshold - tier1_threshold
            confidence = 0.7 - ((distance - tier1_threshold) / range_size) * 0.2  # 0.5-0.7 range
            reasoning = f"Worker near job site ({distance:.1f}m away - acceptable with GPS accuracy)"
        elif distance <= tier3_threshold:
            tier = 'acceptable'
            location_match = True
            range_size = tier3_threshold - tier2_threshold
            confidence = 0.5 - ((distance - tier2_threshold) / range_size) * 0.1  # 0.4-0.5 range
            reasoning = f"Worker in vicinity ({distance:.1f}m away - marginal, check photos carefully)"
        else:
            tier = 'failed'
            location_match = False
            confidence = 0.1
            reasoning = f"Worker too far from job site ({distance:.1f}m away - max {max_distance_meters:.0f}m)"
        
        return {
            "location_match": location_match,
            "distance_meters": round(distance, 2),
            "confidence": round(confidence, 3),
            "reasoning": reasoning,
            "tier": tier,
            "gps_accuracy": {
                "reference": ref_accuracy,
                "proof": proof_accuracy,
                "total": total_accuracy
            },
            "threshold_used": adjusted_max_distance
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
