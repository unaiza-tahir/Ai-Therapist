"""
backend/main.py
FastAPI app that exposes a /whatsapp webhook for Twilio.
Twilio POSTs incoming WhatsApp messages here; we run them through
the LangGraph agent (ai_agent.py) and reply back as TwiML.
"""

from dotenv import load_dotenv
load_dotenv()

import logging

from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse

from ai_agent import graph, SYSTEM_PROMPT, parse_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("safespace-backend")

app = FastAPI(title="SafeSpace AI Therapist Backend")


@app.get("/")
async def root():
    """Simple health check so you (and uptime pingers) can verify the service is alive."""
    return {"status": "ok", "service": "safespace-ai-agent"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Twilio calls this endpoint (as application/x-www-form-urlencoded)
    whenever a WhatsApp message comes in on the Sandbox number.
    Expected form fields include: Body, From, To, ProfileName, etc.
    """
    try:
        form = await request.form()
        user_msg = form.get("Body", "").strip()
        from_number = form.get("From", "unknown")

        logger.info(f"Incoming WhatsApp message from {from_number}: {user_msg[:200]}")

        if not user_msg:
            reply_text = "Mujhe aapka message samajh nahi aaya. Please dobara likhein."
        else:
            inputs = {
                "messages": [
                    ("system", SYSTEM_PROMPT),
                    ("user", user_msg),
                ]
            }
            stream = graph.stream(inputs, stream_mode="updates")
            tool_called_name, final_response = parse_response(stream)

            logger.info(f"Tool called: {tool_called_name}")

            reply_text = final_response or (
                "Sorry, mujhe abhi response generate karne mein thodi dikkat ho rahi hai. "
                "Please thodi der baad phir try karein."
            )

    except Exception as e:
        logger.exception("Error while handling WhatsApp webhook")
        reply_text = (
            "Kuch technical issue aa gaya hai. Agar ye emergency hai, please turant "
            "apni local emergency helpline par call karein."
        )

    twiml_response = MessagingResponse()
    twiml_response.message(reply_text)

    return Response(content=str(twiml_response), media_type="application/xml")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)