import math


def calculate_road_distance_km(
    farmer_latitude: float,
    farmer_longitude: float,
    market_latitude: float,
    market_longitude: float
):

    R = 6371.0

    lat1 = math.radians(farmer_latitude)
    lat2 = math.radians(market_latitude)

    dlat = math.radians(
        market_latitude - farmer_latitude
    )

    dlon = math.radians(
        market_longitude - farmer_longitude
    )

    a = (
        math.sin(dlat / 2) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    straight_distance = R * c

    # Road-distance approximation
    road_distance = straight_distance * 1.25

    return round(
        road_distance,
        2
    )