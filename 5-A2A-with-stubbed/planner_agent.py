# planner_agent.py
import uuid
import requests
from a2a_models import A2ARequest, SecurityContext, A2A_PROTOCOL_VERSION

# If running both on same machine for testing, use localhost.
# In real multi-machine setup, replace with http://<machine-b-ip>:8000/a2a
HOTEL_ENDPOINT = "http://localhost:8000/a2a"

SECRET_TOKEN = "SECRET123"
PLANNER_ID = "planner-agent"
HOTEL_AGENT_ID = "hotel-agent"

def send_a2a_message(capability: str, payload: dict):
    """
    Builds an A2ARequest and sends it via HTTP to the hotel agent.
    """
    security = SecurityContext(type="api_key", token=SECRET_TOKEN)

    req = A2ARequest(
        protocol=A2A_PROTOCOL_VERSION,
        message_id=str(uuid.uuid4()),
        sender=PLANNER_ID,
        receiver=HOTEL_AGENT_ID,
        capability=capability,
        security=security,
        payload=payload,
    )

    response = requests.post(HOTEL_ENDPOINT, json=req.dict())
    response.raise_for_status()  # raise if HTTP 4xx/5xx
    return response.json()

def demo_flow():
    # 1) Planner "reasons" and decides to call search_hotels
    print("=== Step 1: Planner → Hotel search_hotels ===")
    search_response = send_a2a_message(
        "search_hotels",
        {
            "city": "Savannah",
            "check_in": "2025-12-20",
            "check_out": "2025-12-22",
            "guests": 2,
        },
    )
    print("Search Response:", search_response)

    if search_response.get("status") != "SUCCESS":
        print("Hotel search failed:", search_response.get("error"))
        return
    
    hotels = search_response["result"]["hotels"]
    if not hotels:
        print("No hotels found.")
        return
    
     # For simplicity, pick first hotel
    chosen_hotel = hotels[0]
    print("\nPlanner picked hotel:", chosen_hotel["name"])


    # 2) Planner calls book_room capability
    print("\n=== Step 2: Planner → Hotel book_room ===")
    book_response = send_a2a_message(
        "book_room",
        {
            "hotel_name": chosen_hotel["name"],
            "check_in": "2025-12-20",
            "check_out": "2025-12-22",
            "guests": 2,
            "guest_name": "Manoj Kumar",
        },
    )

    print("Booking Response:", book_response)

    if book_response.get("status") == "SUCCESS":
        print("\n✅ Reservation confirmed:")
        print("Reservation ID:", book_response["result"]["reservation_id"])
        print("Hotel:", book_response["result"]["hotel_name"])
        print("Total Price:", book_response["result"]["total_price"], "USD")
    else:
        print("\n❌ Booking failed:", book_response.get("error"))

if __name__ == "__main__":
    demo_flow()
    