from langgraph.graph import END, START, StateGraph

from app.courtroom.graph.route import route_after_hitl
from app.courtroom.graph.state import CourtroomState

from app.courtroom.nodes.conclusion_node import conclusion_node
from app.courtroom.nodes.hitl_node import hitl_node
from app.courtroom.nodes.judiciary_node import judiciary_node
from app.courtroom.nodes.moderator_node import moderator_node
from app.courtroom.nodes.perspective_node import (
    p1_node,
    p2_node,
    p3_node,
    p4_node,
    p5_node,
    p6_node,
    p7_node,
    p8_node,
    p9_node,
    p10_node,
)
from app.courtroom.nodes.query_refine_node import query_refine_node
from app.courtroom.rag.structure.graph.graph import graph as rag_graph

compiled_rag = rag_graph.compile()

def courtroom_rag_node(state: CourtroomState):
    rag_result = compiled_rag.invoke({
        "query": state["user_input"],
        "turn": 0,
        "why_loop": "",
        "is_sup": False,
        "good_retrieval": "yes",
        "retriever_needed": True
    })
    return {
        "final_docs": rag_result.get("final_docs", [])
    }

from dotenv import load_dotenv
load_dotenv(dotenv_path=".env", override=True)

PERSPECTIVE_NODE_NAMES = [
    "p1_node",
    "p2_node",
    "p3_node",
    "p4_node",
    "p5_node",
    "p6_node",
    "p7_node",
    "p8_node",
    "p9_node",
    "p10_node",
]


def route_to_active_perspective_nodes(state: CourtroomState):
    active_ids = [
        perspective["id"]
        for perspective in state.get("perspectives", [])
        if perspective.get("active") is True and 1 <= perspective["id"] <= 10
    ]

    return [f"p{perspective_id}_node" for perspective_id in active_ids]


def build_courtroom_graph():
    graph = StateGraph(CourtroomState)

    graph.add_node("moderator_node", moderator_node)
    graph.add_node("query_refine_node", query_refine_node)
    graph.add_node("rag_node", courtroom_rag_node)
    graph.add_node("p1_node", p1_node)
    graph.add_node("p2_node", p2_node)
    graph.add_node("p3_node", p3_node)
    graph.add_node("p4_node", p4_node)
    graph.add_node("p5_node", p5_node)
    graph.add_node("p6_node", p6_node)
    graph.add_node("p7_node", p7_node)
    graph.add_node("p8_node", p8_node)
    graph.add_node("p9_node", p9_node)
    graph.add_node("p10_node", p10_node)
    graph.add_node("judiciary_node", judiciary_node)
    graph.add_node("hitl_node", hitl_node)
    graph.add_node("conclusion_node", conclusion_node)

    graph.add_edge(START, "query_refine_node")
    graph.add_edge("query_refine_node", "rag_node")
    graph.add_edge("rag_node", "moderator_node")

    graph.add_conditional_edges(
        "moderator_node",
        route_to_active_perspective_nodes,
        PERSPECTIVE_NODE_NAMES,
    )

    for node_name in PERSPECTIVE_NODE_NAMES:
        graph.add_edge(node_name, "judiciary_node")

    graph.add_edge("judiciary_node", "hitl_node")

    graph.add_conditional_edges(
        "hitl_node",
        route_after_hitl
    )

    graph.add_edge("conclusion_node", END)

    return graph


from langgraph.checkpoint.memory import MemorySaver

courtroom_graph = build_courtroom_graph()
courtroom_app = courtroom_graph.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["hitl_node"]
)

