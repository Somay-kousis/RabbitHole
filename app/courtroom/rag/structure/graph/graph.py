from langgraph.graph import END, START, StateGraph 
from app.courtroom.rag.structure.graph.states import RagState
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env", override=True)

from app.courtroom.rag.structure.nodes.level_one_refine_node import level_one_refine_node
from app.courtroom.rag.structure.nodes.retriever_node import retriver_node
from app.courtroom.rag.structure.nodes.docs_quality_node import docs_quality_node
from app.courtroom.rag.structure.nodes.correct_node import correct_node
from app.courtroom.rag.structure.nodes.incorrect_node import incorrect_node
from app.courtroom.rag.structure.nodes.ambigious_node import ambigious_node
from app.courtroom.rag.structure.nodes.supported_node import supported_node
from app.courtroom.rag.structure.nodes.not_supported_node import not_supported_node
from app.courtroom.rag.structure.nodes.partial_supported_node import partial_supported_node

from app.courtroom.rag.structure.graph.route import route_ragornot, route_gooddocs, route_issupported

graph = StateGraph(RagState)
graph.add_node("level_one_refine_node", level_one_refine_node)
graph.add_node("retriver_node", retriver_node)
graph.add_node("docs_quality_node", docs_quality_node)
graph.add_node("correct_node", correct_node)
graph.add_node("incorrect_node", incorrect_node)
graph.add_node("ambigious_node", ambigious_node)
graph.add_node("supported_node", supported_node)
graph.add_node("not_supported_node", not_supported_node)
graph.add_node("partial_supported_node", partial_supported_node)

graph.add_edge(START, "level_one_refine_node")

graph.add_conditional_edges(
    "level_one_refine_node",
    route_ragornot,
    {
        "retriever_node": "retriver_node",
        "placeholder": END
    }
)

graph.add_edge("retriver_node", "docs_quality_node")

graph.add_conditional_edges(
    "docs_quality_node",
    route_gooddocs,
    {
        "correct_node": "correct_node",
        "incorrect_node": "incorrect_node",
        "ambigious_node": "ambigious_node"
    }
)

graph.add_edge("correct_node", "supported_node")

graph.add_conditional_edges(
    "supported_node",
    route_issupported,
    {
        "supported_node": END,
        "not_supported_node": "not_supported_node",
        "partial_supported_node": "partial_supported_node"
    }
)

graph.add_edge("not_supported_node", "correct_node")
graph.add_edge("partial_supported_node", END)
graph.add_edge("incorrect_node", END)
graph.add_edge("ambigious_node", END)