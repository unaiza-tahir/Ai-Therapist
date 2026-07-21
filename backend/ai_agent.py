from langchain.agents import tool
from tools import query_medgemma, call_emergency

@tool
def ask_mental_health_specialist(query: str) -> str:
    """
    Generate a therapeutic response using the MedGemma model.
    Use this for all general user queries, mental health questions, emotional concerns,
    or to offer empathetic, evidence-based guidance in a conversational tone.
    """
    return query_medgemma(query)


@tool
def emergency_call_tool() -> None:
    """
    Place an emergency call to the safety helpline's phone number via Twilio.
    Use this only if the user expresses suicidal ideation, intent to self-harm,
    or describes a mental health emergency requiring immediate help.
    """
    call_emergency()


from geopy.geocoders import Nominatim
import requests

geolocator = Nominatim(user_agent="safespace-ai-therapist")

@tool
def find_nearby_therapists_by_location(location: str) -> str:
    """
    Finds real therapists near the specified location using OpenStreetMap (Nominatim + Overpass API).

    Args:
        location (str): The city or area to search.

    Returns:
        str: A list of therapist names, addresses, and phone numbers.
    """
    # Step 1: Location ko lat/lng mein convert karna
    geocode_result = geolocator.geocode(location)

    if not geocode_result:
        return "Location not found"

    lat, lng = geocode_result.latitude, geocode_result.longitude

    # Step 2: Overpass API se nearby therapists/clinics dhoondna
    radius = 5000  # meters

    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json][timeout:25];
    (
      node["healthcare"="psychotherapist"](around:{radius},{lat},{lng});
      node["amenity"="doctors"]["healthcare:speciality"~"psychotherapy|psychiatry"](around:{radius},{lat},{lng});
      node["amenity"="clinic"](around:{radius},{lat},{lng});
    );
    out body;
    """

    headers = {"User-Agent": "safespace-ai-therapist"}

    try:
        response = requests.get(overpass_url, params={"data": overpass_query}, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return f"Error contacting Overpass API: {e}"
    except ValueError:
        return "Overpass API server busy or returned invalid response. Please try again in a moment."

    elements = data.get("elements", [])

    if not elements:
        return f"No nearby therapists found near {location}"

    output = [f"Therapists near {location}:"]
    top_results = elements[:5]

    for place in top_results:
        tags = place.get("tags", {})
        name = tags.get("name", "Unknown")
        address_parts = [
            tags.get("addr:street", ""),
            tags.get("addr:housenumber", ""),
            tags.get("addr:city", "")
        ]
        address = " ".join(p for p in address_parts if p) or "Address not available"
        phone = tags.get("phone", tags.get("contact:phone", "Phone not available"))

        output.append(f"- {name} | {address} | {phone}")

    result = "\n".join(output)
    return result


# Step1: Create an AI Agent & Link to backend
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from config import GROQ_API_KEY


tools = [ask_mental_health_specialist, emergency_call_tool, find_nearby_therapists_by_location]
# llm = ChatOpenAI(model="gpt-4", temperature=0.2, api_key=OPENAI_API_KEY)
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.2, api_key=GROQ_API_KEY)
graph = create_react_agent(llm, tools=tools)

SYSTEM_PROMPT = """
You are an AI engine supporting mental health conversations with warmth and vigilance.
You have access to three tools:

1. `ask_mental_health_specialist`: Use this tool to answer all emotional or psychological queries with therapeutic guidance.
2. `find_nearby_therapists_by_location`: Use this tool if the user asks about nearby therapists or if recommending local professional help would be beneficial.
3. `emergency_call_tool`: Use this immediately if the user expresses suicidal thoughts, self-harm intentions, or is in crisis.

Always take necessary action. Respond kindly, clearly, and supportively.
"""

def parse_response(stream):
    tool_called_name = "None"
    final_response = None

    for s in stream:
        # Check if a tool was called
        tool_data = s.get('tools')
        if tool_data:
            tool_messages = tool_data.get('messages')
            if tool_messages and isinstance(tool_messages, list):
                for msg in tool_messages:
                    tool_called_name = getattr(msg, 'name', 'None')

        # Check if agent returned a message
        agent_data = s.get('agent')
        if agent_data:
            messages = agent_data.get('messages')
            if messages and isinstance(messages, list):
                for msg in messages:
                    if msg.content:
                        final_response = msg.content

    return tool_called_name, final_response


"""if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        print(f"Received user input: {user_input[:200]}...")
        inputs = {"messages": [("system", SYSTEM_PROMPT), ("user", user_input)]}
        stream = graph.stream(inputs, stream_mode="updates")
        tool_called_name, final_response = parse_response(stream)
        print("TOOL CALLED: ", tool_called_name)
        print("ANSWER: ", final_response)"""