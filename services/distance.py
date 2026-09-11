import requests


# =========================================================
# ROAD DISTANCE USING OSRM
# =========================================================

def calculate_distance_km(
    farmer_latitude: float,
    farmer_longitude: float,
    market_latitude: float,
    market_longitude: float
):
    """
    Calculate actual road distance between farmer and market
    using OSRM / OpenStreetMap road network.

    Returns distance in kilometres.
    """

    url = (
        "https://router.project-osrm.org/"
        "route/v1/driving/"
        f"{farmer_longitude},{farmer_latitude};"
        f"{market_longitude},{market_latitude}"
    )

    params = {
        "overview": "false"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        # -------------------------------------------------
        # Check OSRM response
        # -------------------------------------------------

        if data.get("code") != "Ok":

            raise ValueError(
                "OSRM could not find a road route."
            )

        routes = data.get("routes", [])

        if not routes:

            raise ValueError(
                "No road route found between farmer and market."
            )

        # -------------------------------------------------
        # Distance returned by OSRM is in metres
        # -------------------------------------------------

        distance_meters = routes[0]["distance"]

        distance_km = distance_meters / 1000

        return round(
            distance_km,
            2
        )

    except requests.RequestException as error:

        raise RuntimeError(
            f"Road distance service unavailable: {error}"
        )