# Step1: Setup therapist response tool using Groq cloud API (no local model needed)
from groq import Groq
from config import GROQ_API_KEY

_groq_client = Groq(api_key=GROQ_API_KEY)


def query_medgemma(prompt: str) -> str:
    """
    Calls a cloud LLM (via Groq) with a therapist personality profile.
    Returns responses as an empathic mental health professional.
    """
    system_prompt = """You are Dr. Emily Hartman, a warm and experienced clinical psychologist. 
    Respond to patients with:

    1. Emotional attunement ("I can sense how difficult this must be...")
    2. Gentle normalization ("Many people feel this way when...")
    3. Practical guidance ("What sometimes helps is...")
    4. Strengths-focused support ("I notice how you're...")

    Key principles:
    - Never use brackets or labels
    - Blend elements seamlessly
    - Vary sentence structure
    - Use natural transitions
    - Mirror the user's language level
    - Always keep the conversation going by asking open ended questions to dive into the root cause of patients problem
    """

    try:
        response = _groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=350,
            top_p=0.9,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "I'm having technical difficulties, but I want you to know your feelings matter. Please try again shortly."


# Step2: Setup Twilio calling API tool
from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, EMERGENCY_CONTACT


def call_emergency():
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    call = client.calls.create(
        to=EMERGENCY_CONTACT,
        from_=TWILIO_FROM_NUMBER,
        url="http://demo.twilio.com/docs/voice.xml",  # Can customize message
    )


# Step3: Setup Location tool
