def calculate_transport_cost(
    distance_km: float,
    cost_per_km: float = 25
):
    """
    Calculate estimated transportation cost.

    distance_km:
        Road distance between farmer and market.

    cost_per_km:
        Estimated transport cost per km.
    """

    if distance_km < 0:
        raise ValueError("Distance cannot be negative")

    transport_cost = distance_km * cost_per_km

    return round(transport_cost, 2)