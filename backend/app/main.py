import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.chat import router as chat_router
from app.api.query import router as query_router
from app.api.schemes import router as schemes_router
from app.api.compare import router as compare_router
from app.api.documents import router as documents_router
from app.api.checklist import router as checklist_router
from app.api.saved_schemes import router as saved_schemes_router
from seed_data import seed_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("schemesathi-main")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Agentic RAG-Based Government Scheme & Benefits Navigator API",
    version="1.0.0"
)

# Production-ready CORS Middleware
cors_origins = settings.parsed_cors_origins
logger.info(f"Configuring CORS origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under /api
app.include_router(chat_router, prefix=settings.API_V1_STR, tags=["Chat Agent"])
app.include_router(query_router, prefix=settings.API_V1_STR, tags=["RAG Retrieval"])
app.include_router(schemes_router, prefix=settings.API_V1_STR, tags=["Schemes"])
app.include_router(compare_router, prefix=settings.API_V1_STR, tags=["Compare"])
app.include_router(documents_router, prefix=settings.API_V1_STR, tags=["Documents RAG"])
app.include_router(checklist_router, prefix=settings.API_V1_STR, tags=["Checklist"])
app.include_router(saved_schemes_router, prefix=settings.API_V1_STR, tags=["Saved Schemes"])

@app.on_event("startup")
def startup_event():
    logger.info(f"Starting SchemeSathi AI Backend [{settings.ENVIRONMENT.upper()} mode]...")
    seed_database()
    logger.info("Backend initialization completed successfully.")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "database_type": "postgresql" if settings.is_production else "sqlite/postgres",
        "vector_db": "qdrant",
        "llm_configured": bool(settings.effective_llm_key),
        "docs_url": "/docs"
    }

@app.get("/")
def root():
    return {
        "app": settings.PROJECT_NAME,
        "status": "online",
        "health_check": "/health",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
