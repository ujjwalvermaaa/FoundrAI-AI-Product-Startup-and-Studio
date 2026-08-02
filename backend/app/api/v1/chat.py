"""
Chat API — POST /api/v1/chat/message
Streams Foundr AI responses via Ollama.
"""
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.api.deps import get_current_active_user
from app.models.user import User
from app.core.config import settings

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatMessage(BaseModel):
    message: str
    history: list[dict] = []  # [{"role": "user"|"assistant", "content": str}]


SYSTEM_PROMPT = """You are Foundr, an expert AI co-founder and startup advisor built into FoundrAI.
You have deep knowledge of:
- Startup validation, lean methodology, and product-market fit
- Business model design (Osterwalder canvas, pricing, unit economics)
- Market sizing (TAM/SAM/SOM), competitive analysis, positioning
- Product strategy, MVP scoping, roadmapping
- Technical architecture for SaaS and AI products
- Financial modelling, fundraising, pitch decks
- Go-to-market strategy, growth, and marketing

Your style:
- Direct, concise, practical. No fluff.
- Give specific frameworks, numbers, and actionable next steps
- Ask clarifying questions when needed
- Refer users to FoundrAI modules (Idea Validation, Market Research, etc.) when relevant
- Never say you can't help — always give your best answer

Always respond in a conversational but expert tone, as if you're a co-founder who has built multiple companies."""


async def stream_ollama(message: str, history: list[dict]):
    """Stream response from Ollama."""
    import httpx

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history[-10:]:  # last 10 messages for context
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": message})

    payload = {
        "model": settings.ollama_model,
        "messages": messages,
        "stream": True,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": 512,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{settings.ollama_base_url}/api/chat",
                json=payload,
            ) as resp:
                if resp.status_code != 200:
                    yield f"data: {json.dumps({'error': 'Ollama unavailable'})}\n\n"
                    return

                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("message", {}).get("content", "")
                        if token:
                            yield f"data: {json.dumps({'token': token})}\n\n"
                        if chunk.get("done"):
                            yield f"data: {json.dumps({'done': True})}\n\n"
                            return
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@router.post("/message")
async def chat_message(
    body: ChatMessage,
    current_user: User = Depends(get_current_active_user),
):
    """Stream a Foundr AI response."""
    return StreamingResponse(
        stream_ollama(body.message, body.history),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
