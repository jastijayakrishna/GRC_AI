# Project File Structure

```
ai-auditor/
│
├── app.py                          # Main Streamlit application
├── rag_engine.py                   # ChromaDB integration & RAG logic
├── framework_crosswalk.csv         # 66 risk patterns with control mappings
├── requirements.txt                # Python dependencies
├── run.bat                         # Windows quick launcher
├── .gitignore                      # Git exclusions
│
├── README.md                       # Main documentation
├── PROJECT_SUMMARY.md              # Detailed metrics & portfolio talking points
├── SAMPLE_INPUTS.md                # Test cases for demos
│
└── scripts/                        # Development utilities
    ├── test_patterns.py            # Automated pattern matching tests
    └── reload_database.py          # Force database reload utility
```

## File Descriptions

### Core Application
- **app.py** (315 lines) - Streamlit UI, input handling, LLM orchestration, CSV export
- **rag_engine.py** (191 lines) - ChromaDB setup, semantic search, pattern matching, PDF ingestion
- **framework_crosswalk.csv** (66 patterns) - Risk pattern database with ISO/SOC2/HIPAA/NIST mappings

### Documentation
- **README.md** - Installation, usage, architecture, features
- **PROJECT_SUMMARY.md** - Technical deep-dive, metrics, interview talking points
- **SAMPLE_INPUTS.md** - Ready-to-use test cases with expected results

### Development Tools
- **scripts/test_patterns.py** - Validates pattern matching across 8 scenarios
- **scripts/reload_database.py** - Clears ChromaDB cache and reloads CSV

### Configuration
- **requirements.txt** - 6 Python packages (streamlit, ollama, pandas, chromadb, sentence-transformers, pypdf)
- **.gitignore** - Excludes chroma_db/, logs, cache, temp files
- **run.bat** - Windows launcher (checks Ollama, pulls model, starts Streamlit)

## Generated at Runtime (Git-Ignored)
```
chroma_db/                          # ChromaDB vector database (auto-created)
audit_trail.log                     # Runtime logging (ISO A.12.4 compliant)
__pycache__/                        # Python bytecode cache
temp_*.pdf                          # Uploaded policy PDFs (temporary)
audit_report_*.csv                  # Exported reports (optional ignore)
```

## Total Size
- Source code: ~900 lines
- Documentation: ~500 lines
- Database: 66 patterns × 4 frameworks = 264 control mappings
- Dependencies: 6 packages (~200MB with sentence-transformers)
- LLM: llama3.2 (~2GB via Ollama)
