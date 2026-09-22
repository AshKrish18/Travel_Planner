from pydantic import BaseModel

class tourist_places(BaseModel):
    city : str

class Places(BaseModel):
    city : str
    spot_name : str
    description : str
    estimated_price_inr : float

    
