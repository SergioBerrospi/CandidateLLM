# AIPE LLM Project

## Overview

AIPE LLM is an end-to-end application designed to build, test, and deploy Large Language Model (LLM) solutions for political analysis and content understanding.  
The project follows a modular architecture that separates data ingestion, retrieval, model management, and API serving into independent but interoperable components.  

The current version represents the MVP stage, which implements a retrieval-based question-answering system.  
The system retrieves the most relevant text segments given a query, using text embeddings and similarity search.

---

## Architecture

aipe_llm/
├── aipe_api/           # FastAPI application serving endpoints
│   ├── main.py
│   └── routers/
├── aipe_retriever/     # Core retriever logic for text similarity
│   ├── retriever.py
│   └── utils.py
├── aipe_data/          # (Planned) data ingestion and preprocessing pipelines
├── aipe_model/         # (Planned) model fine-tuning and LLM management
├── notebooks/          # Experimental notebooks for exploration
├── tests/              # Unit tests for components
├── infra/              # Infrastructure and orchestration
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
└── README.md

---

## MVP Workflow

1. The user sends a question to the FastAPI endpoint (/ask).
2. The retriever module loads precomputed document embeddings.
3. Cosine similarity is computed between the query embedding and stored chunks.
4. The API returns the text chunk(s) with the highest similarity score.

This MVP focuses on retrieval; future iterations will integrate an LLM for generation using the retrieved context.

---

## Installation

### 1. Clone the repository
git clone https://github.com/yourusername/aipe_llm.git
cd aipe_llm

### 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

---

## Running Locally

### Using FastAPI directly

uvicorn aipe_api.main:app --reload

Access the API at: http://localhost:8000/docs

### Example Request

curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "What are the main political proposals of candidate X?"}'

Example Response:
{
  "query": "What are the main political proposals of candidate X?",
  "retrieved_text": "Candidate X focuses on education reform and economic transparency..."
}

---

## Running with Docker

The repository includes Docker support for reproducibility.

### 1. Build the image
docker-compose build

### 2. Start the services
docker-compose up

This launches the FastAPI app (and Redis if configured).  
The API will be available at http://localhost:8000.

---

## Testing

To run the unit tests:

pytest -v

Tests are organized under the tests/ directory and include retriever and API integration tests.

---

## Development Workflow

- Version Control: GitHub is used for code versioning and collaboration.
- Continuous Integration: GitHub Actions (to be added) for automated testing and linting.
- Branching Strategy:  
  - main → stable production code  
  - dev → integration branch  
  - feature branches → per feature/task

---

## Planned Modules and Next Steps

| Module | Description | Status |
|---------|--------------|--------|
| aipe_data | Data ingestion, cleaning, and transformation pipeline | Planned |
| aipe_model | LLM integration (retrieval-augmented generation, fine-tuning) | Planned |
| aipe_retriever | Text embedding and retrieval module | MVP Complete |
| aipe_api | FastAPI serving layer for REST API | MVP Complete |
| infra | Docker, orchestration, and deployment setup | MVP Complete |

### Upcoming Milestones

1. Integrate LLM generation (RAG: Retrieval-Augmented Generation).
2. Add persistent vector store (e.g., Redis, Pinecone, or FAISS).
3. Add MLflow tracking for experiments.
4. Include logging and monitoring via Prometheus/Grafana.
5. Deploy to AWS ECS or EKS using CI/CD pipelines.

---

## Tech Stack

| Layer | Technology |
|--------|-------------|
| API | FastAPI |
| Backend | Python 3.10+ |
| Retrieval | SentenceTransformers / OpenAI embeddings |
| Orchestration | Docker / Docker Compose |
| Caching / Storage | Redis (planned) |
| Deployment | AWS ECS / ECR (planned) |
| Version Control | GitHub |
| CI/CD | GitHub Actions |

---

## Contributing

1. Fork the repository.
2. Create a feature branch:  
   git checkout -b feature/your-feature-name
3. Commit and push your changes.
4. Open a Pull Request to dev.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Maintainer

Developed and maintained by the AIPE Engineering Team.  
For inquiries or collaboration, contact the project maintainer.
