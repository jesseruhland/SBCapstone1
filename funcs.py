"""Additional helper functions for app."""

from models import Site

def create_filters(ra):
    """Format filters for query based on request args.  Return formatted filters in a list."""

    borough = ra.get("borough")
    site_name = ra.get("site_name")
    zip_code = ra.get("zip_code")
    male_condoms = ra.get("male_condoms")
    female_condoms = ra.get("fc2_female_insertive_condoms")
    lubricant = ra.get("lubricant")

    result = []

    if borough:
        result.append(Site.borough == borough)

    if site_name:
        result.append(Site.name.ilike(f"%{site_name}%"))
    
    if zip_code:
        result.append(Site.zip_code == zip_code)
    
    if male_condoms:
        result.append(Site.male_condoms == male_condoms)
    
    if female_condoms:
        result.append(Site.fc2_female_insertive_condoms == female_condoms)
    
    if lubricant:
        result.append(Site.lubricant == lubricant)
    
    return result