import os
from dotenv import load_dotenv
from flask import Flask


def load_config(app: Flask) -> None:
    load_dotenv()
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret"),
        OPENWEATHER_API_KEY=os.getenv("OPENWEATHER_API_KEY", ""),
        MAPS_PROVIDER=os.getenv("MAPS_PROVIDER", "google"),
        DEFAULT_CITY=os.getenv("DEFAULT_CITY", "Kyiv"),
        DEFAULT_COUNTRY=os.getenv("DEFAULT_COUNTRY", "Ukraine"),
        TICKETMASTER_API_KEY=os.getenv("TICKETMASTER_API_KEY", ""),
        TICKETMASTER_MARKET=os.getenv("TICKETMASTER_MARKET", "US"),
        TICKETMASTER_DEFAULT_COUNTRY=os.getenv("TICKETMASTER_DEFAULT_COUNTRY", "US"),
        TICKETMASTER_DEFAULT_KEYWORD=os.getenv("TICKETMASTER_DEFAULT_KEYWORD", "tour"),
    )

