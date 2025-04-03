from fastapi import FastAPI
from app.api.routes import router
from app.core.database import create_table
from app.core.elastic import create_es_index
import uvicorn

# Initialize FastAPI app
app = FastAPI(title="Resume Search API", description="API for uploading and searching resumes")

# Include API routes
app.include_router(router)

# Initialize database and Elasticsearch index on startup
@app.on_event("startup")
def startup_event():
    create_table()  # Ensure database table exists
    create_es_index()  # Ensure Elasticsearch index exists

# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)