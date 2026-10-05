import json
import logging
from typing import Dict, Any, List, Optional, TypedDict
from app.agent.tools import (
    search_schemes,
    search_knowledge_base,
    search_web_for_government_schemes,
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
    intent: str
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
        """Build LangGraph flow with strict intent detection and tool routing"""
        try:
            from langgraph.graph import StateGraph, END
            
            builder = StateGraph(AgentState)

            # Node 1: Intent Analysis & Tool Selection
            def analyze_and_route(state: AgentState):
                q = state["query"].lower().strip()
                tools = []
                intent = "INFORMATIONAL"
                
                # 1. Checklist request
                if "checklist" in q:
                    intent = "CHECKLIST"
                    tools = ["create_document_checklist"]
                # 2. Document request
                elif "what document" in q or "documents do i need" in q or "proofs needed" in q:
                    intent = "DOCUMENTS_ONLY"
                    tools = ["get_required_documents", "search_knowledge_base"]
                # 3. Comparison request
                elif "compare" in q or " vs " in q or "versus" in q or "difference between" in q:
                    intent = "COMPARISON"
                    tools = ["compare_schemes", "search_knowledge_base"]
                # 4. Latest / Current news
                elif "latest" in q or "update" in q or "current" in q or "recent" in q or "2026" in q:
                    intent = "LATEST_NEWS"
                    tools = ["search_web_for_government_schemes"]
                # 5. Personalized eligibility
                elif any(k in q for k in ["student", "income", "from ", "my family", "i am", "for me"]):
                    intent = "PERSONALIZED"
                    tools = ["search_schemes", "check_eligibility", "search_knowledge_base"]
                # 6. Default informational query ("What is PM-KISAN?")
                else:
                    intent = "INFORMATIONAL"
                    tools = ["search_knowledge_base", "get_scheme_details"]

                return {
                    "intent": intent,
                    "tool_calls": list(set(tools))
                }

            # Node 2: Execute Tools
            def execute_tools(state: AgentState):
                query = state["query"]
                intent = state.get("intent", "INFORMATIONAL")
                tools_to_run = state.get("tool_calls", [])
                retrieved = {}
                sources = []
                scheme_ids = []

                # Execute RAG Tool
                if "search_knowledge_base" in tools_to_run:
                    rag_res = search_knowledge_base(query, top_k=5)
                    retrieved["rag_result"] = rag_res
                    sources.extend(rag_res.get("sources", []))

                # Execute Web Search Tool
                if "search_web_for_government_schemes" in tools_to_run:
                    web_res = search_web_for_government_schemes(query, max_results=5)
                    retrieved["web_result"] = web_res

                # Execute Scheme Search Tool
                if "search_schemes" in tools_to_run:
                    schemes = search_schemes(query)
                    retrieved["schemes"] = schemes
                    for s in schemes[:3]:
                        scheme_ids.append(s["id"])

                # Execute Comparison Tool
                if "compare_schemes" in tools_to_run:
                    # Try to match schemes in query
                    table_res = compare_schemes([query])
                    retrieved["comparison"] = table_res

                # Execute Checklist Tool
                if "create_document_checklist" in tools_to_run:
                    chk_res = create_document_checklist(query)
                    retrieved["checklist"] = chk_res

                # Execute Documents Tool
                if "get_required_documents" in tools_to_run:
                    docs_res = get_required_documents(query)
                    retrieved["required_documents"] = docs_res

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
                intent = state.get("intent", "INFORMATIONAL")
                retrieved = state.get("retrieved_data", {})
                user_context = state.get("user_context")
                
                # Context chunks pass to LLM service
                context_chunks = []
                if "rag_result" in retrieved and retrieved["rag_result"].get("sources"):
                    for s in retrieved["rag_result"].get("sources", []):
                        context_chunks.append({
                            "payload": {
                                "scheme_name": s.get("scheme_name"),
                                "document_name": s.get("document_name"),
                                "source_url": s.get("source_url"),
                                "category": s.get("category"),
                                "text": s.get("snippet")
                            }
                        })
                
                if "web_result" in retrieved:
                    for w in retrieved["web_result"]:
                        context_chunks.append({
                            "payload": {
                                "scheme_name": w.get("title"),
                                "document_name": "Official Government Portal" if w.get("is_official") else "Third-Party Reference",
                                "source_url": w.get("link"),
                                "category": "Live Online Search",
                                "text": w.get("snippet")
                            }
                        })

                system_prompt = (
                    "You are SchemeSathi AI. Synthesize clean, grounded, user-facing markdown responses.\n"
                    "RULES:\n"
                    "1. Never output debug logs, tool calls, internal json, top-k chunks, or reasoning.\n"
                    "2. Ground information only in official government sources when available.\n"
                    "3. For comparison queries, output a full Markdown table with columns: Feature | Scheme A | Scheme B.\n"
                    "4. Never say 'You are eligible.' Say 'Based on the information provided, this scheme appears potentially relevant...'\n"
                    "5. Final eligibility must be verified on official government portals."
                )

                answer = llm_service.generate_formatted_response(
                    query=query,
                    intent=intent,
                    retrieved_data=retrieved,
                    context_chunks=context_chunks,
                    user_context=user_context
                )
                
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
        No chain-of-thought or internal tool trace is exposed in user answer.
        """
        if self._graph is not None:
            try:
                initial_state: AgentState = {
                    "query": query,
                    "intent": "",
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

        # Native fallback execution if graph compile fails
        q = query.lower()
        if "compare" in q or " vs " in q:
            intent = "COMPARISON"
            tools_used = ["compare_schemes", "search_knowledge_base"]
        elif "checklist" in q:
            intent = "CHECKLIST"
            tools_used = ["create_document_checklist"]
        elif "latest" in q or "update" in q:
            intent = "LATEST_NEWS"
            tools_used = ["search_web_for_government_schemes"]
        elif any(k in q for k in ["student", "income", "from ", "i am"]):
            intent = "PERSONALIZED"
            tools_used = ["search_schemes", "check_eligibility", "search_knowledge_base"]
        else:
            intent = "INFORMATIONAL"
            tools_used = ["search_knowledge_base", "get_scheme_details"]

        rag_res = search_knowledge_base(query, top_k=5)
        schemes = search_schemes(query)
        scheme_ids = [s["id"] for s in schemes[:3]]
        
        answer = llm_service.generate_formatted_response(
            query=query,
            intent=intent,
            retrieved_data={"rag_result": rag_res, "schemes": schemes},
            context_chunks=[],
            user_context=user_context
        )

        return {
            "answer": answer,
            "sources": rag_res.get("sources", []),
            "scheme_ids": scheme_ids,
            "tools_used": tools_used
        }

agent_executor = SchemeSathiAgent()
