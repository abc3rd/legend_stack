from fastapi import FastAPI
from stripe_routes import router as stripe_router

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Legendary Leads API is live"}

app.include_router(stripe_router)
