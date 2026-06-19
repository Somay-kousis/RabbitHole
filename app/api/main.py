from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.courtroom import router as courtroom_router
from app.api.routes.health import router as health_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(courtroom_router)
