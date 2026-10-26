from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.database import Base, engine
from app.routers import firms, investors, matching

# Create all tables (the routers above import the models, so they are registered)
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
    allow_headers=["*"],
)

app.include_router(investors.router)
app.include_router(firms.router)
app.include_router(matching.router)


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
