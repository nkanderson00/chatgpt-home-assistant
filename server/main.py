from fastapi import FastAPI, Request
import whisper
import torch
import numpy as np
import time

app = FastAPI()

model = "tiny.en"
device = "cpu"
audio_model = whisper.load_model(model).to(device)

@app.post("/transcribe")
async def transcribe(request: Request):
    audio_data: bytes = await request.body()
    s = time.time()
    torch_audio = torch.from_numpy(np.frombuffer(audio_data, np.int16).flatten().astype(np.float32) / 32768.0)
    result = audio_model.transcribe(torch_audio, language='english')
    print(f"Transcribed in {time.time() - s} seconds")
    print(result["text"])
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=2023)