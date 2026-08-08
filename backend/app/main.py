from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.intelligence import router as intelligence_router

from app.database.database import (
    Base,
    engine,
    SessionLocal,
)

from app.api.routes.productization import (
    router as productization_router,
)

from app.api.routes.weather import (

    router as weather_router,
)

from app.database import models

from app.api.routes.health import (
    router as health_router,
)

from app.api.routes.upload import (
    router as upload_router,
)

from app.api.routes.image import (
    router as image_router,
)

from app.api.routes.history import (
    router as history_router,
)

from app.api.routes.status import (
    router as status_router,
)

from app.api.routes.alerts import (
    router as alert_router,
)

from app.api.routes.farms import (
    router as farm_router,
)

from app.agriculture import initialize_agricultural_knowledge_base
from app.api.routes.agriculture import router as agriculture_router

initialize_agricultural_knowledge_base()

# =========================================================
# Database
# =========================================================

Base.metadata.create_all(
    bind=engine
)


# =========================================================
# FastAPI
# =========================================================

app = FastAPI(
    title="Aegis-Terra API",
    description=(
        "AI-powered crop health analysis "
        "backend for smallholder farms."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# Routes
# =========================================================

app.include_router(
    health_router
)

app.include_router(
    upload_router
)

app.include_router(
    image_router
)

app.include_router(
    history_router
)

app.include_router(
    status_router
)

app.include_router(
    alert_router
)

app.include_router(
    farm_router
)

app.include_router(agriculture_router)
app.include_router(intelligence_router)
app.include_router(
    weather_router
)
app.include_router(
    productization_router
)