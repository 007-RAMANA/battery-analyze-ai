
import os
import hmac
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from groq import Groq

# Load environment variables from backend/.env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
APP_ACCESS_TOKEN = os.getenv("APP_ACCESS_TOKEN", "").strip()
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile",
).strip()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("battery_ai_backend")

app = FastAPI(
    title="Battery AI Backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_methods=["GET", "POST"],
    allow_headers=["X-App-Token", "Content-Type"],
)


class ChatRequest(BaseModel):
    messages: list[dict] = Field(min_length=1, max_length=20)


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
def home():
    return {
        "status": "ok",
        "service": "Battery AI Backend",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    x_app_token: str = Header(
        default="",
        alias="X-App-Token",
    ),
):
    # Check app access token.
    if (
        not APP_ACCESS_TOKEN
        or not hmac.compare_digest(
            x_app_token,
            APP_ACCESS_TOKEN,
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Access denied",
        )

    # Check Groq configuration.
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY is missing.")
        raise HTTPException(
            status_code=503,
            detail="AI service is not configured",
        )

    # Validate incoming chat messages.
    allowed_roles = {"system", "user", "assistant"}
    messages = []

    for item in request.messages:
        role = item.get("role")
        content = item.get("content")

        if role not in allowed_roles:
            raise HTTPException(
                status_code=400,
                detail="Invalid message role",
            )

        if not isinstance(content, str) or not content.strip():
            raise HTTPException(
                status_code=400,
                detail="Message content must be text",
            )

        messages.append({
            "role": role,
            "content": content[:8000],
        })

    try:
        logger.info("Sending chat request to Groq model: %s", GROQ_MODEL)

        client = Groq(api_key=GROQ_API_KEY)

        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=1200,
            timeout=45.0,
        )

        reply = completion.choices[0].message.content or ""

        if not reply.strip():
            raise HTTPException(
                status_code=502,
                detail="AI provider returned an empty response",
            )

        logger.info("Groq response received successfully.")

        return ChatResponse(reply=reply.strip())

    except HTTPException:
        raise

    except Exception as exc:
        # Log the error type and message to the backend console.
        # Never log the API key or access token.
        logger.exception(
            "Groq request failed. Error type: %s",
            type(exc).__name__,
        )

        raise HTTPException(
            status_code=502,
            detail="AI provider request failed",
        ) from None
