from dotenv import load_dotenv
load_dotenv()

from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent

from ordis_rag.llm import load_llm

# Initialize Tavily Search Tool
tavily_search_tool = TavilySearch(
    max_results=5,
    topic="general",
)
llm = load_llm()
agent = create_react_agent(llm, [tavily_search_tool])

user_input = "Who was the first warframe released in the game warframe"

for step in agent.stream(
    {"messages": user_input},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()