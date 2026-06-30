from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.courtroom.models.llm import RETRIVER_LITE_MODEL

class WebQueries(BaseModel):
    queries: list[str] = Field(description="List of up to 10 distinct search queries optimized for finding legal news, public reports, and precedents on search engines.")

rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a senior legal research assistant. Your task is to analyze a legal brief request and generate a list of up to 10 distinct search-engine-friendly queries.
    
    The queries should be optimized to find news, legal commentary, case filings, government reports, or public records relevant to the request.
    Generate a diverse set of queries covering different aspects of the request. Output at most 10 queries."""),
    ("user", "Request: {request}")
])

rewrite_chain = rewrite_prompt | RETRIVER_LITE_MODEL.with_structured_output(WebQueries)

def rewrite_query(request: str) -> list[str]:
    """
    Rewrites the request into up to 10 optimized web search queries.
    """
    try:
        result = rewrite_chain.invoke({"request": request})
        # Limit strictly to 10 queries just in case
        return result.queries[:10]
    except Exception as e:
        print(f"Error during query rewriting: {e}")
        # Fallback to the original request as a single query
        return [request]
