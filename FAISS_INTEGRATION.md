# FAISS Vector Database Integration

## Overview
The Finance Coach system is designed to support FAISS vector database integration for RAG (Retrieval-Augmented Generation), enabling the Knowledge Agent to search through financial documents, research papers, and educational content.

## Implementation Details

### 1. Dependencies
```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
```

### 2. Knowledge Base Loader
```python
def load_knowledge_base_retriever(openai_api_key: str):
    """Load the Finance knowledge base FAISS vector store as a retriever."""
    embeddings = OpenAIEmbeddings(api_key=openai_api_key)
    
    knowledge_base_path = "./knowledge_base/faiss_index"
    if os.path.exists(knowledge_base_path):
        vector_store = FAISS.load_local(
            knowledge_base_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        return vector_store.as_retriever(search_kwargs={"k": 5})
    else:
        return None
```

### 3. Integration with Finance Q&A Agent
- Finance Q&A Agent includes FAISS retrieval capability
- Tool automatically available when FAISS index exists
- Graceful fallback to web scraping if knowledge base unavailable

## Current Status

### Knowledge Base Directory Structure
```
knowledge_base/
└── faiss_index/
    ├── index.faiss  (to be created)
    └── index.pkl    (to be created)
```

### Creating the Knowledge Base

To create a FAISS knowledge base for financial documents:

```python
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Load documents
loader = DirectoryLoader('./data/finance_docs/', glob="**/*.txt", loader_cls=TextLoader)
documents = loader.load()

# Split documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

# Create embeddings and FAISS index
embeddings = OpenAIEmbeddings(api_key=your_api_key)
vectorstore = FAISS.from_documents(texts, embeddings)

# Save to disk
vectorstore.save_local("./knowledge_base/faiss_index")
```

## Integration Benefits

1. **Faster Retrieval**: Pre-indexed documents enable instant semantic search
2. **Offline Access**: Knowledge base available without API calls
3. **Cost Effective**: Reduces web scraping and API calls
4. **Consistency**: Curated, verified financial information
5. **Custom Content**: Add proprietary research, reports, and analysis

## Future Enhancements

- [ ] Create initial finance knowledge base with:
  - Investment concepts and terminology
  - Tax rules and regulations
  - Portfolio management strategies
  - Market analysis techniques
- [ ] Add automatic knowledge base updates
- [ ] Implement hybrid search (FAISS + web search)
- [ ] Add document management interface
- [ ] Support multiple knowledge bases (stocks, crypto, taxes, etc.)

## Usage Example

Once the knowledge base is created, the Finance Q&A Agent automatically uses it:

```python
query = "What is dollar cost averaging?"
# Agent searches FAISS knowledge base
# Returns relevant chunks from financial education documents
# Synthesizes answer using LLM + retrieved context
```

## Testing

The system handles FAISS gracefully:
- ✅ Continues to work without FAISS (uses web scraping)
- ✅ Loads FAISS when available
- ✅ Proper error handling for missing/corrupt indices
- ✅ Logs knowledge base status at startup

See `tests/test_multi_agent.py` for FAISS integration tests.
