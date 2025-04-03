import os
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
import json
from app.core.database import create_table, file_exists, insert_json_data
from app.core.elastic import get_es_client, index_data_to_es
from app.core.config import ES_INDEX
from app.services.resume_service import clean_resume_data, get_postgresql_data
from app.services.resume_service import delete_all_documents, delete_es_index

router = APIRouter()


# Endpoint to upload a JSON file to PostgreSQL
@router.post("/upload-json-files/")
async def upload_json_files(file: UploadFile = File(...)):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON files are allowed")
    
    if file_exists(file.filename):
        return {"message": "File already exists. Skipping insert.", "file_name": file.filename}
    
    json_data = json.loads(await file.read())
    insert_json_data(file.filename, json_data)
    return {"message": "File uploaded successfully", "file_name": file.filename}

# Endpoint to upload a folder containing JSON files to PostgreSQL
@router.post("/upload-folder/")
async def upload_folder(folder_path: str):
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=400, detail="Folder does not exist")
    
    if not os.path.isdir(folder_path):
        raise HTTPException(status_code=400, detail="Provided path is not a folder")
    
    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    
    if not json_files:
        raise HTTPException(status_code=400, detail="No JSON files found in the folder")
    
    inserted_files = []
    skipped_files = []
    
    for file_name in json_files:
        if file_exists(file_name):
            skipped_files.append(file_name)
            continue
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)
        insert_json_data(file_name, json_data)
        inserted_files.append(file_name)
    
    return {
        "message": "Upload process completed",
        "uploaded_files": inserted_files,
        "skipped_files": skipped_files
    }

# Endpoint to check Elasticsearch connection
@router.get("/check-es-connection/")
async def check_es():
    try:
        es = get_es_client()  # Create Elasticsearch client inside the function
        if es.ping():
            return {"message": "Connected to Elasticsearch"}
        else:
            return {"error": "Failed to connect to Elasticsearch"}
    except Exception as e:
        return {"error": str(e)}

# Endpoint to index data from PostgreSQL into Elasticsearch
@router.post("/index-data/")
async def index_data():
    try:
        index_data_to_es(get_postgresql_data, clean_resume_data)  # Calls the function to index data from PostgreSQL to Elasticsearch
        return {"message": "Data indexed successfully from PostgreSQL to Elasticsearch"}
    except Exception as e:
        return {"error": str(e)}

# Endpoint to check Elasticsearch connection
@router.get("/check-es-connection/")
async def check_es():
    try:
        es = get_es_client()  # Create Elasticsearch client inside the function
        if es.ping():
            return {"message": "Connected to Elasticsearch"}
        else:
            return {"error": "Failed to connect to Elasticsearch"}
    except Exception as e:
        return {"error": str(e)}
    
# Endpoint to fetch all data from Elasticsearch
@router.get("/get-all-data/")
async def get_all_data():
    es = get_es_client()  # Create Elasticsearch client inside the function
    query = {
        "query": {
            "match_all": {}
        }
    }
    results = es.search(index=ES_INDEX, body=query, size=1000)  # Fetching a larger batch if needed
    hits = results["hits"]["hits"]
    total_count = results["hits"]["total"]["value"]  # Total count of documents in the index

    return {
        "message": f"Data retrieved successfully. Total documents: {total_count}",
        "total_count": total_count,
        "data": [hit["_source"] for hit in hits]
    }


# Endpoint to search for a specific resume by name in Elasticsearch
@router.get("/search-elasticsearch/")
async def search_es(name: str):
    es = get_es_client()  # Create Elasticsearch client inside the function
    query = {
        "query": {
            "match": {
                "resume_data.Name": name
            }
        }
    }
    results = es.search(index=ES_INDEX, body=query)
    hits = results["hits"]["hits"]
    match_count = len(hits)  # Count of matched documents

    return {
        "message": f"Found {match_count} matching results",
        "matched_count": match_count,
        "data": [hit["_source"] for hit in hits]
    }


@router.get("/search_with_keywords/")
async def search_with_keywords(
    keyword: str = Query(..., description="Enter skill, experience, achievement, or any context"),
    min_experience: int = Query(None, description="Minimum years of experience (optional)")
):
    es = get_es_client()
    
    search_query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": keyword,
                            "fields": [
                                "resume_data.Skills^3",  # Boosting skills field
                                "resume_data.Experience.title^2",
                                "resume_data.Experience.description",
                                "resume_data.Key Accomplishments^2",
                                "resume_data.Years of Experience"
                            ],
                            "fuzziness": "AUTO"  # Allows small typos
                        }
                    }
                ]
            }
        },
        "size": 50  # Return up to 50 results
    }

    if min_experience is not None:
        search_query["query"]["bool"]["filter"] = [
            {
                "range": {
                    "resume_data.Years of Experience": {
                        "gte": min_experience
                    }
                }
            }
        ]

    results = es.search(index=ES_INDEX, body=search_query)
    hits = results["hits"]["hits"]

    return {
        "message": f"Found {len(hits)} matching candidates",
        "matched_count": len(hits),
        "data": [hit["_source"] for hit in hits]
    }


@router.get("/search_by_context/")
async def search_by_context(
    prompt: str = Query(..., description="Enter a context to search for relevant candidates")
):
    es = get_es_client()
    
    search_query = {
        "query": {
            "multi_match": {
                "query": prompt,
                "fields": [
                    "resume_data.*"  # Search across all fields inside resume_data
                ],
                "fuzziness": "AUTO",  # Allows for minor typos
                "operator": "or"
            }
        },
        "size": 50  # Return up to 50 relevant results
    }

    results = es.search(index=ES_INDEX, body=search_query)
    hits = results["hits"]["hits"]

    return {
        "message": f"Found {len(hits)} candidates matching the context",
        "matched_count": len(hits),
        "data": [hit["_source"] for hit in hits]
    }

@router.post("/delete-all-data/")
async def delete_all_data(delete_index: bool = False):
    try:
        if delete_index:
            delete_es_index()  # Delete entire index
        else:
            delete_all_documents()  # Delete all documents, keep the index
        return {"message": "Data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))