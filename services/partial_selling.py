from services.net_realisation import calculate_net_realisation


# =========================================================
# CALCULATE PARTIAL SELLING
# =========================================================

def calculate_partial_selling(
    total_quantity_kg: float,
    markets: list,
    quantities_kg: list
):

    if total_quantity_kg <= 0:
        raise ValueError("Total quantity must be greater than 0")

    if len(markets) != len(quantities_kg):
        raise ValueError(
            "Markets and quantities must have same length"
        )

    total_allocated = sum(quantities_kg)

    if round(total_allocated, 2) != round(total_quantity_kg, 2):
        raise ValueError(
            "Allocated quantity must equal total quantity"
        )

    market_results = []

    total_gross_value = 0
    total_cost = 0
    total_net_realisation = 0

    for market, quantity in zip(markets, quantities_kg):

        if quantity <= 0:
            continue

        capacity = market.get(
            "capacity_kg",
            total_quantity_kg
        )

        if quantity > capacity:
            raise ValueError(
                f"{market['market_name']} capacity is only "
                f"{capacity} kg"
            )

        result = calculate_net_realisation(
            quantity_kg=quantity,
            price_per_quintal=market["modal_price"],
            distance_km=market["distance_km"],
            market_charge_percent=market.get(
                "market_charge_percent",
                1.0
            ),
            other_cost_per_kg=market.get(
                "other_cost_per_kg",
                0.50
            )
        )

        percentage = (
            quantity / total_quantity_kg
        ) * 100

        market_results.append({

            "market_name": market["market_name"],

            "percentage": round(
                percentage,
                2
            ),

            "quantity_kg": round(
                quantity,
                2
            ),

            "capacity_kg": capacity,

            "price_per_quintal":
                market["modal_price"],

            "distance_km":
                result["distance_km"],

            "gross_value":
                result["gross_value"],

            "transport_cost":
                result["transport_cost"],

            "market_charges":
                result["market_charges"],

            "other_costs":
                result["other_costs"],

            "total_cost":
                result["total_cost"],

            "net_realisation":
                result["net_realisation"],

            "net_realisation_per_kg":
                result["net_realisation_per_kg"]
        })

        total_gross_value += result["gross_value"]
        total_cost += result["total_cost"]
        total_net_realisation += result["net_realisation"]

    return {

        "total_quantity_kg":
            total_quantity_kg,

        "total_gross_value":
            round(total_gross_value, 2),

        "total_cost":
            round(total_cost, 2),

        "total_net_realisation":
            round(total_net_realisation, 2),

        "markets":
            market_results
    }


# =========================================================
# FIND BEST MARKET SPLIT
# =========================================================

