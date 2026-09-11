from datetime import date

from database import SessionLocal, engine, Base

from models.market import Market
from models.market_price import MarketPrice


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# DATABASE SESSION
# =========================================================

db = SessionLocal()


try:

    # =====================================================
    # MARKET DATA
    # =====================================================

    markets_data = [

        {
            "name": "Pune APMC",
            "city": "Pune",
            "latitude": 18.5204,
            "longitude": 73.8567,
            "capacity_kg": 400
        },

        {
            "name": "Sangli APMC",
            "city": "Sangli",
            "latitude": 16.8524,
            "longitude": 74.5815,
            "capacity_kg": 300
        },

        {
            "name": "Kolhapur APMC",
            "city": "Kolhapur",
            "latitude": 16.7050,
            "longitude": 74.2433,
            "capacity_kg": 500
        }

    ]


    # =====================================================
    # CREATE / UPDATE MARKETS
    # =====================================================

    for data in markets_data:

        market = (
            db.query(Market)
            .filter(
                Market.name == data["name"]
            )
            .first()
        )

        if market is None:

            market = Market(
                name=data["name"],
                city=data["city"],
                latitude=data["latitude"],
                longitude=data["longitude"],
                capacity_kg=data["capacity_kg"]
            )

            db.add(market)

        else:

            market.city = data["city"]
            market.latitude = data["latitude"]
            market.longitude = data["longitude"]
            market.capacity_kg = data["capacity_kg"]


    db.commit()


    # =====================================================
    # DELETE OLD MARKET PRICES
    # =====================================================

    db.query(MarketPrice).delete()

    db.commit()


    # =====================================================
    # MARKET PRICE DATA
    # =====================================================

    prices_data = [

        # =================================================
        # TOMATO
        # =================================================

        {
            "crop_name": "Tomato",
            "market_name": "Pune APMC",
            "min_price": 1100,
            "max_price": 1100,
            "modal_price": 1100
        },

        {
            "crop_name": "Tomato",
            "market_name": "Sangli APMC",
            "min_price": 1000,
            "max_price": 1000,
            "modal_price": 1000
        },

        {
            "crop_name": "Tomato",
            "market_name": "Kolhapur APMC",
            "min_price": 1000,
            "max_price": 1000,
            "modal_price": 1000
        },


        # =================================================
        # ONION
        # =================================================

        {
            "crop_name": "Onion",
            "market_name": "Pune APMC",
            "min_price": 2750,
            "max_price": 2750,
            "modal_price": 2750
        },

        {
            "crop_name": "Onion",
            "market_name": "Sangli APMC",
            "min_price": 3350,
            "max_price": 3350,
            "modal_price": 3350
        },

        {
            "crop_name": "Onion",
            "market_name": "Kolhapur APMC",
            "min_price": 3200,
            "max_price": 3200,
            "modal_price": 3200
        },


        # =================================================
        # POTATO
        # =================================================

        {
            "crop_name": "Potato",
            "market_name": "Pune APMC",
            "min_price": 1000,
            "max_price": 1000,
            "modal_price": 1000
        },

        {
            "crop_name": "Potato",
            "market_name": "Sangli APMC",
            "min_price": 1150,
            "max_price": 1150,
            "modal_price": 1150
        },

        {
            "crop_name": "Potato",
            "market_name": "Kolhapur APMC",
            "min_price": 1800,
            "max_price": 1800,
            "modal_price": 1800
        }

    ]


    # =====================================================
    # ADD MARKET PRICES
    # =====================================================

    today = date.today()


    for data in prices_data:

        market_price = MarketPrice(

            crop_name=data["crop_name"],

            market_name=data["market_name"],

            date=today,

            min_price=data["min_price"],

            max_price=data["max_price"],

            modal_price=data["modal_price"]

        )

        db.add(market_price)


    db.commit()


    # =====================================================
    # SUCCESS MESSAGE
    # =====================================================

    print("")
    print("==============================================")
    print("KisanLink market data seeded successfully!")
    print("==============================================")


    print("")
    print("Market capacities:")

    print("Pune APMC       : 400 kg")
    print("Sangli APMC     : 300 kg")
    print("Kolhapur APMC   : 500 kg")


    print("")
    print("Crops added:")

    print("Tomato")
    print("Onion")
    print("Potato")


    print("")
    print("Market prices added successfully!")

    print("==============================================")


except Exception as e:

    db.rollback()

    print("")
    print("ERROR while seeding database:")
    print(e)
    print("")

    raise


finally:

    db.close()
    +