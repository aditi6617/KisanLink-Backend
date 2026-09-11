from services.net_realisation import calculate_net_realisation


def compare_markets(
    quantity_kg: float,
    markets: list
):

    results = []

    # ==================================================
    # CALCULATE EACH MARKET
    # ==================================================

    for market in markets:

        result = calculate_net_realisation(

            quantity_kg=quantity_kg,

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


        # ==================================================
        # STORE MARKET RESULT
        # ==================================================

        results.append({

            "market_name": market["market_name"],

            "price_per_quintal": market["modal_price"],

            "distance_km": result["distance_km"],

            "gross_value": result["gross_value"],

            "transport_cost": result["transport_cost"],

            "market_charges": result["market_charges"],

            "other_costs": result["other_costs"],

            "total_cost": result["total_cost"],

            "net_realisation": result["net_realisation"],

            "net_realisation_per_kg": result[
                "net_realisation_per_kg"
            ]

        })


    # ==================================================
    # SORT BY HIGHEST NET REALISATION
    # ==================================================

    results.sort(
        key=lambda x: x["net_realisation"],
        reverse=True
    )


    # ==================================================
    # FIND BEST MARKET
    # ==================================================

    best_market = results[0]


    # ==================================================
    # FINAL RESPONSE
    # ==================================================

    return {

        "quantity_kg": quantity_kg,

        "recommended_market": best_market[
            "market_name"
        ],

        "highest_net_realisation": best_market[
            "net_realisation"
        ],

        "highest_net_realisation_per_kg": best_market[
            "net_realisation_per_kg"
        ],

        "markets": results

    }