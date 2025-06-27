from typing import Annotated, List, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langchain_core.documents import Document

class OrdisState(TypedDict):
    question: str
    web_question: str
    resources: List[str]
    documents: List[Document]
    answer: str
    supplement: bool

    @classmethod
    def new(cls, question: str):
        return OrdisState(
            question=question,
            web_question='',
            documents=[],
            resources=[], 
            answer='', 
            supplement=False
        )