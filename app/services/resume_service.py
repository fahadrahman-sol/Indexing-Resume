import json
from app.core.database import connect_db
from app.core.config import ES_INDEX
# from app.core.elastic import es
from app.core.elastic import get_es_client


# Now use get_es_client to get an Elasticsearch client instead of referring to es directly
def clean_resume_data(resume_data):
    """
    Ensures that fields in resume_data have the expected types.
    If a field is not of the expected type, we set it to None.
    """
    # Your existing clean_resume_data function
    list_fields = ["Skills", "Hobbies", "Languages", "Certifications", "Notable Companies"]
    for field in list_fields:
        if field in resume_data:
            value = resume_data[field]
            if isinstance(value, str):
                if value.strip().upper() == "N/A":
                    resume_data[field] = None
                else:
                    resume_data[field] = None
            elif not isinstance(value, list):
                resume_data[field] = None

    nested_fields = ["Education", "Experience"]
    for field in nested_fields:
        if field in resume_data:
            value = resume_data[field]
            if isinstance(value, str):
                if value.strip().upper() == "N/A":
                    resume_data[field] = None
                else:
                    resume_data[field] = None
            elif isinstance(value, list):
                cleaned = []
                for item in value:
                    if isinstance(item, dict):
                        cleaned.append(item)
                resume_data[field] = cleaned if cleaned else None
            else:
                resume_data[field] = None

    for key, value in resume_data.items():
        if isinstance(value, str) and value.strip().upper() == "N/A":
            resume_data[key] = None

    return resume_data


# Fetch all data from PostgreSQL
def get_postgresql_data():
    query = "SELECT file_name, resume_data FROM all_resume_json;"
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(query)
    records = cur.fetchall()
    cur.close()
    conn.close()
    return records

# Example of using get_es_client in this file, if needed
def index_data_to_es(get_postgresql_data, clean_resume_data):
    es = get_es_client()  # Get the Elasticsearch client
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

def delete_es_index():
    es = get_es_client()

    if es.indices.exists(index=ES_INDEX):
        es.indices.delete(index=ES_INDEX)
        print(f"Index '{ES_INDEX}' deleted successfully.")
    else:
        print(f"Index '{ES_INDEX}' does not exist.")
   

def delete_all_documents():
    es = get_es_client()

    if es.indices.exists(index=ES_INDEX):
        es.delete_by_query(index=ES_INDEX, body={"query": {"match_all": {}}})
        print(f"All documents deleted from index '{ES_INDEX}'.")
    else:
        print(f"Index '{ES_INDEX}' does not exist.")
