from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext

from database import Base, engine, SessionLocal

from models.farmer import Farmer
from models.crop import Crop
from models.market import Market
from models.market_price import MarketPrice

from services.net_realisation import calculate_net_realisation
from services.market_comparison import compare_markets
from services.road_distance import calculate_road_distance_km
from services.partial_selling import find_best_split


# ==================================================
# PASSWORD SECURITY
# ==================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ==================================================
# DATABASE
# ==================================================

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI(
    title="KisanLink API"
)


# ==================================================
# SIGNUP REQUEST MODEL
# ==================================================

class SignupRequest(BaseModel):
    name: str
    location: str
    phone: str
    email: str | None = None
    password: str
class LoginRequest(BaseModel):
    phone: str
    password: str


# ==================================================
# SIGNUP
# ==================================================

@app.post("/signup")
def signup(
    data: SignupRequest,
    db: Session = Depends(get_db)
):

    # Check phone number
    existing_farmer = (
        db.query(Farmer)
        .filter(Farmer.phone == data.phone)
        .first()
    )

    if existing_farmer:
        raise HTTPException(
            status_code=400,
            detail="Phone number already registered"
        )


    # Check email
    if data.email:

        existing_email = (
            db.query(Farmer)
            .filter(Farmer.email == data.email)
            .first()
        )

        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )


    # Hash password
    password_hash = pwd_context.hash(
        data.password
    )


    # Create farmer
    farmer = Farmer(
        name=data.name,
        location=data.location,
        phone=data.phone,
        email=data.email,
        password_hash=password_hash
    )


    db.add(farmer)
    db.commit()
    db.refresh(farmer)


    return {
        "message": "Farmer registered successfully!",
        "farmer_id": farmer.id,
        "name": farmer.name
    }
# ==================================================
# LOGIN
# ==================================================

@app.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    # Find farmer by phone number
    farmer = (
        db.query(Farmer)
        .filter(Farmer.phone == data.phone)
        .first()
    )

    # Check if farmer exists
    if not farmer:
        raise HTTPException(
            status_code=401,
            detail="Invalid phone number or password"
        )

    # Check password
    if not pwd_context.verify(
        data.password,
        farmer.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid phone number or password"
        )

    # Successful login
    return {
        "message": "Login successful!",
        "farmer_id": farmer.id,
        "name": farmer.name,
        "location": farmer.location
    }


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():

    return {
        "message": "KisanLink Backend is running!"
    }


# ==================================================
# PRICE DISCOVERY
# ==================================================

@app.get("/prices/{crop_name}")
def get_prices(
    crop_name: str,
    db: Session = Depends(get_db)
):

    prices = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.crop_name.ilike(crop_name)
        )
        .all()
    )

    if not prices:

        return {
            "message":
                f"No price data found for {crop_name}"
        }

    return prices


# ==================================================
# NET REALISATION
# ==================================================

@app.get("/net-realisation")
def net_realisation(

    quantity_kg: float,

    price_per_quintal: float,

    distance_km: float,

    market_charge_percent: float = 1.0,

    other_cost_per_kg: float = 0.50

):

    result = calculate_net_realisation(

        quantity_kg=quantity_kg,

        price_per_quintal=price_per_quintal,

        distance_km=distance_km,

        market_charge_percent=
            market_charge_percent,

        other_cost_per_kg=
            other_cost_per_kg

    )

    return result


# ==================================================
# MARKET COMPARISON
# ==================================================

@app.post("/compare-markets")
def compare_market_options(

    crop_name: str,

    quantity_kg: float,

    farmer_latitude: float,

    farmer_longitude: float,

    db: Session = Depends(get_db)

):

    # --------------------------------------------------
    # GET CROP PRICES
    # --------------------------------------------------

    prices = (

        db.query(MarketPrice)

        .filter(
            MarketPrice.crop_name.ilike(crop_name)
        )

        .all()

    )


    if not prices:

        return {

            "message":
                f"No market price data found for {crop_name}"

        }


    # --------------------------------------------------
    # GET MARKETS
    # --------------------------------------------------

    market_records = (

        db.query(Market)

        .all()

    )


    market_lookup = {

        market.name: market

        for market in market_records

    }


    # --------------------------------------------------
    # PREPARE MARKETS
    # --------------------------------------------------

    markets = []


    for price in prices:

        market = market_lookup.get(
            price.market_name
        )


        if market is None:
            continue


        # --------------------------------------------------
        # ROAD DISTANCE
        # --------------------------------------------------

        distance_km = calculate_road_distance_km(

            farmer_latitude,

            farmer_longitude,

            market.latitude,

            market.longitude

        )


        # --------------------------------------------------
        # DISTANCE FALLBACK
        # --------------------------------------------------

        if distance_km is None:

            distance_km = 0


        markets.append({

            "market_name":
                market.name,

            "modal_price":
                price.modal_price,

            "distance_km":
                distance_km,

            "capacity_kg":
                getattr(
                    market,
                    "capacity_kg",
                    quantity_kg
                ),

            "market_charge_percent":
                1.0,

            "other_cost_per_kg":
                0.50

        })


    # --------------------------------------------------
    # CHECK MARKETS
    # --------------------------------------------------

    if not markets:

        return {

            "message":
                "No matching markets found."

        }


    # --------------------------------------------------
    # COMPARE
    # --------------------------------------------------

    result = compare_markets(

        quantity_kg=quantity_kg,

        markets=markets

    )


    return result


# ==================================================
# PARTIAL SELLING
# ==================================================

@app.post("/partial-selling")
def partial_selling(

    crop_name: str,

    quantity_kg: float,

    farmer_latitude: float,

    farmer_longitude: float,

    db: Session = Depends(get_db)

):

    # --------------------------------------------------
    # GET CROP PRICES
    # --------------------------------------------------

    prices = (

        db.query(MarketPrice)

        .filter(
            MarketPrice.crop_name.ilike(crop_name)
        )

        .all()

    )


    if not prices:

        return {

            "message":
                f"No market price data found for {crop_name}"

        }


    # --------------------------------------------------
    # GET MARKETS
    # --------------------------------------------------

    market_records = (

        db.query(Market)

        .all()

    )


    market_lookup = {

        market.name: market

        for market in market_records

    }


    # --------------------------------------------------
    # PREPARE MARKETS
    # --------------------------------------------------

    markets = []


    for price in prices:

        market = market_lookup.get(
            price.market_name
        )


        if market is None:
            continue


        # --------------------------------------------------
        # ROAD DISTANCE
        # --------------------------------------------------

        distance_km = calculate_road_distance_km(

            farmer_latitude,

            farmer_longitude,

            market.latitude,

            market.longitude

        )


        # --------------------------------------------------
        # DISTANCE FALLBACK
        # --------------------------------------------------

        if distance_km is None:

            distance_km = 0


        markets.append({

            "market_name":
                market.name,

            "modal_price":
                price.modal_price,

            "distance_km":
                distance_km,

            "capacity_kg":
                getattr(
                    market,
                    "capacity_kg",
                    quantity_kg
                ),

            "market_charge_percent":
                1.0,

            "other_cost_per_kg":
                0.50

        })


    # --------------------------------------------------
    # CHECK MARKETS
    # --------------------------------------------------

    if len(markets) < 2:

        return {

            "message":
                "At least two markets are required."

        }


    # --------------------------------------------------
    # FIND BEST SPLIT
    # --------------------------------------------------

    result = find_best_split(

        total_quantity_kg=quantity_kg,

        markets=markets

    )


    return result