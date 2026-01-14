from fastapi import FastAPI, HTTPException
import ollama
import os

app = FastAPI()

API_KEY = os.getenv("API_KEY", "devkey")

@app.post("/chat")
def chat(payload: dict, x_api_key: str | None = None):
    prompt = payload.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing prompt")

    resp = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "answer": resp["message"]["content"]
    }
