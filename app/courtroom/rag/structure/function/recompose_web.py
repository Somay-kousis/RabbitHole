from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.courtroom.models.llm import RETRIEVER_MODEL
from app.courtroom.rag.structure.graph.states import RagState
from langchain_core.documents import Document

recompose_web_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a senior legal researcher preparing a structured legal and factual brief for a courtroom agent using web research.

    You are given a list of web search results. Each result has a specific source tag (e.g., <TimesOfIndia>, <@username_x_post>, <BarAndBench>).
    
    Synthesize these search results into a clean, structured factual and legal summary.
    
    CRITICAL RULES:
    1. Classify each cited source/claim as either [OFFICIAL] or [UNOFFICIAL]:
       - Use [OFFICIAL] if the source is an official government site, official court portal (.gov.in, nic.in), or primary legislative text.
       - Use [UNOFFICIAL] if the source is secondary commentary, news media, blogs, or social media.
    2. Whenever you state a fact, event, or legal point, you MUST cite the source using both the [OFFICIAL]/[UNOFFICIAL] classification AND the exact matching source tag (e.g., "[UNOFFICIAL] <TimesOfIndia>...", "[OFFICIAL] <SupremeCourtOfIndia>...", or "[UNOFFICIAL] <@username_x_post>...").
    3. Group the findings logically by issue or topic.
    4. Do not invent any facts. Only use the details provided in the search results.
    5. Keep the writing professional and legal in tone."""),
    ("user", "Case Request: {request}\n\nWeb Search Results:\n{documents}")
])

recompose_web_chain = recompose_web_prompt | RETRIEVER_MODEL | StrOutputParser()

def recompose_web(search_results: list[dict], state: RagState) -> list:
    """
    Synthesizes the web search results into a clean legal brief, 
    ensuring all facts are cited with their parsed source tags.
    """
    if not search_results:
        # Wrap an empty summary document
        return [Document(page_content="No relevant web search results found.", metadata={"type": "recomposed_web_brief"})]
        
    # Format search results for prompt, including their source tags
    doc_blocks = []
    for item in search_results:
        block = f"Source: {item['source_tag']} (URL: {item['url']})\n"
        block += f"Title: {item['title']}\n"
        block += f"Content:\n{item['content']}"
        doc_blocks.append(block)
        
    documents_text = "\n\n=========================================\n\n".join(doc_blocks)
    
    summary = recompose_web_chain.invoke({
        "request": state["request"],
        "documents": documents_text
    })
    
    final_doc = Document(
        page_content=summary,
        metadata={"type": "recomposed_web_brief", "source_count": len(search_results)}
    )
    
    return [final_doc]
