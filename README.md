# ordis-rag

## Objective
To create an AI agent that uses RAG to search websites and API endpoints, store embeddings, and answer Warframe-related questions.

## Environment Variables

To use this project, you need to create a `.env` file in the root directory with the following variables:

- `GOOGLE_API_KEY`: Your Google API key for accessing the Gemini models.
- `LLM_DEFAULT_MODEL`: The default language model to use (e.g., `google_genai:gemini-2.5-flash`).
- `TAVILY_API_KEY`: Your Tavily API key for web search.
