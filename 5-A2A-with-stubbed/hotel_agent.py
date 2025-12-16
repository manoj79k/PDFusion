# hotel_agent.py
from fastapi import FastAPI, HTTPException
from a2a_models import A2ARequest, A2AResponse, A2A_PROTOCOL_VERSION
import uuid

app = FastAPI(title="Hotel Agent (A2A Demo)")

# In real world this would be in a secret manager / env var.
SECRET_TOKEN = "SECRET123"
AGENT_ID = "hotel-agent"

@app.post("/a2a", response_model=A2AResponse)
async def handle_a2a(request: A2ARequest) -> A2AResponse:
    """
    Hotel Agent entrypoint for A2A messages.
    """

     # --- 1. Validate protocol ---
    if request.protocol != A2A_PROTOCOL_VERSION:
        raise HTTPException(status_code=400, detail="Unsupported protocol")
    
     # --- 2. Validate 'receiver' ---
    if request.receiver != AGENT_ID:
        raise HTTPException(status_code=400, detail="Wrong receiver agent")
    
     # --- 3. Validate security token ---
    if request.security.type != "api_key" or request.security.token != SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid security token")
    
    # --- 4. Dispatch by capability ---
    try:
        if request.capability == "search_hotels":
            result_data = search_hotels(request.payload)
        elif request.capability == "book_room":
            result_data = book_room(request.payload)
        else:
            return build_error_response(
                request,
                code="UNKNOWN_CAPABILITY",
                message=f"Capability '{request.capability}' not supported",
            )
    except Exception as ex:
        # In real system: log exception, add correlation id etc.
        return build_error_response(
            request,
            code="INTERNAL_ERROR",
            message=str(ex),
        )

    return A2AResponse(
    protocol=A2A_PROTOCOL_VERSION,
    message_id=str(uuid.uuid4()),
    correlation_id=request.message_id,
    sender=AGENT_ID,
    receiver=request.sender,
    status="SUCCESS",
    result=result_data,
    )


def search_hotels(payload: dict) -> dict:
    """
    Dummy hotel search.
    """
    city = payload.get("city", "Unknown City")
    check_in = payload.get("check_in")
    check_out = payload.get("check_out")
    guests = payload.get("guests")

    # You could call real services / DB here.
    return {
        "query": {
            "city": city,
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests,
        },
        "hotels": [
            {"name": "Riverside Grand", "city": city, "price": 180, "rating": 4.6},
            {"name": "Historic Square Inn", "city": city, "price": 150, "rating": 4.3},
        ],
    }

def book_room(payload: dict) -> dict:
    """
    Dummy booking function.
    """
    reservation_id = str(uuid.uuid4())
    hotel_name = payload.get("hotel_name")
    guest_name = payload.get("guest_name")
    check_in = payload.get("check_in")
    check_out = payload.get("check_out")
    guests = payload.get("guests")

    # Again, here you would call a real booking API / DB.
    total_price = 360.00

    return {
        "reservation_id": reservation_id,
        "hotel_name": hotel_name,
        "guest_name": guest_name,
        "check_in": check_in,
        "check_out": check_out,
        "guests": guests,
        "total_price": total_price,
        "currency": "USD",
    }

def build_error_response(
    request: A2ARequest, code: str, message: str
) -> A2AResponse:
    return A2AResponse(
        protocol=A2A_PROTOCOL_VERSION,
        message_id=str(uuid.uuid4()),
        correlation_id=request.message_id,
        sender=AGENT_ID,
        receiver=request.sender,
        status="ERROR",
        result=None,
        error={"code": code, "message": message},
    )

# -------------------------------------------------------------------
# Local dev entrypoint
# -------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    # Run on all interfaces so it can act as "Machine B"
    uvicorn.run("hotel_agent:app", host="0.0.0.0", port=8000, reload=True)