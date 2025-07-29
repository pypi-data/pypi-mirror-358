# main entry point
from threading import Thread

import nest_asyncio
import uvicorn
from fastapi import Body, FastAPI, HTTPException, Query
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel

from phoenix_ai_services.rag_controller import summarize_with_config
from phoenix_ai_services.registry import EndpointRegistry
from phoenix_ai_services.tool_controller import run_tool

# Enable nested event loop
nest_asyncio.apply()
app = FastAPI(title="Phoenix AI Services - RAG Framework")

# In-memory endpoint registry
registry = EndpointRegistry()


# === Pydantic Schemas ===
class RAGConfig(BaseModel):
    api_key: str
    embedding_model: str
    chat_model: str
    index_path: str


# === Dynamic Endpoint Manager APIs ===
@app.post("/rag/endpoints/{name}")
def add_rag_endpoint(name: str, config: RAGConfig):
    registry.add(name, config.dict())
    return {"message": f"✅ Endpoint '{name}' registered."}


@app.put("/rag/endpoints/{name}")
def update_rag_endpoint(name: str, config: RAGConfig):
    registry.update(name, config.dict())
    return {"message": f"🔁 Endpoint '{name}' updated."}


@app.delete("/rag/endpoints/{name}")
def delete_rag_endpoint(name: str):
    registry.delete(name)
    return {"message": f"❌ Endpoint '{name}' deleted."}


@app.get("/rag/endpoints")
def list_rag_endpoints():
    return registry.list_all()


# === Universal RAG Query Handler ===
@app.get("/rag/query/{name}")
def query_rag_endpoint(
    name: str,
    question: str = Query(...),
    mode: str = Query("standard"),
    top_k: int = Query(5),
):
    config = registry.get(name)
    if not config:
        raise HTTPException(status_code=404, detail=f"Endpoint '{name}' not found.")
    return summarize_with_config(config, question, mode, top_k)


@app.get("/test/run")
def test_run():
    results = {}

    # Test RAG if "default_rag" is registered
    try:
        config = registry.get("default_rag")
        if config and config.get("type") == "rag":
            rag_response = summarize_with_config(
                config=config,
                question="What is the leave policy?",
                mode="standard",
                top_k=3,
            )
            results["RAG_Test"] = rag_response
        else:
            results["RAG_Test"] = "⚠️ 'default_rag' not registered"
    except Exception as e:
        results["RAG_Test"] = f"❌ Failed: {str(e)}"

    # Test tools
    try:
        results["Tool_Calculator"] = run_tool("calculator", "2 + 3 * 4")
        results["Tool_SystemTime"] = run_tool("system_time", "")
        results["Tool_Python"] = run_tool("python", "round(3.14159, 2)")
    except Exception as e:
        results["Tools"] = f"❌ Tool test failed: {str(e)}"

    return results


# === MCP Mount ===
mcp = FastApiMCP(
    app,
    name="Phoenix AI Services",
    description="Dynamic RAG Inference Service with Endpoint Registry",
)
mcp.mount()


# === Launch Server
def run_server():
    print("🚀 Starting Phoenix AI Services at http://localhost:8003")
    uvicorn.run(app, host="0.0.0.0", port=8003)


Thread(target=run_server).start()
