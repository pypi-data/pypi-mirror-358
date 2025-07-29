
# 🔥 Phoenix AI Services is MCP server

Unified agentic framework to run dynamic RAG APIs and utility tools like calculator, date, and   python evaluator.

# phoenix_ai_services

[![PyPI - Version](https://img.shields.io/pypi/v/phoenix-ai-services.svg)](https://pypi.org/project/phoenix-ai-services/)
[![Code Style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python Version](https://img.shields.io/pypi/pyversions/phoenix-ai-services.svg)](https://pypi.org/project/phoenix-ai-services/)
[![License](https://img.shields.io/pypi/l/phoenix-ai-services)](https://github.com/Praveengovianalytics/phoenix_ai_services/LICENSE)

---

> `phoenix_ai_services` is a modular Python package for managing RAG endpoints, tool-based APIs, and plug-and-play AI utilities using FastAPI & Poetry. It supports RESTful control for registering, updating, and deleting endpoints for RAG, tools, and more.


## 🔧 Setup

```bash
poetry install
poetry run python phoenix_ai_services/main.py
```

## 🚀 API Endpoints

### RAG
- `POST /rag/endpoints/{name}` – Register RAG
- `PUT /rag/endpoints/{name}` – Update RAG
- `DELETE /rag/endpoints/{name}` – Remove RAG
- `GET /rag/query/{name}` – Ask RAG agent

### Tools
- `GET /tool/calculator?input_data=2+3*4`
- `GET /tool/system_time`
- `GET /tool/python?input_data=round(3.14159, 2)`

### Admin
- `GET /registry` – View all registered endpoints

## 🧠 Powered by Phoenix Agentic AI Framework
