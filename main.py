from fastapi import FastAPI, Depends, HTTPException, status, Query
from schemas.saved_tourist_places import tourist_places, Places
from sqlalchemy.orm import Session
from stored_data.database import Base, get_db, engine
from stored_data.model import TouristPlaceModel, SuggestedPlaceModel
from schemas.mapbox import PlaceSearchResponse
from services.mapbox_service import search_places_in_india
import os
from services.gemini_services import making_itenary, budget_estimation, suggestions
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from your local frontend file
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.delete("/travelplanner/pinboard/{place_name}")
def saving_tourist_places(place_name: str, db: Session = Depends(get_db)):
    deleted_place = db.query(TouristPlaceModel).filter(TouristPlaceModel.name == place_name).first()
    if not deleted_place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = f"{place_name} not found in the database"
        )

    db.delete(deleted_place)
    db.commit()

    return {

        "message" : f"{place_name} is deleted from the database"
    }

@app.get("/travelplanner/pinboard")
def get_saved_tourist_places(db: Session = Depends(get_db)):
    saved_places = db.query(TouristPlaceModel).all()
    return {
        "saved places" : saved_places
    }

@app.post("/travelplanner/search-and-pin", status_code=status.HTTP_201_CREATED)
async def search_and_pin_place(
    query: str = Query(..., description="Tourist place name to search and save directly"),
    db: Session = Depends(get_db)
):
    """
    Searches Mapbox for a place and automatically saves the top matching result name to PostgreSQL.
    """
    results = await search_places_in_india(
        query=query,
        limit=1,
        access_token=MAPBOX_ACCESS_TOKEN
    )

    if not results:
        raise HTTPException(
            status_code=404, 
            detail=f"No tourist places found matching '{query}' to save."
        )

    top_result = results[0]

    # Save only the place name to PostgreSQL
    new_place = TouristPlaceModel(
        name=top_result["name"]
    )

    db.add(new_place)
    db.commit()
    db.refresh(new_place)

    return {
        "message": "Tourist place pinned successfully!",
        "pinned_place": new_place
    }

# GET: Fetch all pinned destinations
@app.get("/travelplanner/pinned-places")
def get_pinned_places(db: Session = Depends(get_db)):
    return db.query(TouristPlaceModel).all()


# DELETE: Remove a pinned destination by ID
@app.delete("/travelplanner/pinned-places/{place_id}")
def delete_pinned_place(place_id: int, db: Session = Depends(get_db)):
    place = db.query(TouristPlaceModel).filter(TouristPlaceModel.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Pinned place not found")
    
    db.delete(place)
    db.commit()
    return {"message": f"Deleted {place.name} successfully"}

@app.get("/travelplanner/get_itenary")
async def get_budget_itenery(
    original_place: str = Query(
        ...,
        description="Enter the city where you are form"
    ),
    days: int = Query(
        ...,
        description="Enter no. of days"
    ),
    db: Session = Depends(get_db)
):
    pinned_places = db.query(TouristPlaceModel).all()

    if not pinned_places:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tourist place is pinned"
        )

    result = await making_itenary(
        places=pinned_places,
        day=days,
        original_place=original_place
    )

    return {
        "Itenary":result
    }

@app.get("/travelplanner/budget_calculator")
async def budget_calculator(
    original_place: str = Query(
        ...,
        description="Enter the city where you are from"
    ),
    days: int = Query(
        ...,
        description="Enter the no. of days"
    ),
    db: Session = Depends(get_db)
):
    pinned_places = db.query(TouristPlaceModel).all()
    previous_response = get_budget_itenery(days, db=db,original_place=original_place)

    result = await budget_estimation(
        places=pinned_places,
        responese=previous_response,
        days=days,
        original_place=original_place
    )

    return {
        "Budget which is calculated": result
    }

@app.get("/travelplanner/select-suggestions")
async def discover_places(
    db: Session = Depends(get_db)
):
    
    pinned_places = db.query(TouristPlaceModel).all()

    if not pinned_places:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No city is pinned"
        )

    suggested_spot = await suggestions(pinned_places=pinned_places)

    return {
        "pinned_places" : [p.name for p in pinned_places],
        "suggestion places" : suggested_spot
    }  

@app.post("/travelplanner/select-suggestions/saving-suggestions")
def saving_suggestions(
    city : str,
    spot_name : str,
    description: str,
    estimated_price_inr : float,
    db: Session = Depends(get_db)
):
    new_suggestions = SuggestedPlaceModel(
        city=city,
        spot_name=spot_name,
        description=description,
        estimated_price_inr=estimated_price_inr
    )

    db.add(new_suggestions)
    db.commit()
    db.refresh(new_suggestions)

    return {
        "message" : "tourist_place is saved successfully",
        "place": new_suggestions
    }