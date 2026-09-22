import os
from google import genai
from stored_data.model import TouristPlaceModel
from dotenv import load_dotenv
import json

load_dotenv()

Gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=Gemini_api_key)

async def making_itenary(places: list[TouristPlaceModel], day : int, original_place: str):
    places_list = places_list = "\n".join([f"- {place.name}" for place in places])

    prompt = f"""
    So the user is from {original_place} and with according to this make the following itenary
    You are an expert Indian travel planner specializing in budget-friendly trips.

    A user has pinned the following tourist destinations to their travel board:
    {places_list}

    The user wants a **{day}-day budget-friendly itinerary** visiting these places.

    Please provide a structured plan covering:
    1. **Day-by-Day Schedule**: Group nearby destinations together to minimize travel distance/cost over {day} days.
    2. **Budget Transport Tips**: Recommend cheap transit options between these spots (e.g., Metro, local buses, shared autos).
    3. **Budget Food & Entry Tips**: Mention inexpensive local food options near these spots and any ticket costs.
    4. **Cost Estimate Summary**: A realistic low-budget cost breakdown for the entire trip.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt   
    )

    return response

async def budget_estimation(places: list[TouristPlaceModel], responese: str, days: int, original_place: str):
    places_list = places_list = "\n".join([f"- {place.name}" for place in places])

    prompt = f"""
So the traveller is from {original_place} and with accordance to this calculate the following budget for the following
You are an expert Indian travel consultant and budget strategist. 

A traveler is planning a {days}-day trip to visit the following pinned tourist destinations:
{places_list}

Generate a comprehensive, low-to-mid range budget calculation breakdown for this trip. 
Format your output cleanly using bold subheadings and direct bullet points.

Include realistic cost estimates in Indian Rupees (INR - ₹) for each of the following categories:

1. ✈️ **Intercity Travel (Flights / Trains)**:
   - Provide estimated round-trip flight/train costs to reach the target city/region.
   - Mention cheaper alternatives (e.g., Sleeper/3AC Train vs. Budget Airfares).

2. 🛺 **Local Transit (Auto, Metro, Bus, Cabs)**:
   - Estimate local transit costs between the pinned spots ({days}-day total).
   - Breakdown options: Metro passes, auto-rickshaw fares, and shared transit tips.

3. 🏨 **Accommodation (Hotels / Hostels)**:
   - Estimated total hotel/hostel cost for {days - 1 if days > 1 else 1} night(s).
   - Options for budget travelers (backpacking hostels, 2-star/3-star budget hotels).

4. 🍱 **Food & Dining**:
   - Estimated daily food budget (breakfast, lunch, dinner, and famous street snacks near the pinned spots).
   - Total food cost for {days} days.

5. 🎟️ **Entry Fees & Activities**:
   - Estimated ticket prices, camera fees, or guide charges for the pinned destinations.

6. 💰 **Grand Total & Budget Summary**:
   - Provide a realistic **Estimated Total Cost per Person (₹)**.
   - Add 2 quick money-saving tips specific to these locations.

Also make the budget with response to {responese} as this is the most ideal budget plan which we have
"""

    result = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return result

async def suggestions(pinned_places: list[TouristPlaceModel]):
   cities_list = ", ".join([place.name for place in pinned_places])

   prompt = f"""
    You are an expert Indian tour guide.
    
    CRITICAL INSTRUCTION: You MUST ONLY suggest tourist spots located strictly within these specific pinned cities:
    {cities_list}

    DO NOT suggest places from Delhi, Mumbai, or any other city not listed above.

    For EACH city listed in [{cities_list}], provide all top famous tourist spots to visit along with their estimated ticket/entry costs in INR.
    so that the user can select which places he can visit.
    Give more than 20 for each places.

    Respond strictly in JSON format matching this structure:
    [
      {{
        "city": "Must match one of the cities in: {cities_list}",
        "spot_name": "Name of Tourist Spot in that city",
        "description": "Brief 1-line highlight of the spot",
        "estimated_price_inr": 150
      }}
    ]

    Do not include markdown code block formatting like ```json. Return raw JSON string only.
    """
   response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

   try:
        raw_text = response.text.strip().removeprefix("```json").removesuffix("```").strip()  
        suggestions = json.loads(raw_text)
        return suggestions
   except Exception as e:
        print(f"Failed to parse gemini input {e}")
        return [] 