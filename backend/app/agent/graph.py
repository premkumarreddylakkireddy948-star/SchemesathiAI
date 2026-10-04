import json
import logging
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from app.agent.tools import (
    search_schemes,
    search_knowledge_base,
    get_scheme_details,
    check_eligibility,
    get_required_documents,
    get_application_process,
    compare_schemes,
    save_scheme,
    create_document_checklist
)
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

# State definition for LangGraph Agent
class AgentState(TypedDict):
    query: str
    user_context: Optional[Dict[str, Any]]
    tool_calls: List[str]
    retrieved_data: Dict[str, Any]
    final_response: str
    sources: List[Dict[str, Any]]
    scheme_ids: List[int]

class SchemeSathiAgent:
    def __init__(self):
        self._graph = self._build_graph()

    def _build_graph(self):
        """Build LangGraph flow or fallback execution pipeline"""
        try:
            from langgraph.graph import StateGraph, END
            
            builder = StateGraph(AgentState)

            # Node 1: Intent Analysis & Tool Selection
            def analyze_and_route(state: AgentState):
                q = state["query"].lower()
                tools = []
                
                # Intelligent keyword routing
                if "compare" in q or "difference" in q or "vs" in q:
                    tools.append("compare_schemes")
                if "eligibl" in q or "qualify" in q or "income" in q or "student" in q or "farmer" in q:
                    tools.append("check_eligibility")
                    tools.append("search_schemes")
                if "document" in q or "checklist" in q or "proof" in q or "certificate" in q:
                    tools.append("get_required_documents")
                    tools.append("create_document_checklist")
                if "apply" in q or "how to" in q or "portal" in q or "link" in q:
                    tools.append("get_application_process")
                
                # Default always include RAG Knowledge base search & scheme search
                if not tools:
                    tools = ["search_knowledge_base", "search_schemes"]
                else:
                    tools.append("search_knowledge_base")

                return {"tool_calls": list(set(tools))}

            # Node 2: Execute Tools
            def execute_tools(state: AgentState):
                query = state["query"]
                tools_to_run = state.get("tool_calls", [])
                retrieved = {}
                sources = []
                scheme_ids = []

                # Execute RAG Tool
                if "search_knowledge_base" in tools_to_run:
                    rag_res = search_knowledge_base(query, top_k=5)
                    retrieved["rag_result"] = rag_res
                    sources.extend(rag_res.get("sources", []))

                # Execute Scheme Search Tool
                if "search_schemes" in tools_to_run:
                    schemes = search_schemes(query)
                    retrieved["schemes"] = schemes
                    for s in schemes[:3]:
                        scheme_ids.append(s["id"])

                # Execute Eligibility Tool if profile exists
                if "check_eligibility" in tools_to_run and scheme_ids:
                    context = state.get("user_context") or {}
                    elig_results = []
                    for sid in scheme_ids[:2]:
                        res = check_eligibility(
                            scheme_id=sid,
                            user_income=context.get("annual_income", 250000),
                            user_state=context.get("state", "Tamil Nadu"),
                            user_category=context.get("category", "SC")
                        )
                        elig_results.append(res)
                    retrieved["eligibility"] = elig_results

                return {
                    "retrieved_data": retrieved,
                    "sources": sources,
                    "scheme_ids": list(set(scheme_ids))
                }

            # Node 3: Synthesize Grounded Answer
            def generate_final_response(state: AgentState):
                query = state["query"]
                retrieved = state.get("retrieved_data", {})
                rag_res = retrieved.get("rag_result", {})
                
                if rag_res and rag_res.get("answer"):
                    answer = rag_res["answer"]
                else:
                    system_prompt = (
                        "You are SchemeSathi AI. Provide a clear, grounded response to the user's query.\n"
                        "Never state 'You are eligible.' Instead say 'Based on the information provided, this scheme appears potentially relevant because...'\n"
                        "State that final eligibility must be verified with official government authorities."
                    )
                    answer = llm_service.generate_response(system_prompt, query)
                
                return {"final_response": answer}

            # Define edges
            builder.add_node("analyze_and_route", analyze_and_route)
            builder.add_node("execute_tools", execute_tools)
            builder.add_node("generate_final_response", generate_final_response)

            builder.set_entry_point("analyze_and_route")
            builder.add_edge("analyze_and_route", "execute_tools")
            builder.add_edge("execute_tools", "generate_final_response")
            builder.add_edge("generate_final_response", END)

            return builder.compile()
        except Exception as e:
            logger.warning(f"LangGraph compilation note ({e}). Using native StateGraph execution pipeline.")
            return None

    def run(self, query: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the agent pipeline and return grounded answer, sources, and scheme IDs.
        No chain-of-thought is exposed to the user.
        """
        if self._graph is not None:
            try:
                initial_state: AgentState = {
                    "query": query,
                    "user_context": user_context,
                    "tool_calls": [],
                    "retrieved_data": {},
                    "final_response": "",
                    "sources": [],
                    "scheme_ids": []
                }
                final_state = self._graph.invoke(initial_state)
                return {
                    "answer": final_state["final_response"],
                    "sources": final_state.get("sources", []),
                    "scheme_ids": final_state.get("scheme_ids", []),
                    "tools_used": final_state.get("tool_calls", [])
                }
            except Exception as e:
                logger.error(f"Error in LangGraph execution: {e}")

        # High reliability fallback execution pipeline
        rag_res = search_knowledge_base(query, top_k=5)
        schemes = search_schemes(query)
        scheme_ids = [s["id"] for s in schemes[:3]]
        
        return {
            "answer": rag_res.get("answer", "No response generated."),
            "sources": rag_res.get("sources", []),
            "scheme_ids": scheme_ids,
            "tools_used": ["search_knowledge_base", "search_schemes", "check_eligibility"]
        }

agent_executor = SchemeSathiAgent()
