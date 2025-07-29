from agno.document.chunking.agentic import AgenticChunking
from agno.embedder.openai import OpenAIEmbedder
from agno.models.deepseek import DeepSeek
from agno.vectordb.lancedb import LanceDb
from agno.knowledge.agent import AgentKnowledge
import importlib.resources
import os


embedder_id = os.getenv("EMBEDDER_MODEL")
embedder_api_key = os.getenv("EMBEDDER_API_KEY")
embedder_base_url = os.getenv("EMBEDDER_BASE_URL")
model_id = os.getenv("MODEL")
model_api_key = os.getenv("API_KEY")
model_base_url = os.getenv("BASE_URL")


def load_kb(software=None):
    vector_db = LanceDb(
        table_name=software,
        uri=importlib.resources.path("scmcp_shared", "vector_db"),
        embedder=OpenAIEmbedder(
            id=embedder_id,
            base_url=embedder_base_url,
            api_key=embedder_api_key,
        ),
    )
    model = DeepSeek(
        id=model_id,
        base_url=model_base_url,
        api_key=model_api_key,
    )
    knowledge_base = AgentKnowledge(
        chunking_strategy=AgenticChunking(model=model),
        vector_db=vector_db,
    )

    return knowledge_base
