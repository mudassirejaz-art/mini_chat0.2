# app/routes/image_routes.py
from fastapi import APIRouter
from pydantic import BaseModel
import requests
import os

router = APIRouter()

class ImageRequest(BaseModel):
    prompt: str

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_API_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

@router.post("/generate")
async def generate_image(req: ImageRequest):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {STABILITY_API_KEY}",
    }

    body = {
        "steps": 30,
        "width": 1024,    # ✅ valid size
        "height": 1024,   # ✅ valid size
        "cfg_scale": 7,
        "samples": 1,
        "text_prompts": [{"text": req.prompt, "weight": 1}],
    }

    response = requests.post(STABILITY_API_URL, headers=headers, json=body)

    if response.status_code != 200:
        return {"error": response.text}

    try:
        data = response.json()
        if "artifacts" not in data or len(data["artifacts"]) == 0:
            return {"error": "No image returned from Stability API."}

        image_base64 = data["artifacts"][0]["base64"]
        return {"image_base64": f"data:image/png;base64,{image_base64}"}

    except Exception as e:
        return {"error": str(e)}
