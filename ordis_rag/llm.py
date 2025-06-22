import os
from typing import Optional
from langchain.chat_models import init_chat_model
from langchain.chat_models.base import BaseChatModel

def load_llm(
    model: Optional[str] = None,
    **kwargs
) -> BaseChatModel:
    return init_chat_model(
        model or os.environ['LLM_DEFAULT_MODEL'],
        **kwargs,
    )