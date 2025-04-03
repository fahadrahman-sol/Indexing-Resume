# Indexing Resume and Search 

## Overview
This project is an end-to-end resume indexing and search application built using **FastAPI**, **PostgreSQL**, and **Elasticsearch**. It allows users to upload resume data in JSON format, store it in PostgreSQL, index it in Elasticsearch, and perform efficient search queries.

## Features
- Upload individual JSON resumes or bulk upload from a folder
- Store resume data in PostgreSQL
- Index cleaned resume data into Elasticsearch
- Search resumes using Elasticsearch queries
- API endpoints for managing and querying data

## Project Structure
```
resume_indexing_app/
│── app/
│   ├── api/
│   │   ├── routes.py       # FastAPI endpoints
│   ├── core/
│   │   ├── config.py       # Configuration settings
│   │   ├── database.py     # PostgreSQL connection and queries
│   │   ├── elastic.py      # Elasticsearch client and indexing logic
│   ├── services/
│   │   ├── resume_service.py  # Business logic for resume processing
│── main.py                 # FastAPI app entry point
│── requirements.txt        # Dependencies
│── README.md               # Documentation
```

## Prerequisites
Before running the project, ensure you have the following installed:
- Python 3.8+
- PostgreSQL
- Elasticsearch
- `pipenv` or `venv` for virtual environments

## Installation & Setup
### 1. Clone the Repository
```sh
git clone https://github.com/your-username/resume_indexing_app.git
cd resume_indexing_app
```

### 2. Create a Virtual Environment and Install Dependencies
```sh
python -m venv venv
source venv/bin/activate   # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Update `app/core/config.py` with your PostgreSQL and Elasticsearch credentials.

### 4. Start the Services
Make sure PostgreSQL and Elasticsearch are running.

### 5. Run the Application
```sh
uvicorn main:app --reload
```

## API Endpoints
### Upload and Store Data
| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/upload-json-files/` | Upload a single JSON file |
| `POST` | `/upload-folder/` | Upload multiple JSON files from a folder |
| `POST` | `/index-data/` | Index resume data from PostgreSQL to Elasticsearch |

### Search and Retrieve Data
| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET` | `/get-all-data/` | Retrieve all indexed resumes |
| `GET` | `/search-elasticsearch/?name=John` | Search resumes by name |
| `GET` | `/check-es-connection/` | Check Elasticsearch connection |

### Delete Data
| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/delete-all-data/?delete_index=False` | Delete all indexed documents (but keep the index) |
| `POST` | `/delete-all-data/?delete_index=True` | Delete the entire Elasticsearch index |

## Contributing
Feel free to open issues or submit pull requests if you find bugs or improvements!

## License
This project is licensed under the MIT License.

---
Happy coding! 🚀

