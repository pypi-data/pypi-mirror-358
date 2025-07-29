# rag logic handler
from fastapi import HTTPException
from phoenix_ai.config_param import Param
from phoenix_ai.rag_inference import RAGInferencer
from phoenix_ai.utils import GenAIChatClient, GenAIEmbeddingClient


def get_inferencer(api_key: str, embedding_model: str, chat_model: str):
    embed_client = GenAIEmbeddingClient(
        "openai", model=embedding_model, api_key=api_key
    )
    chat_client = GenAIChatClient("openai", model=chat_model, api_key=api_key)
    return RAGInferencer(embed_client, chat_client)


def summarize_with_config(config, question, mode, top_k):
    try:
        rag = get_inferencer(
            config["api_key"], config["embedding_model"], config["chat_model"]
        )
        df = rag.infer(
            system_prompt=Param.get_rag_prompt(),
            index_path=config["index_path"],
            question=question,
            mode=mode,
            top_k=top_k,
        )
        if "answer" not in df.columns or df.empty:
            raise ValueError("No valid response found in RAG output.")

        return {
            "question": question,
            "answer": df.iloc[-1].get("answer", "No answer generated."),
            "sources": df.to_dict(orient="records"),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"RAG summarization failed: {str(e)}"
        )
