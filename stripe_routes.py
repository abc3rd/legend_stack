from fastapi import APIRouter, Request
import json

router = APIRouter()

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    data = json.loads(payload)
    # TODO: Add Stripe signature verification and tier access logic
    print("Stripe event received:", data)
    return {"status": "received"}
