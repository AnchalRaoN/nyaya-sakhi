DLSA_DIRECTORY = {
    "udupi": {"office": "DLSA Udupi", "phone": "0820-2574434", "address": "District Court Complex, Udupi"},
    "mangalore": {"office": "DLSA Dakshina Kannada", "phone": "0824-2440262", "address": "District Court, Mangaluru"},
    "mangaluru": {"office": "DLSA Dakshina Kannada", "phone": "0824-2440262", "address": "District Court, Mangaluru"},
    "bangalore": {"office": "DLSA Bengaluru Urban", "phone": "080-22111034", "address": "City Civil Court, Bengaluru"},
    "bengaluru": {"office": "DLSA Bengaluru Urban", "phone": "080-22111034", "address": "City Civil Court, Bengaluru"},
    "mysore": {"office": "DLSA Mysuru", "phone": "0821-2423555", "address": "District Court Complex, Mysuru"},
    "mysuru": {"office": "DLSA Mysuru", "phone": "0821-2423555", "address": "District Court Complex, Mysuru"},
}

DEFAULT_DLSA = {"office": "NALSA National Helpline", "phone": "15100", "address": "Contact for nearest DLSA in your district"}


def get_nearest_dlsa(location: str) -> dict:
    if not location:
        return DEFAULT_DLSA
    location_lower = location.lower()
    for city, info in DLSA_DIRECTORY.items():
        if city in location_lower:
            return info
    return DEFAULT_DLSA