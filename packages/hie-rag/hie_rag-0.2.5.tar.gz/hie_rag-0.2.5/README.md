# 📚 HieRAG – Hierarchical Retrieval-Augmented Generation

`hie_rag` is a modular, extensible Python package designed for **Hierarchical Retrieval-Augmented Generation (Hie-RAG)**. It enables you to extract, split, embed, summarize, and query documents using both chunk- and tree-level semantics, all backed by a vector database.

---

## ✅ Features

- PDF/DOCX/XLSX/CSV/PPT ingestion and intelligent semantic splitting
- Hierarchical summarization tree building
- Embedding-based similarity search
- Vector DB indexing and querying (e.g., Qdrant)
- Full streaming interface for frontend integration

---

## 📦 Components Used

| Module      | Role                                                           |
| ----------- | -------------------------------------------------------------- |
| `HieRAG`    | Main interface for processing, querying, and managing indexes. |
| `Split`     | Split raw text into chunks                                     |
| `Process`   | Adds metadata and embeddings to chunks                         |
| `TreeIndex` | Builds tree-based hierarchical summaries                       |
| `Utils`     | Text extraction and token handling                             |
| `Vectordb`  | Stores and queries summaries/chunks                            |
| `AiClient`  | Handles embedding API (e.g., OpenAI, HuggingFace, Ollama)      |

---

## 🛠 Installation

```bash
pip install hie-rag
```

## ⏯︎ How to Use

### Initialize HieRAG

```python
from hie_rag import HieRag

hierag = HieRag(base_url="http://localhost:11434")
```

> [!NOTE]
> Ensure you have set u an AI server. You should have a chatting model and a embedding model running.

### Process and Index a File

```python
with open("sample.pdf", "rb") as f:
    file_bytes = f.read()

for status in hierag.process_and_save_index_stream(
    file_name="sample.pdf",
    uploaded_file=file_bytes,
    min_chunk_size=300,
    max_chunk_size=500
):
    print(status)
```

> ```JSON
> {
>   "status": "✅ Done",
>   "file_id": "abc123",
>   "summary_count": 5,
>   "chunk_count": 22
> }
> ```

### Query the Summaries or Chunks

#### Query Summaries by text:

```python
results = hierag.query_summaries_by_text("What is the contract duration?")
```

#### Query Chunks by text:

```python
results = hierag.query_chunks_by_text("Explain clause 3.4", file_id="abc123")
```

### List & Manage Indexed Files

#### List All Indexed Files

```python
hierag.list_summaries()
```

#### View Chunks of a File

```python
hierag.list_chunks(file_id="abc123")
```

#### Delete a File Index

```python
hierag.delete_index(file_id="abc123")
```

#### Get the Summary of a File

```python
hierag.get_summary(file_id="abc123")
```
