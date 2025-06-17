from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

app = FastAPI()

class TierPayload(BaseModel):
    contact_id: str
    email: str

@app.post("/api/tiers/basic")
async def grant_basic_tier(data: TierPayload):
    print(f"✅ Granting BASIC tier to {data.email} ({data.contact_id})")
    # Simulate access control logic here
    return {"status": "Basic tier granted"}

@app.post("/api/tiers/pro")
async def grant_pro_tier(data: TierPayload):
    print(f"✅ Granting PRO tier to {data.email} ({data.contact_id})")
    # Simulate access control logic here
    return {"status": "Pro tier granted"}

@app.post("/api/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    import stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        email = subscription.get("customer_email", "unknown")
        plan_id = subscription["items"]["data"][0]["plan"]["id"]

        print(f"Stripe subscription update received for {email}: {plan_id}")

        if "pro" in plan_id.lower():
            await grant_pro_tier(TierPayload(contact_id="from_stripe", email=email))
        elif "basic" in plan_id.lower():
            await grant_basic_tier(TierPayload(contact_id="from_stripe", email=email))

    return {"status": "Webhook received"}
