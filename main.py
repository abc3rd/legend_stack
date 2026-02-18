from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from stripe_routes import router as stripe_router
from transcriber_routes import router as transcriber_router

app = FastAPI(
    title="Legendary Leads API",
    description="API for payment processing and AI text transcription",
    version="1.0.0"
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {
        "message": "Legendary Leads API is live",
        "endpoints": {
            "transcriber_ui": "/api/transcriber",
            "api_docs": "/docs",
            "stripe_webhook": "/webhook",
            "transcriber_api": "/api/transcriber/convert"
        }
    }

# Include routers
app.include_router(stripe_router)
app.include_router(transcriber_router)
