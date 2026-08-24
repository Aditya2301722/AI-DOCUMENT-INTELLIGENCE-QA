\# AI Document Intelligence \& Question Answering System



> A document-grounded AI system for intelligent PDF analysis, semantic search, contextual question answering, and source attribution.



\## Overview



The \*\*AI Document Intelligence \& Question Answering System\*\* is an end-to-end application that allows users to upload PDF documents and ask questions about their content.



The system processes documents through a structured ingestion pipeline, creates retrieval-ready chunks, generates embeddings, stores them in PostgreSQL with pgvector, retrieves relevant information for user questions, and generates grounded answers with source attribution.



The application combines document intelligence, semantic retrieval, vector search, conversational context, and large language model generation.



\---



\## Key Features



\- PDF document upload

\- Structured PDF parsing with Docling

\- OCR processing with RapidOCR

\- Text, heading, table, and picture extraction

\- Canonical document representation

\- Structure-aware document chunking

\- Retrieval-specific text generation

\- Local embedding generation with Ollama

\- Qwen3 Embedding 0.6B

\- PostgreSQL with pgvector

\- Semantic vector retrieval

\- Session-scoped document retrieval

\- Document replacement

\- Context-grounded question answering

\- Source attribution

\- FastAPI backend

\- React + TypeScript frontend



\---



\## How It Works



The application follows an end-to-end document question-answering workflow:



```text

PDF

&#x20;↓

Document Parsing

&#x20;↓

OCR / Structure Extraction

&#x20;↓

Canonical Document

&#x20;↓

Structure-Aware Chunking

&#x20;↓

Embedding Generation

&#x20;↓

PostgreSQL + pgvector

&#x20;↓

Semantic Retrieval

&#x20;↓

Context Processing

&#x20;↓

LLM Generation

&#x20;↓

Grounded Answer + Sources

