# Notion Archive

A simple Python library for adding semantic search to Notion HTML exports.

## What is Notion Archive?

Notion Archive parses your exported Notion workspace and adds AI-powered search using embeddings. It's a basic tool that lets you search through your Notion content using natural language instead of just keywords.

## What it does

- Parses Notion HTML exports 
- Generates embeddings using OpenAI or local models
- Stores them in a vector database (ChromaDB)
- Provides basic search functionality
- Extracts some metadata (tags, titles, workspace structure)

## Installation

```bash
pip install notion-archive
```

## How to use it

### 1. Export your Notion workspace
1. In Notion, go to Settings & Members → Settings
2. Click "Export all workspace content"
3. Choose "HTML" format (not Markdown)
4. Download and unzip the file
5. You'll get a folder like `Export-abc123.../`

### 2. Use the library
```python
from notion_archive import NotionArchive

# Initialize with persistent storage
archive = NotionArchive(
    embedding_model="text-embedding-3-large",
    db_path="./my_archive"  # Saves data permanently
)

# Add your export
archive.add_export('./Export-abc123-def456-etc')

# Build index (automatically skips if already exists)
archive.build_index()  # Smart - won't rebuild unnecessarily

# Search (always fast after first build)
results = archive.search("meeting notes")
for result in results:
    print(f"{result['title']}: {result['content'][:100]}...")
```

**To force a rebuild:**
```python
archive.build_index(force_rebuild=True)  # Rebuilds even if index exists
```

## Embedding Models

```python
# OpenAI (requires API key, costs money)
archive = NotionArchive(embedding_model="text-embedding-3-large")
archive = NotionArchive(embedding_model="text-embedding-3-small")

# Local models (free, slower)
archive = NotionArchive(embedding_model="all-MiniLM-L6-v2")
```

## How it works

1. You export your Notion workspace as HTML
2. The parser extracts text and basic metadata 
3. Text gets chunked and turned into embeddings
4. Embeddings are stored in ChromaDB
5. Search queries get embedded and matched against stored chunks

## Limitations

- Only works with HTML exports (not live Notion)
- No incremental updates - you have to rebuild the index
- Basic metadata extraction
- Search quality depends on your embedding model choice
- Large workspaces can be expensive with OpenAI models

## API

```python
# Initialize
archive = NotionArchive(embedding_model="model-name", db_path="./archive_db")

# Add export folder  
archive.add_export("./path/to/export")

# Build search index (smart - skips if exists)
archive.build_index()

# Force rebuild if needed
archive.build_index(force_rebuild=True)

# Check if index exists
if archive.has_index():
    print("Ready to search!")

# Search
results = archive.search("query", limit=10)

# Get info
stats = archive.get_stats()
```

## Requirements

- Python 3.8+
- A Notion workspace exported as HTML
- OpenAI API key if using OpenAI models

## Common issues

**"No documents found"** - Make sure you exported as HTML, not Markdown, and pointed to the unzipped folder.

**"OpenAI API error"** - Set your API key: `export OPENAI_API_KEY=sk-your-key-here`

**"Memory error"** - Large workspaces need lots of RAM. Try using a smaller embedding model or chunking your export.

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

A simple tool for adding semantic search to your Notion exports.