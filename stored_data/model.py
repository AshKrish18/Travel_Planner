from sqlalchemy import Column, Integer, String, Float
from stored_data.database import Base


class TouristPlaceModel(Base):
    __tablename__ = "tourist_places"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

class SuggestedPlaceModel(Base):
    __tablename__ = "suggested_places"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False)
    spot_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    estimated_price_inr = Column(Float, nullable=False)