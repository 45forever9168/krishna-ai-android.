from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
import json
from gtts import gTTS
import os
import random

app = FastAPI()

# CORS for Android app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

DEEPSEEK_API_KEY = "sk-5453f6b6849c4e4b9214d801df3236c2"
memory = []

def text_to_speech(text: str, lang: str = "en"):
    filename = f"voice_{random.randint(1000,9999)}.mp3"
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    return filename

def detect_language(text):
    if any(char in text for char in "अआइईउऊएऐओऔकखगघचछजझटठडढतथदधनपफबभमयरलवशषसह"):
        return "hi"
    return "en"

@app.post("/krishna")
async def talk_to_krishna(req: Request):
    data = await req.json()
    prompt = data.get("prompt", "")
    lang = detect_language(prompt)

    memory.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "deepseek-chat",
        "messages": memory[-10:],
        "temperature": 0.7
    }

    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        data=json.dumps(body)
    )

    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"]
        memory.append({"role": "assistant", "content": reply})
        voice_file = text_to_speech(reply, lang)
        return {"reply": reply, "voice_file": voice_file}
    else:
        return {"reply": "I'm offline or there was an error.", "voice_file": None}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
