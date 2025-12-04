from urllib.parse import quote_plus


def build_map_embed(city: str, country: str, lat: str | None = None, lng: str | None = None) -> str:
    # Simple Google Maps embed via coordinates or search query
    if lat and lng:
        return f"https://www.google.com/maps?q={lat},{lng}&output=embed"
    q = quote_plus(f"{city}, {country}")
    return f"https://www.google.com/maps?q={q}&output=embed"

