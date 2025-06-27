from typing import Literal
import bs4
from langgraph.graph import START, END
from langgraph.graph.state import StateGraph
from langgraph.types import Command
from langchain_tavily import TavilySearch
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader

from ordis_rag.llm import load_llm
from ordis_rag.model.grade import Grade
from ordis_rag.model.resources import Resources
from ordis_rag.prompts import load_prompts
from ordis_rag.resource.stats.stats import Stats
from ordis_rag.state import OrdisState
from ordis_rag.vector_store import load_vector_store
from ordis_rag.wiki.wiki_loader import WikiLoader

class Ordis(StateGraph):
    @classmethod
    def init_state(cls, question: str) -> OrdisState:
        return OrdisState.new(question)

    def __init__(self):
        super().__init__(OrdisState)
        self.llm = load_llm()
        self.vector_store = load_vector_store('ordis')
        self.prompts = load_prompts()
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    def retriever(self, state: OrdisState) -> OrdisState:
        state['documents'] = self.vector_store.similarity_search(state['question'])
        return state
    
    def resource_retriever(self, state: OrdisState) -> OrdisState:
        all_resources = '\n'.join(Stats.all_resources().values())
        template = PromptTemplate.from_template(self.prompts["resource_retriever/template"])
        resources: Resources = self.llm\
            .with_structured_output(Resources)\
            .invoke([
                SystemMessage(self.prompts["resource_retriever/system"]),
                HumanMessage(
                    template.invoke({
                        'question': state['question'],
                        'resources': all_resources
                    }).text
                )
            ])

        state['resources'] = resources.uniqueNames

        return state

    def wiki_retriever(self, state: OrdisState) -> OrdisState:
        urls = []
        for resource in state['resources']:
            print(resource)
            if resource in Stats.all():
                url = Stats.all()[resource].wikiaUrl
                print(url)
                if url is not None:
                    urls.append(url)

        loader = WikiLoader(
            web_paths=urls,
        )

        state['documents'] = loader.load()

        return state
    
    def grade_documents(self, state: OrdisState) -> Command[Literal['generate', 'transform_query']]:
        documents = state['documents']
        state['documents'] = []

        template = PromptTemplate.from_template(self.prompts["grade_documents/template"])

        if len(documents) == 0:
            state['supplement'] = True

        for document in documents:
            grade: Grade = self.llm\
                .with_structured_output(Grade)\
                .invoke([
                    SystemMessage(self.prompts["grade_documents/system"]),
                    HumanMessage(
                        template.invoke({
                            'question':state['question'], 
                            'document':document
                        }).text
                    )
                ])
            
            if grade.relevant:
                state['documents'].append(document)
            else:
                state['supplement'] = True

        if state['supplement']:
            return Command(
                update=state,
                goto='transform_query'
            )
        else:
            return Command(
                update=state,
                goto='generate'
            )
        
    def transform_query(self, state: OrdisState) -> OrdisState:
        template = PromptTemplate.from_template(self.prompts["transform_query/template"])

        state['web_question'] = self.llm\
            .invoke([
                SystemMessage(self.prompts["transform_query/system"]),
                HumanMessage(template.invoke({'question': state['question']}).text)
            ])\
            .content

        return state
    
    def websearch(self, state: OrdisState) -> OrdisState:
        tavily_search_tool = TavilySearch(
            max_results=5,
            topic="general",
        )
        docs = tavily_search_tool.invoke({"query": state['web_question']})
        web_results = "\n".join([d["content"] for d in docs['results']])
        web_results = Document(page_content=web_results)
        all_splits = self.text_splitter.split_documents([web_results])

        # Index chunks
        _ = self.vector_store.add_documents(documents=all_splits)
        state['documents'].append(web_results)

        return state
        
    def generate(self, state: OrdisState) -> OrdisState:
        template = PromptTemplate.from_template(self.prompts["generate/template"])
        chain = create_stuff_documents_chain(self.llm, template)

        state['answer'] = self.llm\
            .invoke([
                SystemMessage(self.prompts["generate/system"]),
                HumanMessage(chain.invoke({'context': state['documents'], 'question': state['question']}))
            ])\
            .content

        return state

    def validate_generation(self, state: OrdisState) -> Command[Literal['transform_query', '__end__']]:
        template = PromptTemplate.from_template(self.prompts["validate/template"])

        grade: Grade = self.llm\
                .with_structured_output(Grade)\
                .invoke([
                    SystemMessage(self.prompts["validate/system"]),
                    HumanMessage(
                        template.invoke({
                            'question':state['question'], 
                            'answer':state['answer']
                        }).text
                    )
                ])
        
        if not grade.relevant:
            return Command(
                update={
                    'supplement': True,
                    'answer': ''
                },
                goto='transform_query'
            )
        else:
            return Command(
                goto=END
            )

    def compile(self, checkpointer = None, *, cache = None, store = None, interrupt_before = None, interrupt_after = None, debug = False, name = None):
        # self.add_node('retriever', self.retriever)

        self.add_node('resource_retriever', self.resource_retriever)
        self.add_node('wiki_retriever', self.wiki_retriever)
        self.add_node('grade_documents', self.grade_documents)
        self.add_node('transform_query', self.transform_query)
        self.add_node('websearch', self.websearch)
        self.add_node('generate', self.generate)
        self.add_node('validate', self.validate_generation)

        self.add_edge(START, 'resource_retriever')
        self.add_edge('resource_retriever', 'wiki_retriever')
        # self.add_edge('wiki_retriever', 'grade_documents')
        self.add_edge('wiki_retriever', 'generate')
        self.add_edge('transform_query', 'websearch')
        self.add_edge('websearch', 'generate')
        self.add_edge('generate', END)
        # self.add_edge('generate', 'validate')

        return super().compile(checkpointer, cache=cache, store=store, interrupt_before=interrupt_before, interrupt_after=interrupt_after, debug=debug, name=name)
