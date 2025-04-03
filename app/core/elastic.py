import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from app.core.config import ES_HOST, ES_INDEX, ES_USERNAME, ES_PASSWORD

def get_es_client():
    return Elasticsearch([ES_HOST], basic_auth=(ES_USERNAME, ES_PASSWORD))

def check_es_connection():
    es = get_es_client()
    if not es.ping():
        raise ValueError("Cannot connect to Elasticsearch with provided credentials")

def create_es_index():
    es = get_es_client()
    if not es.indices.exists(index=ES_INDEX):
        es.indices.create(index=ES_INDEX, body={
            "mappings": {
                "properties": {
                    "file_name": {"type": "keyword"},
                    "resume_data": {
                        "properties": {
                            "Name": {"type": "text"},
                            "Email": {"type": "text"},
                            "Phone": {"type": "text"},
                            "Skills": {"type": "keyword"},
                            "Address": {"type": "text"},
                            "Hobbies": {"type": "keyword"},
                            "Education": {
                                "type": "nested",
                                "properties": {
                                    "degree": {"type": "text"},
                                    "institution": {"type": "text"},
                                    "graduation_year": {"type": "keyword"}
                                }
                            },
                            "Languages": {"type": "keyword"},
                            "Experience": {
                                "type": "nested",
                                "properties": {
                                    "dates": {"type": "text"},
                                    "title": {"type": "text"},
                                    "company": {"type": "text"},
                                    "description": {"type": "text"}
                                }
                            },
                            "Certifications": {"type": "keyword"},
                            "Notable Companies": {"type": "keyword"},
                            "Key Accomplishments": {"type": "text"},
                            "Years of Experience": {"type": "text"}
                        }
                    }
                }
            }
        })
        print(f"Index '{ES_INDEX}' created successfully")
    else:
        print(f"Index '{ES_INDEX}' already exists")

def index_data_to_es(get_postgresql_data, clean_resume_data):
    es = get_es_client()
    records = get_postgresql_data()

    if not records:
        print("No data found in PostgreSQL to index.")
        return

    for record in records:
        file_name = record[0]
        resume_data = record[1] if isinstance(record[1], dict) else json.loads(record[1])
        cleaned_data = clean_resume_data(resume_data)
        doc = {"file_name": file_name, "resume_data": cleaned_data}

        try:
            es.index(index=ES_INDEX, document=doc)
            print(f"Indexed document for file: {file_name}")
        except Exception as e:
            print(f"Error indexing document for file {file_name}: {e}")

    print("Data indexed successfully in Elasticsearch")