def find_best_split(
    total_quantity_kg: float,
    markets: list
):

    if total_quantity_kg <= 0:
        raise ValueError(
            "Total quantity must be greater than 0"
        )

    if len(markets) < 2:
        raise ValueError(
            "At least two markets are required"
        )

    if len(markets) > 3:
        raise ValueError(
            "Maximum three markets are supported"
        )

    # -----------------------------------------------------
    # TOTAL CAPACITY
    # -----------------------------------------------------

    total_capacity = sum(
        market.get(
            "capacity_kg",
            total_quantity_kg
        )
        for market in markets
    )

    if total_capacity < total_quantity_kg:

        raise ValueError(
            "Total market capacity is not enough "
            "for the farmer's quantity"
        )

    best_result = None
    best_quantities = None

    step = 10

    # =====================================================
    # TWO MARKETS
    # =====================================================

    if len(markets) == 2:

        for percentage_a in range(
            0,
            101,
            step
        ):

            percentage_b = (
                100 - percentage_a
            )

            quantity_a = (
                total_quantity_kg
                * percentage_a
                / 100
            )

            quantity_b = (
                total_quantity_kg
                * percentage_b
                / 100
            )

            capacity_a = markets[0].get(
                "capacity_kg",
                total_quantity_kg
            )

            capacity_b = markets[1].get(
                "capacity_kg",
                total_quantity_kg
            )

            if quantity_a > capacity_a:
                continue

            if quantity_b > capacity_b:
                continue

            result = calculate_partial_selling(
                total_quantity_kg=total_quantity_kg,
                markets=markets,
                quantities_kg=[
                    quantity_a,
                    quantity_b
                ]
            )

            if (
                best_result is None
                or
                result["total_net_realisation"]
                >
                best_result["total_net_realisation"]
            ):

                best_result = result

                best_quantities = [
                    quantity_a,
                    quantity_b
                ]

    # =====================================================
    # THREE MARKETS
    # =====================================================

    if len(markets) == 3:

        for percentage_a in range(
            0,
            101,
            step
        ):

            for percentage_b in range(
                0,
                101 - percentage_a,
                step
            ):

                percentage_c = (
                    100
                    - percentage_a
                    - percentage_b
                )

                quantity_a = (
                    total_quantity_kg
                    * percentage_a
                    / 100
                )

                quantity_b = (
                    total_quantity_kg
                    * percentage_b
                    / 100
                )

                quantity_c = (
                    total_quantity_kg
                    * percentage_c
                    / 100
                )

                capacity_a = markets[0].get(
                    "capacity_kg",
                    total_quantity_kg
                )

                capacity_b = markets[1].get(
                    "capacity_kg",
                    total_quantity_kg
                )

                capacity_c = markets[2].get(
                    "capacity_kg",
                    total_quantity_kg
                )

                if quantity_a > capacity_a:
                    continue

                if quantity_b > capacity_b:
                    continue

                if quantity_c > capacity_c:
                    continue

                result = calculate_partial_selling(
                    total_quantity_kg=total_quantity_kg,
                    markets=markets,
                    quantities_kg=[
                        quantity_a,
                        quantity_b,
                        quantity_c
                    ]
                )

                if (
                    best_result is None
                    or
                    result["total_net_realisation"]
                    >
                    best_result["total_net_realisation"]
                ):

                    best_result = result

                    best_quantities = [
                        quantity_a,
                        quantity_b,
                        quantity_c
                    ]

    # =====================================================
    # CHECK RESULT
    # =====================================================

    if best_result is None:

        raise ValueError(
            "No feasible market allocation found"
        )

    # =====================================================
    # RECOMMENDED SPLIT
    # =====================================================

    recommended_split = {}

    for market, quantity in zip(
        markets,
        best_quantities
    ):

        percentage = (
            quantity
            / total_quantity_kg
        ) * 100

        recommended_split[
            market["market_name"]
        ] = round(
            percentage,
            2
        )

    # =====================================================
    # ACTIVE MARKETS
    # =====================================================

    active_markets = [

        market_name

        for market_name, percentage
        in recommended_split.items()

        if percentage > 0
    ]

    # =====================================================
    # FIND BEST NET REALISATION PER KG
    # =====================================================

    best_market = max(
        best_result["markets"],
        key=lambda x:
            x["net_realisation_per_kg"]
    )

    best_market_name = best_market[
        "market_name"
    ]

    best_net_per_kg = best_market[
        "net_realisation_per_kg"
    ]

    # =====================================================
    # RECOMMENDATION REASON
    # =====================================================

    if len(active_markets) == 1:

        recommendation_reason = (

            f"{best_market_name} is recommended because "
            f"it provides the highest feasible net return "
            f"of ₹{best_net_per_kg:.2f} per kg."
        )

    else:

        recommendation_reason = (

            f"{best_market_name} provides the highest "
            f"net return of ₹{best_net_per_kg:.2f} per kg, "
            "but the available quantity is distributed "
            "among multiple markets because of capacity "
            "constraints."
        )

    # =====================================================
    # FINAL RESPONSE
    # =====================================================

    return {

        "total_quantity_kg":
            total_quantity_kg,

        "recommended_split":
            recommended_split,

        "recommendation_reason":
            recommendation_reason,

        "best_market":
            best_market_name,

        "best_net_realisation_per_kg":
            best_net_per_kg,

        "highest_net_realisation":
            best_result[
                "total_net_realisation"
            ],

        "total_cost":
            best_result[
                "total_cost"
            ],

        "total_gross_value":
            best_result[
                "total_gross_value"
            ],

        "markets":
            best_result[
                "markets"
            ]
    }