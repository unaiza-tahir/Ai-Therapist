from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from xml.etree.ElementTree import Element, tostring

from ai_agent import graph, SYSTEM_PROMPT, parse_response

app = FastAPI()


class AskRequest(BaseModel):
    message: str


def _twiml_message(body: str) -> PlainTextResponse:
    """Create minimal TwiML <Response><Message>...</Message></Response>"""
    response_el = Element('Response')
    message_el = Element('Message')
    message_el.text = body
    response_el.append(message_el)
    xml_bytes = tostring(response_el, encoding='utf-8')
    return PlainTextResponse(content=xml_bytes, media_type='application/xml')


@app.post("/ask")
async def ask(request: AskRequest):
    user_message = request.message

    inputs = {"messages": [("system", SYSTEM_PROMPT), ("user", user_message)]}
    stream = graph.stream(inputs, stream_mode="updates")
    tool_called_name, final_response = parse_response(stream)

    return {"tool_called": tool_called_name, "response": final_response}


@app.post("/whatsapp_ask")
async def whatsapp_ask(
    From: str = Form(...),
    Body: str = Form(...)
):
    user_message = Body
    sender = From

    inputs = {"messages": [("system", SYSTEM_PROMPT), ("user", user_message)]}
    stream = graph.stream(inputs, stream_mode="updates")
    tool_called_name, final_response = parse_response(stream)

    reply_text = final_response if final_response else "Sorry, I couldn't process that. Please try again."

    return _twiml_message(reply_text)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)