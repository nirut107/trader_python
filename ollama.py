from fastapi import FastAPI, HTTPException
import ollama
import os
import requests

app = FastAPI()


@app.post("/chat")
def chat(payload: dict, model:str="mistral",):
    prompt = payload.get("prompt")
    
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'mistral',
            'prompt': prompt,
            'stream': False
        }
    )

    print(response.json()['response'])

    return {
        "answer": response.json()['response']
    }
