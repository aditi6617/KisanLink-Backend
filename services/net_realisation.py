def calculate_net_realisation(
    quantity_kg: float,
    price_per_quintal: float,
    distance_km: float,
    market_charge_percent: float = 1.0,
    other_cost_per_kg: float = 0.50
):

    # ==================================================
    # 1. VALIDATE INPUT
    # ==================================================

    if quantity_kg <= 0:
        raise ValueError("Quantity must be greater than 0")

    if price_per_quintal < 0:
        raise ValueError("Price cannot be negative")

    if distance_km < 0:
        raise ValueError("Distance cannot be negative")


    # ==================================================
    # 2. CONVERT KG TO QUINTALS
    # ==================================================

    quantity_quintal = quantity_kg / 100


    # ==================================================
    # 3. GROSS SELLING VALUE
    # ==================================================

    gross_value = (
        quantity_quintal
        * price_per_quintal
    )


    # ==================================================
    # 4. TRANSPORT COST
    # ==================================================

    # Prototype transport rate
    # ₹0.03 per kg per km

    transport_rate_per_kg_per_km = 0.03

    transport_cost = (
        quantity_kg
        * distance_km
        * transport_rate_per_kg_per_km
    )


    # ==================================================
    # 5. MARKET CHARGES
    # ==================================================

    market_charges = (
        gross_value
        * market_charge_percent
        / 100
    )


    # ==================================================
    # 6. OTHER COSTS
    # ==================================================

    other_costs = (
        quantity_kg
        * other_cost_per_kg
    )


    # ==================================================
    # 7. TOTAL COST
    # ==================================================

    total_cost = (
        transport_cost
        + market_charges
        + other_costs
    )


    # ==================================================
    # 8. NET REALISATION
    # ==================================================

    net_realisation = (
        gross_value
        - total_cost
    )


    # ==================================================
    # 9. NET REALISATION PER KG
    # ==================================================

    net_realisation_per_kg = (
        net_realisation / quantity_kg
    )


    # ==================================================
    # 10. RETURN RESULT
    # ==================================================

    return {

        "quantity_kg": quantity_kg,

        "quantity_quintal": round(
            quantity_quintal,
            2
        ),

        "price_per_quintal": price_per_quintal,

        "distance_km": round(
            distance_km,
            2
        ),

        "gross_value": round(
            gross_value,
            2
        ),

        "transport_cost": round(
            transport_cost,
            2
        ),

        "market_charges": round(
            market_charges,
            2
        ),

        "other_costs": round(
            other_costs,
            2
        ),

        "total_cost": round(
            total_cost,
            2
        ),

        "net_realisation": round(
            net_realisation,
            2
        ),

        "net_realisation_per_kg": round(
            net_realisation_per_kg,
            2
        )
    }