\# Technology Stack



\## AI Document Intelligence \& Question Answering System



This document explains the technologies used in the project, their responsibilities, and how they work together within the application.



\---



\# 1. Technology Overview



| Technology | Category | Role in the Project |

|---|---|---|

| Python | Backend / AI | Core application and ML pipeline |

| FastAPI | Backend | REST API and application layer |

| React | Frontend | User interface |

| TypeScript | Frontend | Type-safe frontend development |

| Vite | Frontend | Frontend development and build tooling |

| PostgreSQL | Database | Application and document metadata storage |

| pgvector | Vector Database | Semantic vector similarity search |

| Docling | Document Intelligence | PDF parsing and structure extraction |

| RapidOCR | OCR | Text extraction from image-based content |

| Ollama | AI Infrastructure | Local model serving |

| Qwen3 Embedding 0.6B | Embedding Model | Document and query embeddings |

| Pydantic | Backend | Data validation and schemas |

| SQLAlchemy | Database | Application database abstraction |

| Psycopg | Database Driver | PostgreSQL connectivity |

| Alembic | Database | Schema migrations |

| RAG | AI Architecture | Retrieval-grounded question answering |

| BGE Reranker | Retrieval | Retrieval result reranking |



\---



\# 2. Python



Python is the primary programming language used throughout the backend and AI pipeline.



It is responsible for:



\- FastAPI backend development

\- Document ingestion

\- Document normalization

\- Chunking

\- Embedding integration

\- Retrieval

\- Prompt construction

\- LLM integration

\- PostgreSQL interaction



The project separates application logic from machine-learning infrastructure using dedicated modules.



```text

Python

&#x20;|

&#x20;+-- Backend

&#x20;|

&#x20;+-- Document Processing

&#x20;|

&#x20;+-- Embeddings

&#x20;|

&#x20;+-- Retrieval

&#x20;|

&#x20;+-- Generation

&#x20;|

&#x20;+-- Storage

