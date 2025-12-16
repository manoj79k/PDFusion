import uuid
import os
import requests

from a2a_models import (
    A2ARequest,
    SecurityContext,
    Principal,
    Intent,
    Context,
    Meta,
    A2A_PROTOCOL_VERSION,
)
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

HOTEL_ENDPOINT = "http://localhost:8000/a2a"
SECRET_TOKEN = "SECRET123"
PLANNER_ID = "planner-agent"
HOTEL_AGENT_ID = "hotel-agent"

def send_a2a(capability, payload, trace_id):
    req = A2ARequest(
        protocol=A2A_PROTOCOL_VERSION,
        message_id=str(uuid.uuid4()),
        sender=PLANNER_ID,
        receiver=HOTEL_AGENT_ID,
        capability=capability,
        security=SecurityContext(
            type="api_key",
            token=SECRET_TOKEN,
            principal=Principal(user_id="manoj", scopes=["hotel:search", "hotel:book"]),
        ),
        payload=payload,
        intent=Intent(name="travel_planning"),
        context=Context(conversation_id="conv-123"),
        meta=Meta(trace_id=trace_id),
    )

    resp = requests.post(HOTEL_ENDPOINT, json=req.model_dump())
    resp.raise_for_status()
    return resp.json()

def llm_choose_best_hotel(hotels):
    prompt = f"""
You are the planner agent.

Given this hotel list:
{hotels}

Choose the best hotel for a business traveler. Output ONLY the hotel name.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content.strip()


def demo_flow():
    trace_id = f"trace-{uuid.uuid4()}"

    print("\n=== 1. Planner → Hotel (search_hotels) ===")
    search = send_a2a(
        "search_hotels",
        {
            "city": "Savannah",
            "check_in": "2025-12-20",
            "check_out": "2025-12-22",
            "guests": 2,
        },
        trace_id,
    )
    print("Search Response:", search)
    

    hotels = search["result"]["hotels"]
    print("\nPlanner received hotels:", hotels)
    
if __name__ == "__main__":
    demo_flow()
   
